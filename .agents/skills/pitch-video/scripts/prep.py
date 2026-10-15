"""Step 1: normalize the talking-head recording, find speech, transcribe it, locate the face.

usage: python prep.py <input video> [--noise -35] [--minsil 0.35]
writes: source.mov (CFR 30 fps, 1080p tall, 48 kHz PCM, A/V aligned), voice16k.wav, sil.json,
        captions_raw.json (speech chunks + text, SOURCE seconds), face.json
"""
import argparse, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from common import TB, run, probe, save

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--noise", type=float, default=-35)
ap.add_argument("--minsil", type=float, default=0.35)
ap.add_argument("--av-offset", type=float, default=None, help="force an extra audio shift in ms (+ = later); skips auto-alignment")
ap.add_argument("--no-av-fix", action="store_true", help="don't auto-correct a take whose lips and voice are out of sync")
a = ap.parse_args()

# ── 1. Normalize with explicit A/V alignment ──
# Phone/QuickTime files often start audio later than video (here: +0.156 s). Raw decoders and some
# filters silently drop that offset, which shows up later as "lips don't match". Re-time both streams to
# zero and re-insert the offset with adelay/atrim so source.mp4 is unambiguous from here on.
info = probe(a.input)
v = next(s for s in info["streams"] if s["codec_type"] == "video")
au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
if au is None:
    sys.exit("input has no audio track")
off = float(au.get("start_time", 0)) - float(v.get("start_time", 0))
vdur = float(v.get("duration") or info["format"]["duration"])
print(f"audio offset {off * 1000:+.0f} ms, duration {vdur:.2f}s")


def normalize(off):
    afix = f",adelay={int(off * 1000)}:all=1" if off > 0.005 else (f",atrim=start={-off},asetpts=PTS-STARTPTS" if off < -0.005 else "")
    run(["-i", a.input, "-filter_complex",
         f"[0:v]setpts=PTS-STARTPTS,fps=30,scale=-2:1080,format=yuv420p[v];"
         f"[0:a]asetpts=PTS-STARTPTS,aresample=48000{afix},apad[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{vdur:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "15",
         "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", "source.mov"])


if a.av_offset is not None:
    off += a.av_offset / 1000
    print(f"forced extra audio shift {a.av_offset:+.0f} ms")
normalize(off)
# Container timestamps aren't the whole story: webcams in low light, screen recorders under load and re-encodes
# (lost AAC priming, frame interpolation) can put the voice 100-200 ms off the lips. Measure it on the picture
# itself and correct the take before anything is transcribed, so every later step inherits a synced source.
if a.av_offset is None and not a.no_av_fix:
    try:
        from common import lip_lag
        lag, r, seen = lip_lag("source.mov", 0, min(vdur, 75))
        print(f"lip sync of the raw take: {lag:+d} ms (r={r:.2f}, face in {100 * seen:.0f}% of frames)")
        if r >= 0.2 and abs(lag) >= 50:
            off += lag / 1000            # picture earlier than sound (lag < 0) → move the audio earlier, and vice versa
            normalize(off)
            lag2, r2, _ = lip_lag("source.mov", 0, min(vdur, 75))
            print(f"  corrected audio by {lag:+d} ms → now {lag2:+d} ms (r={r2:.2f})")
    except Exception as e:
        print("lip sync pre-check skipped:", e)
SRC = "source.mov"
run(["-i", SRC, "-vn", "-ac", "1", "-ar", "16000", "voice16k.wav"])

