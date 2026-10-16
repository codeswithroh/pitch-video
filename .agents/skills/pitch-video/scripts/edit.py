"""Step 3: build the edit decision list (timeline.json) from captions.json + project.json.

- Trims pauses (keeps breaths natural, scene breaks a beat longer), cutting only on the 30 fps grid.
- Applies the global speed-up (default 1.1x, pitch preserved later by atempo).
- Resolves scenes/shots that are anchored to spoken phrases, so visuals change exactly on the words.
All output times are EDITED seconds (after trims and speed-up), snapped to frames.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import load, save, snap, FPS

P = load("project.json")
# Rules memory: lasting preferences from past notes override project defaults (project.json still wins if it sets a key).
try:
    import rules as _rules
    for _k, _v in _rules.apply().items():
        if _k not in P:
            P[_k] = _v
            print(f"rule applied: {_k} = {_v}")
        elif isinstance(_v, dict) and isinstance(P[_k], dict):
            P[_k] = {**_v, **P[_k]}
except Exception as _e:
    print("rules skipped:", _e)
caps = load("captions.json")
# Pacing. "reel" (default for the split layout) follows measured top-performing reels: no dead air, natural
# beats of 0.2-0.4 s between phrases, speech in the first frames, and NO speed-up (tightness comes from the
# gaps, never from talking faster). "classic" is the original pitch-video pacing: 1.1x and roomier pauses.
PACE = P.get("pace", "reel" if P.get("layout") == "split" else "classic")
if PACE == "reel":
    SPEED = float(P.get("speed", 1.0))
    PZ = {"scene": 0.4, "long": 0.25, "short_max": 0.4, "head": 0.1, "tail": 2.0, **P.get("pause", {})}
else:
    SPEED = float(P.get("speed", 1.1))
    PZ = {"scene": 1.0, "long": 0.6, "short_max": 0.8, "head": 0.25, "tail": 2.5, **P.get("pause", {})}

norm = lambda s: re.sub(r"[^a-z0-9 ]", "", re.sub(r"<[^>]+>", "", s.lower().replace("-", " ")))

def find(phrase, after=-1):
    for i, c in enumerate(caps):
        if i > after and norm(phrase) in norm(c["text"]):
            return i
    # The phrase may straddle two caption lines (whisper chunks don't follow sentences): cut at the line it starts in.
    for i in range(max(after + 1, 0), len(caps) - 1):
        a = norm(caps[i]["text"])
        k = (a + " " + norm(caps[i + 1]["text"])).find(norm(phrase))
        if k != -1:
            return i if k < len(a) else i + 1
    lines = "\n".join(f"  [{i}] {c['text']}" for i, c in enumerate(caps))
    sys.exit(f"phrase not found (after line {after}): {phrase!r}\ncaption lines:\n{lines}")

# ── Scene/shot anchors (caption indices) ──
scene_at, shot_at = [], []
last = -1
for si, sc in enumerate(P["scenes"]):
    i = 0 if si == 0 else find(sc["start"], last - 1 if last >= 0 else -1)
    scene_at.append(i)
    last = i
    for k, sh in enumerate(sc["shots"]):
        j = i if k == 0 else find(sh["from"], last - 1)
        shot_at.append((si, k, j))
        last = j
scene_starts = set(scene_at[1:])
holds = [(norm(h["after"]), h["keep"]) for h in P.get("holds", [])]

# ── Keep intervals (source seconds, frame-snapped) ──
START = snap(max(0, caps[0]["start"] - PZ["head"]))
END = snap(caps[-1]["end"] + PZ["tail"])
keep, cur = [], START
# Cut only inside REAL silence. Caption line edges are ASR estimates and can sit inside a word ("posts" lost its
# "-ts" when a tight gap was trimmed between line edges); the silence detector's spans are measured on the audio.
SIL = [tuple(x) for x in load("sil.json", [])]


def real_gap(a, b):
    best = None
    for s0, s1 in SIL:
        ov = min(s1, b + 0.15) - max(s0, a - 0.15)
        if ov > 0 and (best is None or ov > best[0]):
            best = (ov, s0, s1)
    return (best[1], best[2]) if best else None


try:
    import numpy as _np
    from common import pcm as _pcm
    VOICE16 = _pcm("voice16k.wav", 16000)
    _E = _np.sqrt(_np.convolve(VOICE16 ** 2, _np.ones(160) / 160, "same"))[::160]
except Exception:
    VOICE16 = None


def quietest(lo, hi, default):
    if VOICE16 is None or hi - lo < 0.02:
        return default
    i0, i1 = int(lo * 100), int(hi * 100)
    seg = _E[i0:i1 + 1]
    return (i0 + int(_np.argmin(seg))) / 100 if len(seg) else default


for i in range(len(caps) - 1):
    a, b = caps[i]["end"], caps[i + 1]["start"]
    if SIL:
        rg = real_gap(a, b)
        if rg is None:
            continue                                     # speech runs straight on: no cut here
        a, b = rg
    g = b - a
    if g <= 0:
        continue
    hold = next((v for k, v in holds if k in norm(caps[i]["text"])), None)
    if hold is not None:
        t = hold
    elif i + 1 in scene_starts or g >= 1.8:
        t = PZ["scene"]
    elif g > PZ["short_max"]:
        t = PZ["long"]
    else:
        t = g
    if t < g - 1 / FPS:
        ca, cb = a + t / 2, b - t / 2
        if VOICE16 is not None:
            # land each cut on the quietest 10 ms near it, after the word's decay and before the next onset
            ca = quietest(max(a + 0.05, ca - 0.08), min(ca + 0.08, cb - 0.02), ca)
            cb = quietest(max(cb - 0.08, ca + 0.02), min(cb + 0.08, b - 0.03), cb)
        ca, cb = snap(ca), snap(cb)
        if ca > cur:
            keep.append([cur, ca])
        cur = cb
keep.append([cur, END])
keep = [k for k in keep if k[1] - k[0] >= 1 / FPS]

def m(t):
    """source → edited seconds (before speed-up)."""
    out = 0.0
    for a, b in keep:
        if t <= a:
            return out
        if t <= b:
            return out + (t - a)
        out += b - a
    return out

E = lambda t: snap(m(t) / SPEED)
TOTAL = E(END)

def boundary(i):
    """Edited time of the cut before caption i: middle of the (trimmed) pause."""
    if i == 0:
        return 0.0
    return snap((E(caps[i - 1]["end"]) + E(caps[i]["start"])) / 2)

# ── Scenes ──
scenes = []
for si, sc in enumerate(P["scenes"]):
    s = boundary(scene_at[si])
    e = boundary(scene_at[si + 1]) if si + 1 < len(scene_at) else TOTAL
    scenes.append({"n": f"{si + 1:02d}", "title": sc["title"], "start": s, "end": e, "chip": sc.get("chip", si not in (0, len(P["scenes"]) - 1)),
                   "end_card": bool(sc.get("end_card"))})

# ── Shots ──
plan = []
for idx, (si, k, j) in enumerate(shot_at):
    s = boundary(j) if k else scenes[si]["start"]
    nxt = shot_at[idx + 1] if idx + 1 < len(shot_at) else None
    e = (boundary(nxt[2]) if nxt[1] else scenes[nxt[0]]["start"]) if nxt else TOTAL
    sh = {key: v for key, v in P["scenes"][si]["shots"][k].items() if key != "from"}
    if "rec" in sh:
        fa = float(sh.pop("t"))
        fb = sh.pop("to", None)
        sh["fit"] = [fa, float(fb) if fb is not None else fa + (e - s)]
    if scenes[si]["end_card"]:
        sh["end_card"] = True
    plan.append({"start": s, "end": e, "scene": si, **sh})
for p in plan:
    if p["end"] - p["start"] < 0.3:
        sys.exit(f"shot too short ({p['end'] - p['start']:.2f}s): {p}")

# ── Captions (edited time) ──
ecaps = []
for i, c in enumerate(caps):
    s, e = E(c["start"]), E(c["end"]) + 0.12
    if i + 1 < len(caps):
        e = min(e, E(caps[i + 1]["start"]))
    ec = {"start": s, "end": round(e, 3), "html": c.get("html", c["text"]), "src": [c["start"], c["end"]]}
    if c.get("words"):
        ec["words"] = [{"text": w["text"], "start": E(w["start"]), "end": E(w["end"]), "b": w.get("b", False)} for w in c["words"]]
    ecaps.append(ec)


# ── Caption chunks: 1-3 words, split at phrase boundaries, shown 2 frames before the first word and
# hard-swapped on the next chunk (no pop animation). Emphasis colours the whole chunk.
LEAD = {"a", "an", "the", "to", "for", "of", "in", "into", "on", "and", "or", "but", "with", "your", "my", "at", "from", "by", "it's", "is"}


def chunk_line(words, maxw):
    out, cur = [], []
    for k, w in enumerate(words):
        cur.append(w)
        nxt = words[k + 1] if k + 1 < len(words) else None
        brk = re.search(r"[.,!?;:]$", w["text"]) or len(cur) >= maxw
        if nxt and not brk and len(cur) >= 2 and nxt["start"] - w["end"] > 0.18:
            brk = True                                   # a real pause is a phrase boundary
        if nxt and nxt.get("b") != w.get("b"):
            brk = True                                   # emphasis starts/ends: its own chunk, so colour stays on the key words
        if brk or nxt is None:
            carry = []
            # never end a chunk on a word that leads into the next one ("for a" | "hackathon")
            while nxt and len(cur) > 1 and nxt.get("b") == cur[-1].get("b") and not re.search(r"[.,!?;:]$", cur[-1]["text"]) and re.sub(r"[^a-z']", "", cur[-1]["text"].lower()) in LEAD:
                carry.insert(0, cur.pop())
            out.append(cur)
            cur = carry
    if (len(out) > 1 and len(out[-1]) == 1 and len(out[-2]) < maxw and not re.search(r"[.!?]$", out[-2][-1]["text"])
            and out[-2][-1].get("b") == out[-1][0].get("b")):
        last = out.pop()                                 # no orphan single word at the end of a line
        out[-1] = out[-1] + last
    return out


CAPCFG = {"mode": "words" if P.get("layout") == "split" else "lines", "max_words": 3, **(P.get("captions") or {})}
chunks = []
if CAPCFG["mode"] == "words" and all(c.get("words") for c in ecaps):
    for li, c in enumerate(ecaps):
        for g in chunk_line(c["words"], CAPCFG["max_words"]):
            txt = " ".join(w["text"] for w in g)
            chunks.append({"start": max(0.0, g[0]["start"] - 2 / FPS), "last": g[-1]["end"], "line": li,
                           "html": f"<b>{txt}</b>" if any(w["b"] for w in g) else txt})
    for k, ch in enumerate(chunks):
        nxt = chunks[k + 1]["start"] if k + 1 < len(chunks) else TOTAL
        # hard swap inside a phrase run; after the last word of a line, hold briefly, never over the next line
        ch["end"] = round(nxt if nxt - ch["last"] < 0.6 else min(nxt, ch["last"] + 0.3), 3)
        ch["start"] = round(ch["start"], 3)
        del ch["last"]
elif CAPCFG["mode"] == "words":
    print("captions: no word timing in captions.json (run words.py), falling back to whole lines")

# ── Cold open: cinematic shots before the first spoken word. Everything spoken shifts later by INTRO;
# cut_speaker.py pads the speaker track with the same silence, so sync checks still compare like with like.
INTRO = 0.0
intro = []
for k, sh in enumerate((P.get("intro") or {}).get("shots", [])):
    d = snap(float(sh.get("len", 3.5)))
    intro.append({"start": INTRO, "end": snap(INTRO + d), "scene": -1, "intro": True, "pip": False,
                  **{key: v for key, v in sh.items() if key != "len"}})
    INTRO = snap(INTRO + d)
if INTRO:
    for x in scenes + plan + ecaps + [w for c in ecaps for w in c.get("words", [])]:
        x["start"], x["end"] = snap(x["start"] + INTRO), snap(x["end"] + INTRO)
    plan = intro + plan
    TOTAL = snap(TOTAL + INTRO)

if INTRO:
    for ch in chunks:
        ch["start"], ch["end"] = snap(ch["start"] + INTRO), snap(ch["end"] + INTRO)
save("timeline.json", {"speed": SPEED, "pace": PACE, "total": TOTAL, "intro": INTRO, "keep": keep, "scenes": scenes,
                       "caps": ecaps, "chunks": chunks, "captions": CAPCFG, "plan": plan})
print(f"source {END - START:.1f}s → edited {m(END):.1f}s → {SPEED}x = {TOTAL:.2f}s  ({len(keep)} kept pieces)"
      + (f", incl. a {INTRO:.2f}s cold open" if INTRO else ""))
for s in scenes:
    print(f"  {s['n']} {s['title']:<22} {s['start']:6.2f} → {s['end']:6.2f}")
for p in plan:
    print(f"      {p['start']:6.2f}-{p['end']:6.2f}  " + ", ".join(f"{k}={v}" for k, v in p.items() if k not in ("start", "end", "scene")))
