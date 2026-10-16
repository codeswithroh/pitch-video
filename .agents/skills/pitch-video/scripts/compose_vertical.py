"""Step 9b: the 9:16 video (1080x1920) for Reels, Shorts, TikTok and X.

Two modes, picked by project.json "layout":
  "split"  the main output (P["output"]). The canvas (bg.mp4 + cards/titles/chips/end card) is 1080x960 and fills
           the top half; the speaker fills the bottom half; captions sit on the seam. Full-frame speaker shots
           show the face over the whole frame. Renders its own audio with the same chain as compose.py.
  "pitch"  a vertical cut of the 16:9 video (out/<name>_vertical.mp4): the 16:9 picture on top, the face below,
           reusing the already-verified horizontal audio.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import TB, alpha_track, audio_graph, caption_items, layout, load, run, FPS, music_gain

t = load("timeline.json")
P = load("project.json")
face = load("face.json")
TOTAL = t["total"]
SPLIT = layout() == "split"
OUT = P.get("output", "out/demo.mp4") if SPLIT else P.get("output", "out/demo.mp4").replace(".mp4", "_vertical.mp4")
SEAM = 960
os.makedirs("ov_v", exist_ok=True)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
theme = {"accent": "#ffe040", "body": "Inter", **(P.get("theme") or {})}

# ── captions ──
# Reel style (word chunks): one look for the whole video, all caps in a dark box with a thin light edge so it
# reads on black, white and footage alike. On the seam over visuals; on the shirt during full-face shots, never
# over the mouth. A chunk that runs across a cut moves to the new shot's position on the cut frame.
items, WORDS = caption_items(t)
STRIP = 260
full_face = [(p["start"], p["end"]) for p in t["plan"] if p.get("speaker")]
sw0, sh0 = face["w"], face["h"]
mouth_full = (face["cy"] + 0.13 * sh0) / sh0 * 1920                     # mouth height in a full-frame face shot
LOW = int(min(1700, mouth_full + 420))                                    # caption centre: on the shirt
POS = {"seam": SEAM - 20, "low": LOW}
html = os.path.abspath("ov_v/caps.html")
size = 64 if WORDS else 58
box = ("display:inline-block;max-width:960px;text-transform:uppercase;letter-spacing:.5px;padding:12px 26px 14px;"
       "background:rgba(8,8,12,.88);border:2px solid rgba(255,255,255,.22);border-radius:14px") if WORDS else \
      "display:inline-block;width:960px;padding:18px 26px;background:rgba(6,8,18,.82);border-radius:18px"
open(html, "w").write(f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={theme['body'].replace(' ', '+')}:wght@700;800;900&display=swap" rel="stylesheet">
<style>html,body{{margin:0;width:1080px;height:{STRIP}px;background:transparent}}
#r{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}}
.c{{{box};text-align:center;font:{900 if WORDS else 800} {size}px/1.12 "{theme['body']}",Inter,sans-serif;color:#fff}}
.c b{{color:{theme['accent']};font-weight:inherit}}</style></head><body><div id=r></div>
<script>window.render=h=>document.getElementById('r').innerHTML=h</script></body></html>""")
js = os.path.abspath("ov_v/render.mjs")
open("ov_v/caps.json", "w").write(json.dumps([c["html"] for c in items]))
open(js, "w").write(f"""import fs from "node:fs"; import {{ createRequire }} from "node:module";
const {{ chromium }} = createRequire("{TB}/package.json")("playwright");
const caps = JSON.parse(fs.readFileSync("ov_v/caps.json","utf8"));
const b = await chromium.launch(); const p = await b.newPage({{viewport:{{width:1080,height:{STRIP}}}}});
await p.goto("file://{html}"); await p.waitForTimeout(1200); await p.evaluate(()=>document.fonts.ready);
for (const [i,h] of caps.entries()) {{ await p.evaluate(x=>window.render('<div class=c>'+x+'</div>'),h); await p.screenshot({{path:`ov_v/cap${{String(i).padStart(3,"0")}}.png`,omitBackground:true}}); }}
await b.close();""")
subprocess.run(["node", js], check=True)


