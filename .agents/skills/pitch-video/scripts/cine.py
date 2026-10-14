"""Step 5c: render cinematic hero shots of real UI → cine/<name>.mp4, at the exact shot length.

usage: python cine.py [name ...]     (default: every shot with "cine" in timeline.json, intro included)

A hero shot looks ALONG the product's real interface instead of at it: the UI is a slab floating in a black
void, tilted back and rotated so text runs diagonally, with a thin band in focus and everything nearer or
farther melting into blur. The camera drifts slowly toward where the action is and is still moving at the
cut. A soft pool of light lies on the slab around the subject and trails it. The UI itself moves because
the texture is real footage (shots/<name>/ from film.mjs, ideally filmed with hidpi) or a sharp still.
Look and method after 1weiho/cinematic-shot (github.com/1weiho/cinematic-shot); this is an independent
implementation in numpy/OpenCV: true perspective homography, per-pixel depth, depth-of-field by blending a
blur stack on that depth, a light pool computed in plane coordinates, lens vignette and film grain.

Shot spec (in project.json shots, or project.json "intro": {"shots": [...]}):
  {"cine": "hero",                 # name → cine/hero.mp4 (unique per shot)
   "src": "shots/site" | "stills/hero.png",
   "t": 2.0, "to": 6.0,            # footage only: slice of the recording clock to play (time-fitted)
   "focus": [0.30, 0.22],          # subject at shot start, as a fraction of the UI (x, y)
   "track": [0.42, 0.24],          # where the camera drifts to by the end (default: a small move along the line)
   "rack": [0.6, [0.4, 0.5]],      # optional: at 60% of the shot, focus slides to this point (0.6 s ease)
   "scale": "macro",               # xmacro (6x) | macro (3.2x) | medium (2x) | wide (0.95x, the payoff only)
   "roll": -14, "pitch": 38, "yaw": 8, "push": 0.03,   # optional overrides; roll sign alternates by default
   "len": 3.5}                     # intro shots only: length in seconds (in-video shots get their length from the words)
"""
import json, os, subprocess, sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(__file__))
from common import FPS, W, H, layout, load

SCALES = {  # mag, pitch, |roll|, |yaw|, sharp band (share of frame h), max blur at 1080p, spill radius along/across (frame w)
    "xmacro": dict(mag=6.0, pitch=44, roll=16, yaw=10, band=0.06, blur=24, spill=(0.35, 0.22), core=0.4),
    "macro": dict(mag=3.2, pitch=38, roll=13, yaw=8, band=0.11, blur=20, spill=(0.43, 0.28), core=0.4),
    "medium": dict(mag=2.0, pitch=32, roll=10, yaw=7, band=0.22, blur=14, spill=(0.52, 0.35), core=0.45),
    "wide": dict(mag=0.95, pitch=10, roll=0, yaw=2, band=0.6, blur=6, spill=(0.78, 0.56), core=0.0),
}
SPILL = np.array([[0, 0], [0.15, 0], [0.3, 0.06], [0.5, 0.22], [0.68, 0.5], [0.85, 0.82], [1.0, 1.0]])
CORE = np.array([[0, 0], [0.45, 0], [0.7, 0.10], [1.0, 0.22]])


def ramp(x, stops):
    return np.interp(x, stops[:, 0], stops[:, 1])


