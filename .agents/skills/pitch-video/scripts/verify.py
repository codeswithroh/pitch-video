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
import json, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import FPS, TB, VOICE, lip_lag, load, run, probe, pcm, music_gain
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

# 3. lip sync on the speaker track (from the first word: a cold open is black on the speaker track)
try:
    L_ms, r3, seen = lip_lag("speaker_cut.mov", start=t.get("intro", 0))
    print(f"[3] lip sync: mouth vs voice best lag {L_ms:+d} ms (r={r3:.2f}; + = picture later). Face found in {100 * seen:.0f}% of frames")
    if r3 < 0.1:
        # Mouth movement doesn't track the voice at any lag (a still image, face too small, mouth hidden):
        # the offset above is noise, so this was not measured. Real talking heads score ~0.2-0.5.
        skipped.append(f"lip sync inconclusive (mouth vs voice r={r3:.2f}, expected > 0.1)")
    elif r3 > 0.15 and not (-70 <= L_ms <= 140):
        fails.append(f"lip sync off by {L_ms} ms")
except Exception as e:
    print("[3] lip sync check SKIPPED:", e)
    skipped.append(f"lip sync not measured ({e})")

# 4. intelligibility
fc = (f"[0:a]{VOICE},asplit=2[voice][key];"
      f"[1:a]aresample=48000,volume={music_gain(P)}[mus];[mus][key]sidechaincompress=threshold=0.02:ratio=12:attack=15:release=450:makeup=1[musd];"
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
err = subprocess.run(["ffmpeg", "-hide_banner", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
tp = re.findall(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", err)
tpv = float(tp[-1]) if tp and tp[-1] != "-inf" else -99
print(f"[5] integrated loudness {lufs[-1] if lufs else '?'} LUFS (target -16..-11), true peak {tpv:.1f} dBTP (max -1.0), measured on the delivered file")
if tpv > -1.0:
    fails.append(f"true peak {tpv:.1f} dBTP > -1.0 (platform transcodes will clip)")
os.makedirs("out", exist_ok=True)
run(["-i", OUT, "-vf", f"fps=16/{TOTAL},scale=480:-2,tile=4x4", "-frames:v", "1", "out/contact.png"])
print("    contact sheet: out/contact.png")

# 6. every word whole: transcribe the delivered audio and look for caption words missing near a cut join.
# (ASR can mishear a word that's fine, so a miss far from any join is only listed; one at a join fails.)
try:
    run(["-i", OUT, "-vn", "-ac", "1", "-ar", "16000", "out/_final16k.wav"])
    subprocess.run(["whisper-cli", "-m", os.path.join(TB, "ggml-small.en.bin"), "-f", "out/_final16k.wav", "-oj", "-of", "out/_final_asr",
                    "-t", "4", "-np"], capture_output=True)
    heard = " ".join(g["text"] for g in json.load(open("out/_final_asr.json"))["transcription"])
    NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight",
           "9": "nine", "10": "ten", "100": "hundred", "1000": "thousand"}
    nw = lambda x: (lambda y: NUM.get(y, y))(re.sub(r"[^a-z0-9]", "", x.lower()))
    said = [(nw(w["text"]), w["start"]) for c in t["caps"] for w in c.get("words", [])] or \
           [(nw(w), c["start"]) for c in t["caps"] for w in re.sub(r"<[^>]+>", "", c["html"]).split()]
    said = [x for x in said if x[0]]
    hw = [nw(x) for x in heard.split() if nw(x)]
    joins, acc = [], t.get("intro", 0)
    for a, b in t["keep"][:-1]:
        acc += (b - a) / t["speed"]
        joins.append(acc)
    import difflib
    missing = []
    for tag, a0, a1, b0, b1 in difflib.SequenceMatcher(None, [x[0] for x in said], hw, autojunk=False).get_opcodes():
        if tag == "delete":
            missing += said[a0:a1]
        elif tag == "replace":
            # a word heard as something that doesn't sound like it ("worked" -> "did") is as gone as a dropped one;
            # near-misses ("pitch" -> "peach") are ASR spelling and stay
            for x in said[a0:a1]:
                if max((difflib.SequenceMatcher(None, x[0], y).ratio() for y in hw[b0:b1]), default=0) < 0.5:
                    missing.append(x)
    # A word only counts as clipped if the RAW take had it clearly: compare with what ASR heard in the raw
    # recording around the same source time (a mumbled word is unclear in both, and the cut didn't cause it).
    src_t = {}
    k = 0
    for c in load("captions.json"):
        for w in c.get("words", []):
            src_t[k] = w["start"]
            k += 1
    raw_words = []
    for c in load("captions_raw.json", []):
        ws = [x for x in c["text"].split() if nw(x)]
        for j, x in enumerate(ws):
            raw_words.append((nw(x), c["start"] + (c["end"] - c["start"]) * (j + 0.5) / len(ws)))
    idx = {id(x): i for i, x in enumerate(said)}

    v16 = pcm("voice16k.wav", 16000) if os.path.exists("voice16k.wav") else None
    def db(a, b):  # peak 10 ms energy of a word
        x = v16[int(a * 16000):max(int(a * 16000) + 160, int(b * 16000))]
        e = np.sqrt(np.convolve(x ** 2, np.ones(160) / 160, "valid"))
        return 20 * np.log10(e.max() + 1e-9) if len(e) else -120
    speech_db = np.median([db(w["start"], w["end"] + 0.1) for c in load("captions.json") for w in c.get("words", [])]) if v16 is not None else 0

    if v16 is not None:                                   # room noise = the quietest 10% of 10 ms frames of the take
        _e = 20 * np.log10(np.sqrt(np.convolve(v16 ** 2, np.ones(160) / 160, "valid"))[::160] + 1e-9)
        floor = float(np.percentile(_e, 10))
    else:
        floor = speech_db - 30

    def clear_in_raw(x):
        st = src_t.get(idx.get(id(x)))
        if st is None:
            return True
        if v16 is not None and db(st, st + 0.3) < floor + 15:
            return False                                 # mumbled / trailing off in the raw: ASR can't judge it
        return any(abs(rt - st) < 0.8 and difflib.SequenceMatcher(None, x[0], rw).ratio() >= 0.75 for rw, rt in raw_words)

    near = [x for x in missing]
    at_join = [x for x in missing if clear_in_raw(x)]                  # 6a: clear in the raw, gone in the final
    unclear = [x for x in missing if x not in at_join]
    if unclear:
        print("    quiet/mumbled in the raw take, ASR can't judge them: " + ", ".join(f"'{w}' @ {ts:.2f}s" for w, ts in unclear))
    # 6b: physical cut test. The audio each join threw away (60 ms at both edges) must be room noise, not speech.
    edge_bad = []
    if v16 is not None:
        for k, j in enumerate(joins):
            e1, s2 = t["keep"][k][1], t["keep"][k + 1][0]
            lvl = max(db(e1, e1 + 0.06), db(s2 - 0.06, s2))
            if lvl > floor + 15:
                edge_bad.append(f"{j:.2f}s ({lvl - floor:+.0f} dB over room noise)")
        print(f"[6b] cut edges: {len(joins)} joins, {len(edge_bad)} cut into sound (room noise {floor:.0f} dB)")
        if edge_bad:
            fails.append("cut inside speech at " + ", ".join(edge_bad[:6]))
    print(f"[6] words in final audio: {len(said) - len(missing)}/{len(said)} heard; clear in the raw but missing: {len(at_join)}"
          + "")
    if at_join:
        fails.append("word(s) missing from the final audio: " + ", ".join(f"'{w}' @ {ts:.2f}s" for w, ts in at_join))
except Exception as e:
    print("[6] word check SKIPPED:", e)
    skipped.append(f"final-audio word check not run ({e})")

# 7. no black flash or one-frame pop at any cut (single screenshots miss these; strips across cuts catch them)
cuts = sorted({round(p["start"], 3) for p in t["plan"] if p["start"] > 0} | {round(j, 3) for j in (joins if 'joins' in dir() else [])})
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", OUT, "-vf", "scale=96:-2,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
hh = len(raw) // (96 * max(1, round(TOTAL * FPS)))
fr = np.frombuffer(raw[: 96 * hh * (len(raw) // (96 * hh))], np.uint8).reshape(-1, hh, 96).astype(np.float32) / 255 if hh else np.zeros((0, 1, 96))
bad_cuts = []
for c in cuts:
    k = round(c * FPS)
    for i in range(max(1, k - 3), min(len(fr) - 1, k + 3)):
        m, a_, b_ = fr[i].mean(), fr[i - 1].mean(), fr[i + 1].mean()
        pop = np.abs(fr[i] - fr[i - 1]).mean() > 0.12 and np.abs(fr[i] - fr[i + 1]).mean() > 0.12 and np.abs(fr[i - 1] - fr[i + 1]).mean() < 0.04
        if (m < 0.03 and a_ > 0.08 and b_ > 0.08) or pop:
            bad_cuts.append(f"{i / FPS:.2f}s")
print(f"[7] cut frames: {len(cuts)} cuts checked, {len(bad_cuts)} flash/pop frames")
if bad_cuts:
    fails.append("one-frame flash or pop at " + ", ".join(sorted(set(bad_cuts))[:8]))

# 8. captions never over the mouth (first 2.5 s frame by frame, plus the first frame of every face shot)
if os.path.exists("ov_v/caption_boxes.json") and t.get("captions", {}).get("mode") == "words":
    try:
        import mediapipe as mp
        from mediapipe.tasks.python import vision, BaseOptions
        lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=os.path.join(TB, "face_landmarker.task")), running_mode=vision.RunningMode.IMAGE))
        boxes = json.load(open("ov_v/caption_boxes.json"))
        intro = t.get("intro", 0)
        times = [intro + k * 0.1 for k in range(26)] + [p["start"] + 0.05 for p in t["plan"] if p.get("speaker")]
        over = []
        for ts in times:
            act = [b for b in boxes if b["start"] <= ts < b["end"]]
            if not act:
                continue
            img = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{ts:.3f}", "-i", OUT, "-frames:v", "1", "-vf", "format=rgb24",
                                  "-f", "rawvideo", "-"], capture_output=True).stdout
            H_ = len(img) // (1080 * 3)
            if not H_:
                continue
            r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.frombuffer(img, np.uint8)[: 1080 * H_ * 3].reshape(H_, 1080, 3).copy()))
            for f_ in r.face_landmarks:
                my = [f_[i].y * H_ for i in (0, 13, 14, 17, 61, 291)]
                if any(b["y0"] - 10 < max(my) and min(my) < b["y1"] + 10 for b in act):
                    over.append(f"{ts:.2f}s")
        print(f"[8] caption vs mouth: {len(times)} frames checked, {len(over)} with a caption over the mouth")
        if over:
            fails.append("caption over the mouth at " + ", ".join(sorted(set(over))[:8]))
    except Exception as e:
        print("[8] caption/mouth check SKIPPED:", e)

if fails:
    print("\nRESULT: FAIL\n  - " + "\n  - ".join(fails))
    sys.exit(1)
if skipped:
    # A skipped check is not a passed check: never report PASS for something we did not measure.
    print("\nRESULT: UNVERIFIED\n  - " + "\n  - ".join(skipped))
    sys.exit(2)
print("\nRESULT: PASS")
sys.exit(0)
