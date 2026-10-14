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
for i in range(len(caps) - 1):
    a, b = caps[i]["end"], caps[i + 1]["start"]
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
        ca, cb = snap(a + t / 2), snap(b - t / 2)
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
    ecaps.append({"start": s, "end": round(e, 3), "html": c.get("html", c["text"]), "src": [c["start"], c["end"]]})

save("timeline.json", {"speed": SPEED, "total": TOTAL, "keep": keep, "scenes": scenes, "caps": ecaps, "plan": plan})
print(f"source {END - START:.1f}s → edited {m(END):.1f}s → {SPEED}x = {TOTAL:.2f}s  ({len(keep)} kept pieces)")
for s in scenes:
    print(f"  {s['n']} {s['title']:<22} {s['start']:6.2f} → {s['end']:6.2f}")
for p in plan:
    print(f"      {p['start']:6.2f}-{p['end']:6.2f}  " + ", ".join(f"{k}={v}" for k, v in p.items() if k not in ("start", "end", "scene")))