def spans(a, b):
    """Split [a, b) at full-face shot edges → [(start, end, position)]."""
    cuts = sorted({a, b, *[x for s, e in full_face for x in (s, e) if a < x < b]})
    return [(s, e, "low" if any(fs <= s + 1e-3 and e <= fe + 1e-3 for fs, fe in full_face) else "seam")
            for s, e in zip(cuts, cuts[1:]) if e - s > 1e-3]


tracks = {"seam": [], "low": []}
boxes = []
for i, c in enumerate(items):
    for s, e, pos in spans(c["start"], min(c["end"], TOTAL)):
        tracks[pos].append((s, e, f"ov_v/cap{i:03d}.png"))
        boxes.append({"start": round(s, 3), "end": round(e, 3), "pos": pos, "y0": POS[pos] - 60, "y1": POS[pos] + 60})
json.dump(boxes, open("ov_v/caption_boxes.json", "w"))
cap_seam = alpha_track("caps_seam", tracks["seam"], TOTAL, (1080, STRIP), d="ov_v")
cap_low = alpha_track("caps_low", tracks["low"], TOTAL, (1080, STRIP), d="ov_v")

# ── picture ──
full = [(p["start"], p["end"]) for p in t["plan"] if p.get("speaker") or (p.get("end_card") and not SPLIT)]
isfull = "+".join(f"between(t,{a},{b - 0.001})" for a, b in full) or "0"
sw, sh = face["w"], face["h"]
fw = int(sh * 9 / 16) // 2 * 2                      # full-frame face: 9:16 crop of the source height
ffx = int(min(max(face["cx"] - fw / 2, 0), sw - fw))
if SPLIT:
    # bottom half: a 9:8 crop around the face (1080x960)
    bh = min(sh, int(sw * 8 / 9)) // 2 * 2
    bw = int(bh * 9 / 8) // 2 * 2
    bx = int(min(max(face["cx"] - bw / 2, 0), sw - bw))
    by = int(min(max(face["cy"] - bh * 0.45, 0), sh - bh))
    cards = []
    for i, p in enumerate(t["plan"]):
        if p.get("title"):
            cards.append((p["start"], p["end"], f"ov/title{i}.png"))
        if p.get("card"):
            cards.append((p["start"] + p.get("card_delay", 0.4), p["end"], f"ov/card_{p['card']}.png"))
        if p.get("end_card"):
            cards.append((p["start"], p["end"], "ov/end.png"))
    alpha_track("trk_cards_split", cards, TOTAL, (1080, 960))
    alpha_track("trk_chips_split", [(s["start"] + 0.2, min(s["start"] + 3.6, s["end"]), f"ov/chip{s['n']}.png")
                                    for s in t["scenes"] if s["chip"]], TOTAL, (1080, 960))
    fc = [
        "color=c=0x0b0b0d:s=1080x1920:r=30[base]",
        "[0:v]scale=1080:960,setsar=1[top]",
        "[top][3:v]overlay=0:0[top1]",
        "[top1][4:v]overlay=0:0[top2]",
        f"[1:v]crop={bw}:{bh}:{bx}:{by},scale=1080:960,setsar=1[bot]",
        f"[1:v]crop={fw}:{sh}:{ffx}:0,scale=1080:1920,setsar=1[fullface]",
        "[base][top2]overlay=0:0[a]",
        f"[a][bot]overlay=0:{SEAM}[b]",
        # a thin accent line on the seam ties the halves together
        f"[b]drawbox=x=0:y={SEAM - 3}:w=1080:h=6:color={theme['accent']}@0.9:t=fill[b2]",
        f"[b2][fullface]overlay=0:0:enable='{isfull}'[c]",
        f"[c][2:v]overlay=0:{POS['seam'] - STRIP // 2}[c2]",
        f"[c2][5:v]overlay=0:{POS['low'] - STRIP // 2},format=yuv420p[v]",
    ]
    ins = ["-i", "bg.mp4", "-i", "speaker_cut.mov", "-i", cap_seam, "-i", "ov/trk_cards_split.mov", "-i", "ov/trk_chips_split.mov", "-i", cap_low]
