"""Step 8: synthesize the cinematic sound-effects track (sfx.wav) and the music bed (music.wav), 48 kHz stereo.

Automatic cues: whoosh on scene changes, riser→boom on the first cut away from the speaker (the hook),
pop+thud when a card appears, riser→sub-boom on title statements, boom+shimmer AFTER the last spoken word.
Custom cues come from project.json "sfx" (see SKILL.md). Heavy sounds that overlap speech are automatically
low-passed and lowered so they never mask words (a lesson learned the hard way).
"""
import json, os, sys, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import load, run, FPS

SR = 48000
rng = np.random.default_rng(7)
t = load("timeline.json")
P = load("project.json")
TOTAL = t["total"]
plan, caps, scenes = t["plan"], t["caps"], t["scenes"]

def T(d): return np.arange(int(SR * d)) / SR
def env(x, a=0.005, r=None):
    e = np.ones(len(x)); k = max(1, int(a * SR)); e[:k] = np.linspace(0, 1, k)
    if r:
        k2 = max(1, int(r * SR)); e[-k2:] *= np.linspace(1, 0, k2)
    return x * e
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from itertools import accumulate
    # one-pole IIR via cumulative trick (fast enough for short sounds)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y
def hp(x, fc): return x - lp(x, fc)
def noise(d): return rng.uniform(-1, 1, int(SR * d))

# ── sound library (mono) ──
def boom(d=2.2, f0=58, depth=1.0):
    x = T(d)
    tone = np.sin(2 * np.pi * (f0 - 26 * np.minimum(x, 1)) * x) * np.exp(-2.6 * x)
    sub = np.sin(2 * np.pi * 34 * x) * np.exp(-1.6 * x) * 0.6
    crack = lp(noise(d), 900) * np.exp(-14 * x) * 1.4
    return env((tone + sub + crack) * depth, 0.002, 0.3)
def subboom(): return lp(boom(2.6, 48, 1.2), 220)
def riser(d=1.5):
    x = T(d)
    return env((np.sin(2 * np.pi * (160 * x + 420 * x ** 2)) * 0.35 + hp(noise(d), 1500) * 0.35) * (x / d) ** 2.2, 0.01, 0.02)
def whoosh(d=0.75):
    x = T(d); return lp(hp(noise(d), 400), 3000) * np.sin(np.pi * np.minimum(x / d, 1)) ** 2 * 0.9
def swing():
    x = T(0.16); return hp(noise(0.16), 2200) * np.sin(np.pi * x / 0.16) * 0.5
def hit(big=False):
    d = 0.5 if big else 0.32; x = T(d)
    out = np.sin(2 * np.pi * (150 - 60 * x) * x) * np.exp(-22 * x) * 0.9 + lp(noise(d), 2500) * np.exp(-45 * x) * 0.8
    if big: out = out + 0.6 * boom(d, 70, 0.6)[: len(out)]
    return env(out, 0.001, 0.05)
def bighit(): return hit(True)
def chime(notes=(880, 1320, 1760), gap=0.08, d=1.3, amp=0.28):
    x = T(d); out = np.zeros_like(x)
    for k, f in enumerate(notes):
        m = x >= k * gap; xs = x[m] - k * gap
        out[m] += amp * (np.sin(2 * np.pi * f * xs) + 0.3 * np.sin(4 * np.pi * f * xs)) * np.exp(-4.5 * xs)
    return env(out, 0.002, 0.2)
def ding(): return chime((988, 1319), 0.07, 0.8, 0.18)
def fanfare(): return chime((523, 659, 784, 1047), 0.09, 1.6, 0.22)
def coin(): return chime((1047, 1319, 1568, 2093), 0.06, 1.4, 0.2)
def blink():
    x = T(0.45); f = 1700 * np.exp(-5 * x) + 260
    return env(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-5 * x) * 0.35 + chime((2093, 2637), 0.05, 0.45, 0.08), 0.002, 0.08)
def step():
    x = T(0.09); return lp(noise(0.09), 350) * np.exp(-40 * x) * 1.6
