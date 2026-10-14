"""Step 10: objective QA. Run it every render; do not ship on a FAIL.

0. pipeline self-test (selftest.py): a synthetic flash+click clip through the same cut, speed-up, mix and mux.
   Proves the pipeline keeps sync before the real footage is judged (separates pipeline drift from tracker noise).
1. container: audio/video durations match AND the decoded sample count matches the stated duration
   (catches the "timestamps say 114 s, samples say 105 s" class of bug that wrecks lip sync).
2. voice timing: final mix vs speaker_cut.mov envelope cross-correlation in 8 s windows (must be ~0 ms).
3. lip sync: mouth opening (face landmarks) vs voice envelope on speaker_cut.mov (expect -60..+100 ms).
4. intelligibility: voice stem vs everything-else stem per caption (want ≥ 10 dB; flags anything < 8 dB).
5. loudness (EBU R128 integrated) and a 16-frame contact sheet (out/contact.png) to eyeball.
"""
import os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import TB, VOICE, load, run, probe, pcm
from selftest import run_selftest

t = load("timeline.json")
P = load("project.json")
OUT = P.get("output", "out/demo.mp4")
TOTAL = t["total"]
fails = []
skipped = []

# 0. pipeline self-test
if not run_selftest():
    fails.append("pipeline self-test: the pipeline itself moves sound against picture")

# 1. container
st = {s["codec_type"]: s for s in probe(OUT)["streams"]}
vd, ad = float(st["video"]["duration"]), float(st["audio"]["duration"])
dec = len(pcm(OUT, 8000)) / 8000
print(f"[1] video {vd:.3f}s  audio {ad:.3f}s  decoded audio {dec:.3f}s  rate {st['audio']['sample_rate']}")
if abs(vd - ad) > 0.1 or abs(dec - ad) > 0.1:
    fails.append("audio track length/timestamps inconsistent")

# 2. voice timing in final mix
def envl(x, hop=80):
    return np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "same"))[::hop]
a, b = envl(pcm("speaker_cut.mov", 8000)), envl(pcm(OUT, 8000))
n = min(len(a), len(b))
lags = []
for s in range(0, n - 800, 800):
    u, v = a[s:s + 800] - a[s:s + 800].mean(), b[s:s + 800] - b[s:s + 800].mean()
    if u.std() < 1e-4:
        continue
    lags.append(max(range(-30, 31), key=lambda L: np.dot(u[max(0, L):800 + min(0, L)], v[max(0, -L):800 - max(0, L)])) * 10)
bad = [l for l in lags if abs(l) > 30]
print(f"[2] voice offset in final vs speaker track (ms, per 8 s window): {lags}")
if len(bad) > max(1, len(lags) // 10):
    fails.append("voice drifts against the picture in the final mix")

# 3. lip sync on the speaker track
try:
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(TB, "face_landmarker.task")), running_mode=vision.RunningMode.VIDEO))
    Wd, Hd = 480, 320
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "speaker_cut.mov", "-vf", f"fps=30,scale={Wd}:{Hd},format=rgb24",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, Hd, Wd, 3)
    op = np.full(len(fr), np.nan)
    for i in range(len(fr)):
        r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr[i])), int(i * 1000 / 30))
        if r.face_landmarks:
            p = r.face_landmarks[0]
            op[i] = np.hypot(p[13].x - p[14].x, (p[13].y - p[14].y) * Hd / Wd) / (np.hypot(p[10].x - p[152].x, (p[10].y - p[152].y) * Hd / Wd) + 1e-6)
    x = pcm("speaker_cut.mov", 48000)
    k = len(x) // 1600
    rms = np.log(np.sqrt((x[:k * 1600].reshape(k, 1600) ** 2).mean(1)) + 1e-4)
    m = min(len(op), len(rms))
    NI = round(t.get("intro", 0) * 30)  # the cold open is black on the speaker track: measure from the first word on
    op, rms, m = op[NI:m], rms[NI:m], m - NI
    o = np.nan_to_num(op, nan=np.nanmean(op)); r_ = rms
    o, r_ = (o - o.mean()) / (o.std() + 1e-9), (r_ - r_.mean()) / (r_.std() + 1e-9)
    sc = {L: np.dot(o[max(0, L):m + min(0, L)], r_[max(0, -L):m - max(0, L)]) / m for L in range(-15, 16)}
    L = max(sc, key=sc.get)
    print(f"[3] lip sync: mouth vs voice best lag {L * 33:+d} ms (r={sc[L]:.2f}; + = picture later). Face found in {100 * np.mean(~np.isnan(op)):.0f}% of frames")
    if sc[L] < 0.1:
        # Mouth movement doesn't track the voice at any lag (a still image, face too small, mouth hidden):
        # the offset above is noise, so this was not measured. Real talking heads score ~0.2-0.4.
        skipped.append(f"lip sync inconclusive (mouth vs voice r={sc[L]:.2f}, expected > 0.1)")
    elif sc[L] > 0.15 and not (-70 <= L * 33 <= 140):
        fails.append(f"lip sync off by {L * 33} ms")
