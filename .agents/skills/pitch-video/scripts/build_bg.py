"""Step 6: render the background picture track (bg.mp4): one part per shot, concatenated.

Shot kinds (from timeline.json plan):
  speaker      full-frame talking head (cover-cropped around the face)
  rec + fit    app footage from shots/<rec>/ (CDP screencast frames + stamps.json), time-fitted to the shot
  anim         anims/<name>.mp4 rendered by render_anim.mjs
  image        a still with a slow push-in
  title        dark background (the big text comes from the overlay track)
  cine         cinematic hero shot rendered by cine.py (in split layout the cold open is overlaid full-frame
               by compose_vertical.py, so its canvas part here is just black)
Optional: "zoom": "tl"|"tr"|"bl"|"br"|"c" pushes in toward that corner (to make small UI readable).
"""
import bisect, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import layout, load, run, probe, FPS, W, H

t = load("timeline.json")
face = load("face.json")
P = load("project.json")
BG = P.get("background", "0x05070f")
ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS)]
os.makedirs("parts", exist_ok=True)

def zoom(anchor, frames=24, amount=0.5):
    x = {"tl": "0", "bl": "0", "tr": "iw-iw/zoom", "br": "iw-iw/zoom"}.get(anchor, "(iw-iw/zoom)/2")
    y = {"tl": "0", "tr": "0", "bl": "ih-ih/zoom", "br": "ih-ih/zoom"}.get(anchor, "(ih-ih/zoom)/2")
    return f",zoompan=z='1+{amount}*(1-pow(1-min(1,on/{frames}),3))':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}"

def rec_frames(name):
    d = json.load(open(f"shots/{name}/stamps.json"))
    st = d["stamps"]
    s0 = st[0][1]
    return [d["startedAt"] + (ts - s0) for _, ts in st], [i for i, _ in st]

# Cover-crop the speaker to 16:9 keeping the face in the upper-middle third.
sw, sh = face["w"], face["h"]
scale = max(W / sw, H / sh)
cw, ch = round(sw * scale / 2) * 2, round(sh * scale / 2) * 2
cx = min(max(face["cx"] * scale - W / 2, 0), cw - W)
cy = min(max(face["cy"] * scale - H * 0.42, 0), ch - H)
SPEAKER_VF = f"scale={cw}:{ch},crop={W}:{H}:{int(cx)}:{int(cy)},eq=contrast=1.04:saturation=1.06"

# Footage that doesn't match the canvas (16:9 recordings in the split layout's 1080x960 top half) sits on a
# blurred, darkened copy of itself instead of flat bars. Film at the canvas size to avoid it entirely.
if layout() == "split":
    FIT = (f"split[f0][f1];[f0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,eq=brightness=-0.18[blur];"
           f"[f1]scale={W}:{H}:force_original_aspect_ratio=decrease[fit];[blur][fit]overlay=(W-w)/2:(H-h)/2")
else:
    FIT = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={BG}"

for i, p in enumerate(t["plan"]):
    out = f"parts/p{i:02d}.mp4"
    dur = p["end"] - p["start"]
    nfr = round(dur * FPS)
    z = zoom(p["zoom"]) if p.get("zoom") else ""
    if p.get("speaker"):
        run(["-ss", f"{p['start']:.4f}", "-i", "speaker_cut.mov", "-an", "-vf", SPEAKER_VF + z, "-frames:v", str(nfr), *ENC, out])
    elif p.get("cine") and not (p.get("intro") and layout() == "split"):
        run(["-i", f"cine/{p['cine']}.mp4", "-vf", f"scale={W}:{H},tpad=stop_mode=clone:stop_duration=5", "-frames:v", str(nfr), *ENC, out])
    elif p.get("anim"):
        run(["-i", f"anims/{p['anim']}.mp4", "-vf", f"scale={W}:{H},tpad=stop_mode=clone:stop_duration=5" + z, "-frames:v", str(nfr), *ENC, out])
    elif p.get("image"):
        run(["-loop", "1", "-i", p["image"], "-vf", f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
             f"zoompan=z='1+0.08*on/{nfr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS}", "-frames:v", str(nfr), *ENC, out])
    elif p.get("rec"):
        times, idx = rec_frames(p["rec"])
        fa, fb = p["fit"]
        speed = (fb - fa) / dur
        k0 = max(0, bisect.bisect_right(times, fa) - 1)
        sel = [k for k in range(k0, len(times)) if times[k] <= fb + 0.2]
        if not sel:
            sys.exit(f"no frames in shots/{p['rec']} between {fa} and {fb}")
        lines = []
        for j, k in enumerate(sel):
            nxt = times[sel[j + 1]] if j + 1 < len(sel) else times[k] + 1 / FPS
            seg = (max(nxt, fa) - max(times[k], fa)) / speed
            if seg > 0:
                lines.append(f"file '{os.path.abspath(f'shots/{p['rec']}/{idx[k]:06d}.jpg')}'\nduration {seg:.4f}")
        lines.append(f"file '{os.path.abspath(f'shots/{p['rec']}/{idx[sel[-1]]:06d}.jpg')}'")
        open(f"parts/p{i:02d}.txt", "w").write("\n".join(lines) + "\n")
        run(["-f", "concat", "-safe", "0", "-i", f"parts/p{i:02d}.txt", "-filter_complex", FIT + f",fps={FPS},tpad=stop_mode=clone:stop_duration=5" + z,
             "-frames:v", str(nfr), *ENC, out])
    else:  # title / black
        run(["-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}", "-frames:v", str(nfr), *ENC, out])
    got = int(probe(out)["streams"][0]["nb_frames"])
    flag = "" if got == nfr else f"  <-- expected {nfr} frames"
    print(f"p{i:02d} {dur:6.2f}s {got:4d}f  " + ", ".join(f"{k}={v}" for k, v in p.items() if k not in ("start", "end", "scene")) + flag)

open("parts/list.txt", "w").write("".join(f"file 'p{i:02d}.mp4'\n" for i in range(len(t["plan"]))))
run(["-f", "concat", "-safe", "0", "-i", "parts/list.txt", "-c", "copy", "bg.mp4"])
n = int(probe("bg.mp4")["streams"][0]["nb_frames"])
print(f"bg.mp4 {n} frames = {n / FPS:.3f}s (timeline {t['total']:.3f}s)")