def glitch(d=0.9):
    x = T(d)
    f = 320 + 480 * np.sign(np.sin(2 * np.pi * 11 * x)) + 200 * np.sin(2 * np.pi * 37 * x)
    sq = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.16 * (np.sin(2 * np.pi * 23 * x) > -0.2)
    return env(sq * np.exp(-1.4 * x) + hp(noise(d), 4000) * 0.06 * np.exp(-3 * x), 0.003, 0.1)
def denied():
    x = T(0.32); f = np.where(x < 0.11, 560, 370)
    return env(lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.17 * (x < 0.29), 3000), 0.002, 0.03)
def success():
    return chime((659, 988), 0.09, 0.9, 0.2)
def lock():
    x = T(0.45)
    return env(np.sin(2 * np.pi * 95 * x) * np.exp(-18 * x) * 0.9 + lp(noise(0.45), 1800) * np.exp(-55 * x) * 0.7
               + np.sin(2 * np.pi * 2600 * x) * np.exp(-90 * x) * 0.25, 0.001, 0.05)
def pop():
    x = T(0.22); return env(np.sin(2 * np.pi * (620 * x + 1400 * x ** 2)) * np.exp(-13 * x) * 0.32, 0.002, 0.03)
def click():
    x = T(0.05); return hp(noise(0.05), 3000) * np.exp(-120 * x) * 0.5
def ticks(d=1.8, every=0.09):
    x = T(d); return np.sin(2 * np.pi * 2300 * x) * np.exp(-140 * np.mod(x, every)) * 0.09 * np.exp(-0.4 * x)
def typing(d=1.5):
    out = np.zeros(int(SR * d))
    for s in np.cumsum(rng.uniform(0.06, 0.16, 40)):
        i = int(s * SR)
        if i < len(out) - 2400: out[i:i + 2400] += click()[:2400] * rng.uniform(0.5, 1)
    return out
def swell(d=2.2):
    x = T(d); pad = sum(np.sin(2 * np.pi * f * x) for f in (523.25, 659.25, 783.99, 1046.5)) * 0.07
    return env(pad * np.sin(np.pi * np.minimum(x / d, 1)), 0.01, 0.2)
def tap():
    """Damped soft tap: a logo or card landing (the soft palette's main contact sound)."""
    x = T(0.18)
    return env(np.sin(2 * np.pi * 180 * x) * np.exp(-34 * x) * 0.55 + lp(noise(0.18), 1200) * np.exp(-60 * x) * 0.35, 0.001, 0.04)
def air(d=0.5):
    """Soft air move: a real spatial change, much gentler than whoosh."""
    x = T(d); return lp(hp(noise(d), 600), 2200) * np.sin(np.pi * np.minimum(x / d, 1)) ** 3 * 0.35
def warm():
    """One short warm tone: a check or a payoff."""
    return chime((523.25, 783.99), 0.05, 0.7, 0.14)
def sting():
    x = T(1.6)
    return env(np.sin(2 * np.pi * 46 * x) * np.exp(-2.2 * x) * 0.8 + (np.sin(2 * np.pi * 233 * x) + np.sin(2 * np.pi * 247 * x)) * 0.12 * np.exp(-2 * x)
               + lp(noise(1.6), 600) * 0.3 * np.exp(-9 * x), 0.002, 0.3)

LIB = {k: v for k, v in globals().items() if callable(v) and k not in ("T", "env", "lp", "hp", "noise", "load", "run")}
HEAVY = {"boom", "subboom", "riser", "sting", "bighit", "glitch"}

# ── placement ──
L = np.zeros(int(SR * (TOTAL + 1))); R = np.zeros_like(L)
speech = [(c["start"], c["end"]) for c in caps]
def place(at, name, gain=1.0, pan=0.0):
    snd = LIB[name]()
    i = int(at * SR)
    if i < 0 or i >= len(L): return
    if name in HEAVY and any(s < at + len(snd) / SR * 0.5 and e > at for s, e in speech):
        snd, gain = lp(snd, 250), gain * 0.7  # keep it under the voice
    snd = snd[: len(L) - i] * gain
    gl, gr = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    L[i:i + len(snd)] += snd * gl * 1.41; R[i:i + len(snd)] += snd * gr * 1.41