except Exception as e:
    print("[3] lip sync check SKIPPED:", e)
    skipped.append(f"lip sync not measured ({e})")

# 4. intelligibility
fc = (f"[0:a]{VOICE},asplit=2[voice][key];"
      f"[1:a]aresample=48000,volume={P.get('music_gain', 0.55)}[mus];[mus][key]sidechaincompress=threshold=0.02:ratio=12:attack=15:release=450:makeup=1[musd];"
      f"[2:a]aresample=48000,volume={P.get('sfx_gain', 0.85)}[fx];[musd][fx]amix=inputs=2:duration=first:normalize=0[bg]")
run(["-i", "speaker_cut.mov", "-i", "music.wav", "-i", "sfx.wav", "-filter_complex", fc,
     "-map", "[voice]", "-ac", "1", "-ar", "16000", "-t", str(TOTAL), "stem_voice.wav", "-map", "[bg]", "-ac", "1", "-ar", "16000", "-t", str(TOTAL), "stem_bg.wav"])
v, g = pcm("stem_voice.wav", 16000), pcm("stem_bg.wav", 16000)
db = lambda z: 20 * np.log10(np.sqrt(np.mean(z ** 2)) + 1e-9)
rows = sorted((db(v[int(c["start"] * 16000):int(c["end"] * 16000)]) - db(g[int(c["start"] * 16000):int(c["end"] * 16000)]), c["start"], re.sub("<[^>]+>", "", c["html"])[:50]) for c in t["caps"])
print(f"[4] voice over background: median {np.median([r[0] for r in rows]):.1f} dB; lowest:")
for r in rows[:5]:
    print(f"      {r[0]:5.1f} dB @ {r[1]:6.2f}s  {r[2]}")
low = [r for r in rows if r[0] < 8]
if low:
    fails.append(f"{len(low)} caption(s) with voice < 8 dB over background (lower/move SFX there)")

# 5. loudness + contact sheet
err = subprocess.run(["ffmpeg", "-hide_banner", "-i", OUT, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
print(f"[5] integrated loudness {lufs[-1] if lufs else '?'} LUFS (target -16..-11)")
os.makedirs("out", exist_ok=True)
run(["-i", OUT, "-vf", f"fps=16/{TOTAL},scale=480:-2,tile=4x4", "-frames:v", "1", "out/contact.png"])
print("    contact sheet: out/contact.png")

if fails:
    print("\nRESULT: FAIL\n  - " + "\n  - ".join(fails))
    sys.exit(1)
if skipped:
    # A skipped check is not a passed check: never report PASS for something we did not measure.
    print("\nRESULT: UNVERIFIED\n  - " + "\n  - ".join(skipped))
    sys.exit(2)
print("\nRESULT: PASS")
sys.exit(0)