def rot(pitch, yaw, roll):
    """CSS order rotateX(pitch) rotateY(yaw) rotateZ(roll): roll applies first. Degrees. y points down, z to the viewer."""
    a, b, c = np.radians([pitch, yaw, roll])
    Rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    Ry = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    Rz = np.array([[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


class Source:
    """A still, or a recording folder (shots/<name>/ with stamps.json) played over [t, to]."""

    def __init__(self, src, t0=0.0, t1=None, dur=1.0):
        self.still = None
        if os.path.isdir(src):
            d = json.load(open(f"{src}/stamps.json"))
            s0 = d["stamps"][0][1]
            self.times = [d["startedAt"] + (ts - s0) for _, ts in d["stamps"]]
            self.idx = [i for i, _ in d["stamps"]]
            self.dir = src
            self.t0 = t0 if t0 else self.times[0]
            self.rate = ((t1 - self.t0) / dur) if t1 else 1.0
            self.cache = (None, None)
        else:
            self.still = cv2.imread(src, cv2.IMREAD_COLOR)
            if self.still is None:
                sys.exit(f"cine: can't read {src}")

    def frame(self, s):
        if self.still is not None:
            return self.still
        tt = self.t0 + s * self.rate
        k = max(0, min(len(self.times) - 1, int(np.searchsorted(self.times, tt, "right")) - 1))
        if self.cache[0] != k:
            self.cache = (k, cv2.imread(f"{self.dir}/{self.idx[k]:06d}.jpg", cv2.IMREAD_COLOR))
        return self.cache[1]


def targets_for(src):
    """Named subject positions saved next to a still (stills/x.json) or a recording (shots/x/targets.json)."""
    f = os.path.join(src, "targets.json") if os.path.isdir(src) else os.path.splitext(src)[0] + ".json"
    return json.load(open(f)) if os.path.exists(f) else {}


def render(spec, n, OW, OH, out, flip):
    tg = targets_for(spec["src"])
    for key in ("focus", "track"):
        if isinstance(spec.get(key), str):
            if spec[key] not in tg:
                sys.exit(f"cine: target {spec[key]!r} not found for {spec['src']} (have: {list(tg)})")
            spec = {**spec, key: tg[spec[key]]}
    if spec.get("rack") and isinstance(spec["rack"][1], str):
        spec = {**spec, "rack": [spec["rack"][0], tg[spec["rack"][1]]]}
    sc = SCALES[spec.get("scale", "macro")]
    wide = spec.get("scale") == "wide"
    dur = n / FPS
    src = Source(spec["src"], spec.get("t", 0.0), spec.get("to"), dur)
    tex0 = src.frame(0)
    th, tw = tex0.shape[:2]
    dpr = spec.get("dpr", 2 if tw >= 2400 else 1)          # texture px per UI px (hidpi recordings/stills)
    uw, uh = tw / dpr, th / dpr                              # UI size in native px
    k = OH / 1080                                            # everything below is specified at 1080p
    P = (2000 if wide else 1300) * max(OW, OH) / 1920        # CSS-style perspective distance
    roll0 = spec.get("roll", 0 if wide else sc["roll"] * (1 if flip else -1))
    yaw0 = spec.get("yaw", sc["yaw"] * (-1 if flip else 1))
    pitch0 = spec.get("pitch", sc["pitch"])
    mag0 = spec.get("mag", sc["mag"])
    push = spec.get("push", 0.05 if wide else 0.03)
    turn = spec.get("turn", 0 if wide else 1.5 * (1 if roll0 >= 0 else -1))
    f0 = np.array(spec.get("focus", [0.5, 0.4])) * [uw, uh]
    f1 = np.array(spec.get("track", (spec.get("focus", [0.5, 0.4])[0] + 0.06, spec.get("focus", [0.5, 0.4])[1] + 0.01))) * [uw, uh]
    frame_at = np.array(spec.get("frame", [0.5, 0.5])) * [OW, OH]   # where the subject sits on screen
    rack = spec.get("rack")
    maxblur = sc["blur"] * k
    levels = [0, 2, 4, 7, 11, 16, 24]
    levels = [l * k for l in levels if l * k <= maxblur * 1.01] + ([maxblur] if maxblur > 24 * k else [])
    # Pool size follows the frame's long side (a 9:16 cold open is narrow but tall).
    base = max(OW, OH * 0.9)
    # Light-themed UIs (white pages) would turn the pool into a hard spotlight: expose them down and spread the
    # light wider, so the paper reads as a dim lit surface rather than a hole cut in black.
    lum = float(np.median(cv2.cvtColor(tex0, cv2.COLOR_BGR2GRAY))) / 255
    light_ui = lum > 0.5
    expo = 0.42 / lum if light_ui else 1.0
    spread = 1.7 if light_ui else 1.0
    rng = np.random.default_rng(7)
    lag_hist = []
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", out],
                          stdin=subprocess.PIPE)
    ys, xs = np.mgrid[0:OH, 0:OW].astype(np.float32)
    hs, ws = OH // 2, OW // 2                                 # plane coordinates/depth/light are smooth: compute at half res
    ys2, xs2 = (np.mgrid[0:hs, 0:ws].astype(np.float32) + 0.5) * 2 - 0.5
    up = lambda a: cv2.resize(a.astype(np.float32), (OW, OH), interpolation=cv2.INTER_LINEAR)
    vign = 1 - 0.7 * np.clip((np.hypot((xs - OW / 2) / (1.2 * OW / 2), (ys - OH / 2) / (0.95 * OH / 2)) - 0.5) / 0.5, 0, 1)

    def drift(s):
        """Ease-out over the first third into a constant drift: the camera never comes to rest before the cut."""
        c = 0.15
        return (s + c * (1 - (1 - min(1.0, 3 * s)) ** 2)) / (1 + c)

    for i in range(n):
        s = i / max(1, n - 1)
        u = drift(s)
        F = f0 + (f1 - f0) * u                                # camera focus point on the UI (native px)
        mag = mag0 * (1 + push * u)
        R = rot(pitch0, yaw0, roll0 + turn * u)

        # Homography: UI px (x, y) → screen. Plane point relative to F, scaled, rotated, perspective-projected.
        def proj(pts):
            p = np.c_[(pts - F) * mag, np.zeros(len(pts))] @ R.T
            zz = p[:, 2]
            return np.c_[frame_at[0] + p[:, 0] * P / (P - zz), frame_at[1] + p[:, 1] * P / (P - zz)], zz
        # Only the part of the slab in front of the camera can be projected: at high magnification the far
        # corners of a full page end up behind the lens and the homography flips. Use a window around the
        # subject, shrunk until every corner is safely in front (the window's edge falls into the dark anyway).
        hx, hy = 1.6 * OW / mag, 1.6 * OH / mag
        for _ in range(30):
            x0, x1 = max(0, F[0] - hx), min(uw, F[0] + hx)
            y0, y1 = max(0, F[1] - hy), min(uh, F[1] + hy)
            corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], float)
            scr, zc = proj(corners)
            if zc.max() < 0.8 * P:
                break
            hx, hy = hx * 0.85, hy * 0.85
        Hm = cv2.getPerspectiveTransform((corners * dpr).astype(np.float32), scr.astype(np.float32))
        tex = src.frame(s).astype(np.float32)
        cv2.rectangle(tex, (0, 0), (tex.shape[1] - 1, tex.shape[0] - 1), (60, 60, 60), max(1, int(dpr)))  # hairline slab edge
        img = cv2.warpPerspective(tex, Hm, (OW, OH), flags=cv2.INTER_LINEAR, borderValue=0)
        win = np.zeros(tex.shape[:2], np.float32)
        win[int(y0 * dpr):int(y1 * dpr), int(x0 * dpr):int(x1 * dpr)] = 1
        img = img * cv2.warpPerspective(win, Hm, (OW, OH), flags=cv2.INTER_LINEAR, borderValue=0)[..., None]
        inside = cv2.warpPerspective(win, Hm, (OW, OH), flags=cv2.INTER_LINEAR, borderValue=0)

        # Per-pixel plane coords (UI px) via the inverse homography, then depth z (linear on the plane).
        Hi = np.linalg.inv(Hm)
        den = Hi[2, 0] * xs2 + Hi[2, 1] * ys2 + Hi[2, 2]
        pu = (Hi[0, 0] * xs2 + Hi[0, 1] * ys2 + Hi[0, 2]) / den / dpr
        pv = (Hi[1, 0] * xs2 + Hi[1, 1] * ys2 + Hi[1, 2]) / den / dpr
        gz = R[2, :2] * mag                                   # dz per UI px along x, y
        z = gz[0] * (pu - F[0]) + gz[1] * (pv - F[1])
        Fd = F
        if rack:
            at, pt = rack
            r = np.clip((s * dur - at * dur) / 0.6, 0, 1)
            r = r * r * (3 - 2 * r)
            Fd = F + (np.array(pt) * [uw, uh] - F) * r
        zf = gz[0] * (Fd[0] - F[0]) + gz[1] * (Fd[1] - F[1])
        # Blur grows with distance from the focal plane; scaled so the frame's far edge reaches maxblur.
        dz = np.abs(z - zf)
        ins2 = inside[::2, ::2][:hs, :ws]
        zs = np.percentile(dz[ins2 > 0.5], 97) if (ins2 > 0.5).any() else 1
        band = sc["band"] * zs * 1.6                          # the sharp band, in depth units
        b = up(np.clip((dz - band) / max(1e-6, zs - band), 0, 1) * maxblur)

        # Depth of field: blend a blur stack by per-pixel blur radius (screen-space, on the warped plate).
        stack = [img]
        for L in levels[1:]:
            q = max(1, int(L / 3))
            small = cv2.resize(img, (OW // q, OH // q), interpolation=cv2.INTER_AREA)
            small = cv2.GaussianBlur(small, (0, 0), max(0.5, L / q / 2))
            stack.append(cv2.resize(small, (OW, OH), interpolation=cv2.INTER_LINEAR))
        lv = np.array(levels, np.float32)
        j = np.clip(np.searchsorted(lv, b) - 1, 0, len(lv) - 2)
        w = np.clip((b - lv[j]) / (lv[j + 1] - lv[j]), 0, 1)[..., None]
        out_img = np.zeros_like(img)
        for li in range(len(lv) - 1):
            m = (j == li)[..., None]
            out_img += np.where(m, stack[li] * (1 - w) + stack[li + 1] * w, 0)
        out_img *= (1 - 0.3 * (b / maxblur))[..., None]       # bokeh spreads and dims, it doesn't glow

        # Light pool on the plane: trails the subject (0.4 s average), stretched along the move, key off-axis.
        lag_hist.append(Fd.copy())
        Lc = np.mean(lag_hist[-max(1, int(0.4 * FPS)):], axis=0)
        mv = f1 - f0
        ang = np.arctan2(mv[1], mv[0]) if np.hypot(*mv) > 1 else 0.0
        ra, rc = sc["spill"][0] * base * spread / mag, sc["spill"][1] * base * spread / mag
        ra, rc = ra * (1 + 0.25 * u), rc * (1 + 0.25 * u)     # opens up as the shot goes on
        dx, dy = pu - Lc[0], pv - Lc[1]
        al = (dx * np.cos(ang) + dy * np.sin(ang)) / ra
        ac = (-dx * np.sin(ang) + dy * np.cos(ang)) / rc
        light = 1 - ramp(np.clip(np.hypot(al, ac), 0, 1), SPILL)
        if sc["core"]:
            key = 0.12 * np.array([ra * (1 if flip else -1), -rc])  # hot spot toward the far side, flips with the diagonal
            al2 = (dx - key[0]) / (ra * sc["core"] * 2.2)
            ac2 = (dy - key[1]) / (rc * sc["core"] * 2.2)
            light *= 1 - ramp(np.clip(np.hypot(al2, ac2), 0, 1), CORE)
        frame = out_img * (up(light) * inside * vign)[..., None]
        frame = frame * 0.92 * expo                            # low key: in-focus text ~85-90% white
        frame += rng.normal(0, 3.0, (OH, OW, 1)).astype(np.float32)  # fine film grain
        ff.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    t = load("timeline.json")
    P_ = load("project.json")
    want = set(sys.argv[1:])
    os.makedirs("cine", exist_ok=True)
    cines = [p for p in t["plan"] if p.get("cine")]
    full = (1080, 1920) if layout() == "split" else (W, H)
    for k_, p in enumerate(cines):
        if want and p["cine"] not in want:
            continue
        n = round((p["end"] - p["start"]) * FPS)
        OW, OH = full if p.get("intro") else (W, H)            # split: the cold open fills the whole 9:16 frame
        out = f"cine/{p['cine']}.mp4"
        render(p, n, OW, OH, out, flip=bool(k_ % 2))
        print(f"{out}  {n} frames {OW}x{OH}  {p.get('scale', 'macro')}  src={p['src']}")