def cap_with(text):
    import re
    n = lambda s: re.sub(r"[^a-z0-9 ]", "", re.sub(r"<[^>]+>", "", s.lower()))
    c = next((c for c in caps if n(text) in n(c["html"])), None)
    if c is None: sys.exit(f"sfx phrase not found: {text!r}")
    return c

def rec_to_edit(rec, ts):
    for p in plan:
        if p.get("rec") == rec and p["fit"][0] - 0.01 <= ts <= p["fit"][1] + 0.01:
            fa, fb = p["fit"]; return p["start"] + (ts - fa) * (p["end"] - p["start"]) / (fb - fa)
    sys.exit(f"sfx: rec {rec!r} time {ts} is not inside any shot's fit range")

A = P.get("sfx_auto", {})
# Sound palette. "soft" (default for the reel pace) follows the house-reel lesson that trailer booms, risers and a
# whoosh on every cut sound cheap: sound follows VISIBLE actions only (a soft air move on a real layout change,
# a damped tap when a card or the end card lands, a warm tone on a payoff) and many cuts stay silent.
SOFT = P.get("sound", "soft" if t.get("pace") == "reel" else "cinematic") == "soft"
if SOFT:
    A = {"whoosh": False, "hook": False, "title": False, "card": False, "end": False, "intro": False, **A}
INTRO = t.get("intro", 0)
if INTRO and A.get("intro", True):
    place(max(0, INTRO - 1.8), "swell", 0.5)
    place(INTRO - 0.05, "subboom", 0.7)
for p in plan:
    for nm in (p.get("sfx") or []) if p.get("cine") else []:   # foley per cinematic shot, e.g. ["typing"]
        place(p["start"] + 0.3, nm, 0.5)
if A.get("whoosh", True):
    for s in scenes[1:]: place(s["start"] - 0.35, "whoosh", 0.45, -0.3)
if A.get("hook", True):
    talk = [p for p in plan if not p.get("intro")]
    first = next((p for p in talk if not p.get("speaker")), None)
    if first and talk and talk[0].get("speaker"):
        place(first["start"] - 1.5, "riser", 0.55); place(first["start"], "boom", 0.75)
for p in plan:
    if p.get("title") and A.get("title", True):
        place(p["start"] - 1.4, "riser", 0.6); place(p["start"] - 0.08, "subboom", 0.75)
    if p.get("card") and A.get("card", True):
        d = p.get("card_delay", 0.4); place(p["start"] + d, "pop", 0.8); place(p["start"] + d + 0.5, "hit", 0.7)
if A.get("end", True) and any(p.get("end_card") for p in plan):
    end_hit = caps[-1]["end"] + 0.1  # strictly after the last word
    place(end_hit, "boom", 0.85); place(end_hit + 0.1, "swell", 1.0)

if SOFT:
    prev = None
    for p in plan:
        kind = "speaker" if p.get("speaker") else "visual"
        if prev is not None and kind != prev and p["start"] > 0.5:
            place(p["start"] - 0.12, "air", 0.35)                    # a real layout change: speaker <-> visual
        prev = kind
        if p.get("title") or p.get("card"):
            place(p["start"] + (p.get("card_delay", 0.4) if p.get("card") else 0.05), "tap", 0.6)
    if any(p.get("end_card") for p in plan):
        place(caps[-1]["end"] + 0.1, "tap", 0.7); place(caps[-1]["end"] + 0.15, "warm", 0.6)

for c in P.get("sfx", []):
    if "phrase" in c:
        cc = cap_with(c["phrase"]); at = cc["end"] if c.get("edge") == "end" else cc["start"]
    elif "rec" in c:
        at = rec_to_edit(c["rec"], c["t"])
    elif "anim" in c:
        at = next(p for p in plan if p.get("anim") == c["anim"])["start"] + c["t"] / 1.0
    else:
        at = c["at"]
    at += c.get("offset", 0)
    for k in range(c.get("repeat", 1)):
        place(at + k * c.get("every", 0.35), c["sound"], c.get("gain", 0.7), c.get("pan", 0))

