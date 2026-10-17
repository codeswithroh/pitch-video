"""Check a recording setup BEFORE the real take: record 5-10 seconds of talking, then run this on it.

usage: python check_take.py <test clip>

Measures what makes a take look janky or out of sync, and says how to fix each one:
  frame rate   the REAL rate from frame timestamps (webcams drop to ~10 fps in dim light while the file still says 30)
  freezes      gaps between frames longer than 0.1 s
  light        brightness of the face (dim faces are what make the camera slow down)
  framing      face size and headroom (split layout puts you on the bottom half: centred, head and shoulders)
  sound        speech level and room noise
  sync         mouth vs voice offset (only meaningful if you talk in the clip)
Exit 0 = good to record the real take; 1 = fix the listed things and test again.
"""
import json, subprocess, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import TB, pcm, probe, lip_lag

if len(sys.argv) < 2:
    sys.exit(__doc__)
f = sys.argv[1]
bad, ok = [], []
info = probe(f)
v = next(s for s in info["streams"] if s["codec_type"] == "video")
a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

# real frame rate and freezes, from presentation timestamps
pts = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=pts_time", "-of", "csv=p=0", f],
                     capture_output=True, text=True).stdout.split()
t = np.array(sorted(float(x.strip(",")) for x in pts if x.strip(",") not in ("", "N/A")))
dt = np.diff(t)
fps = (len(t) - 1) / (t[-1] - t[0]) if len(t) > 2 else 0
freezes = int((dt > 0.1).sum())
print(f"frame rate: {fps:.1f} fps real (file says {v.get('r_frame_rate')}), {freezes} freezes > 0.1 s, longest {dt.max() if len(dt) else 0:.2f} s")
if fps < 27 or freezes > 2:
    bad.append("choppy video: the camera isn't delivering 30 fps. Put a lamp or window IN FRONT of you (not behind), "
               "close heavy apps, or record on your phone / iPhone as Continuity Camera. Then test again.")
else:
    ok.append("smooth 30 fps")

# face light, size and headroom (MediaPipe face detector via the landmarker on a few frames)
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=os.path.join(TB, "face_landmarker.task")), running_mode=vision.RunningMode.IMAGE))
W, H = int(v["width"]), int(v["height"])
dur = float(info["format"]["duration"])
lum, size, top, cx = [], [], [], []
for s in np.linspace(0.5, max(0.6, dur - 0.5), 8):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{s:.2f}", "-i", f, "-frames:v", "1", "-vf", "scale=640:-2,format=rgb24",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    h = len(raw) // (640 * 3)
    if h == 0:
        continue
    img = np.frombuffer(raw, np.uint8)[: 640 * h * 3].reshape(h, 640, 3)
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(img)))
    if not r.face_landmarks:
        continue
    p = np.array([[q.x, q.y] for q in r.face_landmarks[0]])
    x0, y0 = (p.min(0) * [640, h]).astype(int)
    x1, y1 = (p.max(0) * [640, h]).astype(int)
    lum.append(img[max(0, y0):y1, max(0, x0):x1].mean() / 255)
    size.append((y1 - y0) / h)
    top.append(y0 / h)
    cx.append((x0 + x1) / 2 / 640)
if not lum:
    bad.append("no face found: face the camera, with light on your face")
else:
    L, S, T, C = np.median(lum), np.median(size), np.median(top), np.median(cx)
    print(f"face: brightness {100 * L:.0f}%, height {100 * S:.0f}% of frame, top of head at {100 * T:.0f}%, centre at {100 * C:.0f}%")
    if L < 0.38:
        bad.append(f"face too dark ({100 * L:.0f}%): this is also what makes webcams drop frames. Light in front of you, at eye level.")
    else:
        ok.append("face well lit")
    if S > 0.62:
        bad.append("too close: move back so your head and shoulders fit with space above your head")
    elif S < 0.22:
        bad.append("too far: move closer, your face is small in the frame")
    if T < 0.06:
        bad.append("head touches the top edge: lower the camera's tilt or sit lower; leave a little space above your hair")
    if abs(C - 0.5) > 0.15:
        bad.append("off-centre: sit in the middle of the frame")

# sound
if a is None:
    bad.append("no audio track")
else:
    x = pcm(f, 16000)
    fr = np.sqrt((x[: len(x) // 400 * 400].reshape(-1, 400) ** 2).mean(1)) + 1e-9
    db = 20 * np.log10(fr)
    speech, noise = np.percentile(db, 90), np.percentile(db, 10)
    print(f"sound: speech {speech:.0f} dBFS, room noise {noise:.0f} dBFS ({speech - noise:.0f} dB apart)")
    if speech < -32:
        bad.append("voice too quiet: get the mic closer (earbuds or a phone near you work)")
    if speech - noise < 20:
        bad.append("noisy room: turn off fans/AC, close the window, or use earbuds' mic")

# sync clap (on by default: prep uses it to line up picture and voice exactly)
try:
    from common import find_clap
    c = find_clap(f)
    if c:
        print(f"sync clap: found at {c[1]:.2f}s (sound {1000 * (c[0] - c[1]):+.0f} ms from the hands meeting; prep will correct it)")
        ok.append("sync clap found")
    else:
        bad.append("no sync clap: clap once, hands in frame, right after you hit record (it syncs your voice to your lips exactly)")
except Exception:
    pass

# sync (only if they talked)
try:
    lag, r, _ = lip_lag(f, 0, None)
    if r >= 0.2:
        print(f"sync: voice vs lips {lag:+d} ms (prep.py corrects up to ±500 ms automatically)")
except Exception:
    pass

print()
for o in ok:
    print("  ok   ", o)
for b in bad:
    print("  FIX  ", b)
print("\nREADY: record the real take" if not bad else "\nNOT READY: fix the items above and record another 5 s test")
sys.exit(1 if bad else 0)