else:
    side = min(sw, sh)
    fx = int(min(max(face["cx"] - side / 2, 0), sw - side))
    fc = [
        "color=c=0x0b0b0d:s=1080x1920:r=30[base]",
        "[0:v]scale=1080:-2,setsar=1[top]",
        f"[1:v]crop={side}:{side}:{fx}:0,scale=1080:1080,setsar=1[bot]",
        f"[1:v]crop={fw}:{sh}:{ffx}:0,scale=1080:1920,setsar=1[fullface]",
        "[base][top]overlay=0:(960-h)/2-40[a]",
        "[a][bot]overlay=0:960[b]",
        f"[b][fullface]overlay=0:0:enable='{isfull}'[c]",
        f"[c][2:v]overlay=0:{POS['seam'] - STRIP // 2}[c2]",
        f"[c2][3:v]overlay=0:{POS['low'] - STRIP // 2},format=yuv420p[v]",
    ]
    ins = ["-i", "bg.mp4", "-i", "speaker_cut.mov", "-i", cap_seam, "-i", cap_low]


# Cold open (split): the cinematic shots fill the whole 9:16 frame, above everything, before the first word.
INTRO = t.get("intro", 0)
if SPLIT and INTRO:
    parts = [p for p in t["plan"] if p.get("intro")]
    open("ov_v/intro.txt", "w").write("".join(f"file '{os.path.abspath(f'cine/{p['cine']}.mp4')}'\n" for p in parts))
    run(["-f", "concat", "-safe", "0", "-i", "ov_v/intro.txt", "-vf", f"scale=1080:1920,fps={FPS},tpad=stop_mode=clone:stop_duration=600",
         "-t", f"{TOTAL:.4f}", "-c:v", "libx264", "-preset", "fast", "-crf", "15", "ov_v/intro.mp4"])
    ins += ["-i", "ov_v/intro.mp4"]
    k = ins.count("-i") - 1
    fc[-1] = fc[-1].replace(",format=yuv420p[v]", "[v0]")
    fc.append(f"[v0][{k}:v]overlay=0:0:enable='lt(t,{INTRO - 0.001})',format=yuv420p[v]")


def has_drawbox():
    return "drawbox" in subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout


if SPLIT and not has_drawbox():
    fc = [x.replace(f"[b]drawbox=x=0:y={SEAM - 3}:w=1080:h=6:color={theme['accent']}@0.9:t=fill[b2]", "[b]null[b2]") for x in fc]
run([*ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-an",
     "-frames:v", str(round(TOTAL * FPS)), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", str(FPS), "ov_v/_video.mp4"])

# ── audio ──
if SPLIT:
    # Same chain as compose.py, rendered in its own pass (one combined graph once dropped ~9 s of samples).
    run(["-i", "speaker_cut.mov", "-i", "music.wav", "-i", "sfx.wav", "-filter_complex",
         audio_graph(music_gain(P), P.get("sfx_gain", 0.85)),
         "-map", "[aout]", "-t", f"{TOTAL:.4f}", "-c:a", "pcm_s16le", "-ar", "48000", "ov_v/_audio.wav"])
    run(["-i", "ov_v/_video.mp4", "-i", "ov_v/_audio.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT])
else:
    # reuse the horizontal mix (already verified)
    run(["-i", "ov_v/_video.mp4", "-i", P.get("output", "out/demo.mp4"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "copy", "-t", f"{TOTAL:.4f}", "-movflags", "+faststart", OUT])
print("wrote", OUT)