# Duck the whole SFX bed under every spoken line (-9 dB, 80 ms ramps) so effects punctuate pauses, not words.
duck = np.ones_like(L)
rmp = int(0.08 * SR)
for s_, e_ in speech:
    a_, b_ = int(s_ * SR), int(e_ * SR)
    duck[max(0, a_ - rmp):b_ + rmp] = np.minimum(duck[max(0, a_ - rmp):b_ + rmp], 0.35)
duck = np.convolve(duck, np.ones(rmp) / rmp, "same")
L, R = L * duck, R * duck
pk = max(np.abs(L).max(), np.abs(R).max(), 1e-9)
if pk > 0.95: L, R = L / pk * 0.95, R / pk * 0.95
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L, R], 1) * 32767).astype(np.int16).tobytes())
print(f"sfx.wav {TOTAL:.1f}s peak {pk:.2f}; sounds: {', '.join(sorted(LIB))}")

# ── music bed ──
M = P.get("music", "synth")
MDELAY = f"adelay={int(INTRO * 1000)}:all=1,atrim=0:{TOTAL + 1},afade=t=in:st={INTRO}:d=2," if INTRO else ""  # the cold open plays without music
if M == "none":
    run(["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-t", str(TOTAL + 1), "-c:a", "pcm_s16le", "music.wav"])
elif M == "synth":
    # Slow Am–F–C–G pad, 8 s per chord. Neutral, never fights the voice; ducked under speech in compose.
    chords = [(110, 220, 261.63, 329.63), (87.31, 174.61, 220, 261.63), (130.81, 196, 261.63, 329.63), (98, 196, 246.94, 293.66)]
    v = lambda k: "if(lt(mod(t,32),8),{},if(lt(mod(t,32),16),{},if(lt(mod(t,32),24),{},{})))".format(*[c[k] for c in chords])
    e = "min(1,mod(t,8)*1.5)*min(1,(8-mod(t,8))*1.5)"
    expr = "(" + "+".join(f"{a}*sin(2*PI*{v(k)}*t)" for k, a in enumerate([0.32, 0.22, 0.18, 0.14])) + f")*{e}*(0.85+0.15*sin(2*PI*0.18*t))"
    run(["-f", "lavfi", "-i", f"aevalsrc='{expr}':s={SR}:d={TOTAL + 1}", "-af",
         f"{MDELAY}lowpass=f=1400,aecho=0.8:0.7:220|420:0.35|0.22,volume=0.22,afade=t=in:d=3,afade=t=out:st={TOTAL - 4}:d=4",
         "-ac", "2", "-c:a", "pcm_s16le", "music.wav"])
else:  # a user-supplied track: loop/trim, normalize low, fade
    run(["-stream_loop", "-1", "-i", M, "-t", str(TOTAL + 1), "-af",
         f"aresample={SR},loudnorm=I=-30:TP=-6,{MDELAY}afade=t=in:d=2,afade=t=out:st={TOTAL - 4}:d=4", "-ac", "2", "-c:a", "pcm_s16le", "music.wav"])
# Bed level: about 12 dB under the voice before ducking (house range 9-14 dB). The voice chain normalizes to
# -14 LUFS, so measure the bed and write the gain compose/verify will use, unless the project pins music_gain.
if M != "none" and "music_gain" not in P:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", "music.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    import re as _re
    found = _re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    if found and float(found[-1]) > -70:
        g = round(min(1.5, max(0.05, 10 ** ((-14 - P.get("bed_under_voice_db", 12) - float(found[-1])) / 20))), 3)
        json.dump({"music_gain": g}, open("mix.json", "w"))
        print(f"music bed {float(found[-1]):.1f} LUFS → gain {g} (≈{P.get('bed_under_voice_db', 12)} dB under the voice)")
print("music.wav", M)
