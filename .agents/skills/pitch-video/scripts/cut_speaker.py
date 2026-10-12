"""Step 4: cut the talking head on the kept intervals and apply the speed-up → speaker_cut.mov.

Sample-exact: every piece is cut by FRAME number on video and the matching SAMPLE number on audio
(48000 / 30 = 1600 samples per frame), so audio and video can never drift apart across cuts.
Audio stays PCM until the final encode (AAC priming + odd sample rates were the root of a 9 s drift once).
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import load, run, probe, FPS

t = load("timeline.json")
S = t["speed"]
SPF = 48000 // FPS
fc = []
for i, (a, b) in enumerate(t["keep"]):
    fa, fb = round(a * FPS), round(b * FPS)
    d = (fb - fa) / FPS
    fc.append(f"[0:v]trim=start_frame={fa}:end_frame={fb},setpts=PTS-STARTPTS[v{i}];"
              f"[0:a]atrim=start_sample={fa * SPF}:end_sample={fb * SPF},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.015):.4f}:d=0.015[a{i}]")
n = len(t["keep"])
fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
fc.append(f"[vc]setpts=PTS/{S},fps={FPS}[v];[ac]atempo={S},aresample=48000[a]")
run(["-i", "source.mov", "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", "speaker_cut.mov"])
st = {s["codec_type"]: float(s["duration"]) for s in probe("speaker_cut.mov")["streams"]}
print(f"speaker_cut.mov  video {st['video']:.3f}s  audio {st['audio']:.3f}s  timeline {t['total']:.3f}s")
if abs(st["video"] - st["audio"]) > 0.05 or abs(st["video"] - t["total"]) > 0.1:
    sys.exit("DURATION MISMATCH: investigate before going further")
