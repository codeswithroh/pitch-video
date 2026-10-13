"""Step 9b: vertical 9:16 cut (1080x1920) for Reels, Shorts, TikTok and X → out/<name>_vertical.mp4.

Layout: product footage on top (full width), the speaker's face filling the bottom half, captions on the seam.
During full-frame speaker shots and the end card, the face fills the whole frame instead.
Re-uses bg.mp4, speaker_cut.mov, music.wav, sfx.wav and the same audio chain as compose.py.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from common import TB, load, run, FPS

t = load("timeline.json")
P = load("project.json")
face = load("face.json")
TOTAL = t["total"]
OUT = P.get("output", "out/demo.mp4").replace(".mp4", "_vertical.mp4")
os.makedirs("ov_v", exist_ok=True)
theme = {"accent": "#ffe040", "body": "Inter", **(P.get("theme") or {})}

# ── caption PNGs (1080 wide) via Playwright ──
html = os.path.abspath("ov_v/caps.html")
open(html, "w").write(f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;800&display=swap" rel="stylesheet">
<style>html,body{{margin:0;width:1080px;height:1920px;background:transparent}}
.c{{position:absolute;left:50%;top:{1920 // 2 - 20}px;transform:translate(-50%,-50%);width:960px;text-align:center;
font:800 58px/1.15 Inter,sans-serif;color:#fff;padding:18px 26px;background:rgba(6,8,18,.82);border-radius:18px}}
.c b{{color:{theme['accent']}}}</style></head><body><div id=r></div>
<script>window.render=h=>document.getElementById('r').innerHTML=h</script></body></html>""")
js = os.path.abspath("ov_v/render.mjs")
import json
open("ov_v/caps.json", "w").write(json.dumps([c["html"] for c in t["caps"]]))
open(js, "w").write(f"""import fs from "node:fs"; import {{ createRequire }} from "node:module";
const {{ chromium }} = createRequire("{TB}/package.json")("playwright");
const caps = JSON.parse(fs.readFileSync("ov_v/caps.json","utf8"));
const b = await chromium.launch(); const p = await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto("file://{html}"); await p.waitForTimeout(1200); await p.evaluate(()=>document.fonts.ready);
for (const [i,h] of caps.entries()) {{ await p.evaluate(x=>window.render('<div class=c>'+x+'</div>'),h); await p.screenshot({{path:`ov_v/cap${{String(i).padStart(3,"0")}}.png`,omitBackground:true}}); }}
await b.close();""")
subprocess.run(["node", js], check=True)
run(["-f", "lavfi", "-i", "color=c=black@0.0:s=1080x1920,format=rgba", "-frames:v", "1", "ov_v/blank.png"])
lines, cur = [], 0.0
for i, c in enumerate(t["caps"]):
    a, b = max(c["start"], cur), min(c["end"], TOTAL)
    if b <= a:
        continue
    if a > cur:
        lines += [f"file '{os.path.abspath('ov_v/blank.png')}'", f"duration {a - cur:.4f}"]
    lines += [f"file '{os.path.abspath(f'ov_v/cap{i:03d}.png')}'", f"duration {b - a:.4f}"]
    cur = b
lines += [f"file '{os.path.abspath('ov_v/blank.png')}'", f"duration {max(0.04, TOTAL - cur):.4f}", f"file '{os.path.abspath('ov_v/blank.png')}'"]
open("ov_v/caps.txt", "w").write("\n".join(lines) + "\n")
run(["-f", "concat", "-safe", "0", "-i", "ov_v/caps.txt", "-vf", f"fps={FPS},format=rgba", "-t", f"{TOTAL:.4f}", "-c:v", "qtrle", "ov_v/caps.mov"])

# ── picture ──
full = [(p["start"], p["end"]) for p in t["plan"] if p.get("speaker") or p.get("end_card")]
isfull = "+".join(f"between(t,{a},{b - 0.001})" for a, b in full) or "0"
sw, sh = face["w"], face["h"]
# face crop for the bottom half (1080x1080) and for full-frame (1080x1920, i.e. 9:16 of source height)
side = min(sw, sh)
fx = int(min(max(face["cx"] - side / 2, 0), sw - side))
fw = int(sh * 9 / 16) // 2 * 2
ffx = int(min(max(face["cx"] - fw / 2, 0), sw - fw))
fc = [
    "color=c=0x0b0b0d:s=1080x1920:r=30[base]",
    "[0:v]scale=1080:-2,setsar=1[top]",
    f"[1:v]crop={side}:{side}:{fx}:0,scale=1080:1080,setsar=1[bot]",
    f"[1:v]crop={fw}:{sh}:{ffx}:0,scale=1080:1920,setsar=1[fullface]",
    "[base][top]overlay=0:(960-h)/2-40[a]",
    "[a][bot]overlay=0:960[b]",
    f"[b][fullface]overlay=0:0:enable='{isfull}'[c]",
    f"[c][2:v]overlay=0:0:enable='not({isfull})',format=yuv420p[v]",
]
run(["-i", "bg.mp4", "-i", "speaker_cut.mov", "-i", "ov_v/caps.mov", "-filter_complex", ";".join(fc), "-map", "[v]", "-an",
     "-frames:v", str(round(TOTAL * FPS)), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", str(FPS), "ov_v/_video.mp4"])
# ── audio: reuse the horizontal mix (already verified) ──
src = P.get("output", "out/demo.mp4")
run(["-i", "ov_v/_video.mp4", "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-t", f"{TOTAL:.4f}",
     "-movflags", "+faststart", OUT])
print("wrote", OUT)
