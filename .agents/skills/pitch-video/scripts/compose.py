"""Step 9: final composite → out/<name>.mp4 (1080p30, H.264 + AAC 48 kHz).

Video: bg.mp4 + face bubble (speaker_cut.mov, rounded mask, accent frame) + cards + chips + captions.
Overlays are pre-baked into 3 alpha tracks (qtrle) via the concat demuxer: feeding ~50 looped PNGs straight
into one filter graph is 10-50x slower.
Audio: voice cleaned/compressed/normalized, music side-chain ducked under the voice, SFX on top, limiter.
EVERY audio branch is resampled to 48 kHz: loudnorm outputs 192 kHz and mixing that unconverted produced an
AAC track whose timestamps said 114 s but held 105 s of samples (lips drifted, voice ended early).
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import load, run, probe, audio_graph, FPS

t = load("timeline.json")
P = load("project.json")
face = load("face.json")
pip = load("ov/pip.json")
TOTAL = t["total"]
OUT = P.get("output", "out/demo.mp4")
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
run(["-f", "lavfi", "-i", "color=c=black@0.0:s=1920x1080,format=rgba", "-frames:v", "1", "ov/blank.png"])

def track(name, items):
    items = sorted(items)
    lines, cur = [], 0.0
    for a, b, png in items:
        a, b = max(a, cur), min(b, TOTAL)
        if b <= a:
            continue
        if a > cur:
            lines += [f"file '{os.path.abspath('ov/blank.png')}'", f"duration {a - cur:.4f}"]
        lines += [f"file '{os.path.abspath(png)}'", f"duration {b - a:.4f}"]
        cur = b
    if cur < TOTAL:
        lines += [f"file '{os.path.abspath('ov/blank.png')}'", f"duration {TOTAL - cur:.4f}"]
    lines.append(f"file '{os.path.abspath('ov/blank.png')}'")
    open(f"ov/{name}.txt", "w").write("\n".join(lines) + "\n")
    run(["-f", "concat", "-safe", "0", "-i", f"ov/{name}.txt", "-vf", f"fps={FPS},format=rgba", "-t", f"{TOTAL:.4f}", "-c:v", "qtrle", f"ov/{name}.mov"])

track("trk_caps", [(c["start"], c["end"], f"ov/cap{i:03d}.png") for i, c in enumerate(t["caps"])])
cards = []
for i, p in enumerate(t["plan"]):
    if p.get("title"):
        cards.append((p["start"], p["end"], f"ov/title{i}.png"))
    if p.get("card"):
        cards.append((p["start"] + p.get("card_delay", 0.4), p["end"], f"ov/card_{p['card']}.png"))
    if p.get("end_card"):
        cards.append((p["start"], p["end"], "ov/end.png"))
track("trk_cards", cards)
track("trk_chips", [(s["start"] + 0.2, min(s["start"] + 3.6, s["end"]), f"ov/chip{s['n']}.png") for s in t["scenes"] if s["chip"]])

off = [(p["start"], p["end"]) for p in t["plan"] if p.get("speaker") or p.get("end_card") or p.get("pip") is False]
hide = "+".join(f"between(t,{a},{b - 0.001})" for a, b in off) or "0"
cw, ch, cx, cy = face["pip"]
S = pip["size"]
fc = [
    f"[1:v]crop={cw}:{ch}:{cx}:{cy},scale={S}:{S},format=rgba[pv]",
    f"[2:v]format=gray,scale={S}:{S}[pm]",
    "[pv][pm]alphamerge[pip]",
    f"[0:v][pip]overlay=x={pip['x']}:y={pip['y']}:enable='not({hide})'[v0]",
    f"[v0][3:v]overlay=0:0:enable='not({hide})'[v1]",
    "[v1][4:v]overlay=0:0[v2]",
    "[v2][5:v]overlay=0:0[v3]",
    "[v3][6:v]overlay=0:0,format=yuv420p[vout]",
]
# Picture and sound are rendered in SEPARATE passes and then muxed. In one combined graph ffmpeg silently
# dropped ~9 s of audio samples (looped image inputs + loudnorm/sidechain buffering), wrecking lip sync.
INS = ["-i", "bg.mp4", "-i", "speaker_cut.mov", "-loop", "1", "-i", "ov/pipmask.png", "-loop", "1", "-i", "ov/pipframe.png",
       "-i", "ov/trk_cards.mov", "-i", "ov/trk_chips.mov", "-i", "ov/trk_caps.mov", "-i", "music.wav", "-i", "sfx.wav"]
run([*INS, "-filter_complex", ";".join(fc), "-map", "[vout]", "-an", "-frames:v", str(round(TOTAL * FPS)),
     "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "out/_video.mp4"])
run(["-i", "speaker_cut.mov", "-i", "music.wav", "-i", "sfx.wav", "-filter_complex",
     audio_graph(P.get("music_gain", 0.55), P.get("sfx_gain", 0.85)),
     "-map", "[aout]", "-t", f"{TOTAL:.4f}", "-c:a", "pcm_s16le", "-ar", "48000", "out/_audio.wav"])
run(["-i", "out/_video.mp4", "-i", "out/_audio.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-ar", "48000", "-movflags", "+faststart", OUT])
small = OUT.replace(".mp4", "_small.mp4")
run(["-i", OUT, "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-vf", "scale=1600:-2", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
     "-movflags", "+faststart", small])
print("wrote", OUT, "and", small)