# ── 2. Silences → speech chunks ──
err = subprocess.run(["ffmpeg", "-hide_banner", "-i", "voice16k.wav", "-af", f"silencedetect=noise={a.noise}dB:d={a.minsil}",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
total = float(probe("voice16k.wav")["format"]["duration"])
sil = [(s, ends[i] if i < len(ends) else total) for i, s in enumerate(starts)]
speech, cur = [], 0.0
for s, e in sil:
    if s - cur > 0.12:
        speech.append([round(cur, 3), round(s, 3)])
    cur = e
if total - cur > 0.12:
    speech.append([round(cur, 3), round(total, 3)])

# ── 3. Transcribe each chunk separately ──
# Per-chunk transcription gives caption times that are exact to the speech boundaries; whole-file whisper
# timestamps drift by ~0.3-1 s, which makes captions feel late.
os.makedirs("chunks", exist_ok=True)
MODEL = os.path.join(TB, "ggml-small.en.bin")

def transcribe(i):
    s, e = speech[i]
    w = f"chunks/c{i:03d}.wav"
    # Leading/trailing silence pad: whisper often returns nothing for short clips that start on a word.
    run(["-ss", str(max(0, s - 0.08)), "-t", str(e - s + 0.16), "-i", "voice16k.wav", "-af", "adelay=400:all=1,apad=pad_dur=0.8", w])
    subprocess.run(["whisper-cli", "-m", MODEL, "-f", w, "-oj", "-of", w[:-4], "-t", "2", "-np", "-sow", "-ml", "60"],
                   capture_output=True)
    try:
        segs = json.load(open(w[:-4] + ".json"))["transcription"]
    except Exception:
        segs = []
    out = []
    for g in segs:
        txt = g["text"].strip()
        if not txt or re.fullmatch(r"[\[\(].*[\]\)]", txt):  # [BLANK_AUDIO], (breathing), (music)
            continue
        out.append({"from": g["offsets"]["from"] / 1000 - 0.4, "to": g["offsets"]["to"] / 1000 - 0.4, "text": txt})
    if not out:
        # Loud but untranscribed → keep it as a line to fill in from the script; quiet → breath/noise.
        import numpy as np
        from common import pcm
        x = pcm("voice16k.wav", 16000, s, e - s)
        if len(x) and 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) > -32:
            out.append({"from": 0, "to": e - s, "text": "(?)"})
    return out

with ThreadPoolExecutor(4) as ex:
    results = list(ex.map(transcribe, range(len(speech))))

caps = []
for (s, e), segs in zip(speech, results):
    if not segs:
        continue  # noise/breath: treat as silence downstream
    text = " ".join(g["text"] for g in segs)
    words = text.split()
    # Split long chunks into caption-sized lines (≤ ~10 words), timed proportionally to word count.
    if len(words) > 11:
        n = (len(words) + 9) // 10
        per = len(words) / n
        for k in range(n):
            ws = words[round(k * per):round((k + 1) * per)]
            caps.append({"start": round(s + (e - s) * k / n, 3), "end": round(s + (e - s) * (k + 1) / n, 3), "text": " ".join(ws)})
    else:
        caps.append({"start": s, "end": e, "text": text})
save("sil.json", sil)
save("captions_raw.json", caps)

# ── 4. Face position (for the picture-in-picture crop and full-frame framing) ──
face = None
try:
    import numpy as np, mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(TB, "face_landmarker.task"))))
    pv = probe(SRC)["streams"][0]
    Wd, Hd = int(pv["width"]), int(pv["height"])
    boxes = []
    for k in range(24):
        t = vdur * (k + 0.5) / 24
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", SRC, "-frames:v", "1", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) != Wd * Hd * 3:
            continue
        img = np.frombuffer(raw, np.uint8).reshape(Hd, Wd, 3)
        r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(img)))
        if r.face_landmarks:
            xs = [p.x * Wd for p in r.face_landmarks[0]]
            ys = [p.y * Hd for p in r.face_landmarks[0]]
            boxes.append((np.mean([min(xs), max(xs)]), np.mean([min(ys), max(ys)]), max(ys) - min(ys)))
    if boxes:
        cx, cy, fh = (float(np.median([b[i] for b in boxes])) for i in range(3))
        side = int(min(Hd, Wd, fh * 3.0)) // 2 * 2
        x = int(min(max(cx - side / 2, 0), Wd - side))
        y = int(min(max(cy - side * 0.45, 0), Hd - side))
        face = {"w": Wd, "h": Hd, "cx": round(cx), "cy": round(cy), "face_h": round(fh), "pip": [side, side, x, y]}
except Exception as e:
    print("face detection skipped:", e)
if face is None:
    pv = probe(SRC)["streams"][0]
    Wd, Hd = int(pv["width"]), int(pv["height"])
    side = min(Wd, Hd) * 7 // 10 // 2 * 2
    face = {"w": Wd, "h": Hd, "cx": Wd // 2, "cy": Hd // 3, "face_h": None, "pip": [side, side, (Wd - side) // 2, max(0, Hd // 3 - side // 2)]}
save("face.json", face)

print(f"\n{len(caps)} caption lines, {len(sil)} pauses, face {face}\n")
for c in caps:
    print(f"  {c['start']:7.2f}-{c['end']:7.2f}  {c['text']}")
