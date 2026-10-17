"""Shared helpers for the pitch-video pipeline. Every script runs with cwd = the project's work dir."""
import json, os, subprocess

TB = os.environ.get("PITCH_VIDEO_HOME", os.path.expanduser("~/.cache/pitch-video"))
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30


def layout():
    """'pitch' (16:9, face bubble) or 'split' (9:16: visuals on the top half, the speaker on the bottom half)."""
    try:
        return json.load(open("project.json")).get("layout", "pitch")
    except (OSError, ValueError):
        return "pitch"


# The visual canvas: what build_bg.py renders and what footage, animations and cards are designed for.
# In split layout it is the top half of a 1080x1920 frame; the speaker fills the bottom half.
W, H = (1080, 960) if layout() == "split" else (1920, 1080)


# Voice chain shared by compose.py, verify.py and selftest.py: de-rumble, de-mud, presence, compress,
# loudness-normalize, then BACK TO 48 kHz (loudnorm emits 192 kHz; mixing that unconverted broke lip sync once).
VOICE = ("aresample=48000,highpass=f=85,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=4,"
         "acompressor=threshold=-28dB:ratio=4:attack=4:release=140:makeup=6,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000")


def audio_graph(music_gain=0.55, sfx_gain=0.85):
    """The final mix. Inputs: [0:a] speaker_cut, [1:a] music, [2:a] sfx. Output: [aout]."""
    return ";".join([
        f"[0:a]{VOICE},pan=stereo|c0=c0|c1=c0,asplit=2[voice][key]",
        f"[1:a]aresample=48000,volume={music_gain}[mus]",
        "[mus][key]sidechaincompress=threshold=0.02:ratio=12:attack=15:release=450:makeup=1[musd]",
        f"[2:a]aresample=48000,volume={sfx_gain}[fx]",
        "[voice][musd][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95:level=false,aresample=48000[aout]",
    ])


def music_gain(P):
    """Music bed gain: project.json pins it, else sfx.py's measured level (mix.json), else the old default."""
    if "music_gain" in P:
        return P["music_gain"]
    try:
        return json.load(open("mix.json"))["music_gain"]
    except (OSError, ValueError, KeyError):
        return 0.55


def caption_items(t):
    """The captions to draw: 1-3 word chunks when the timeline has them, otherwise whole lines."""
    if (t.get("captions") or {}).get("mode") == "words" and t.get("chunks"):
        return t["chunks"], True
    return t["caps"], False


def alpha_track(name, items, total, size, d="ov"):
    """Bake timed transparent PNGs [(start, end, png)] into one qtrle alpha track <d>/<name>.mov.
    Via the concat demuxer: feeding dozens of looped PNGs into one filter graph is 10-50x slower."""
    blank = os.path.abspath(f"{d}/blank_{size[0]}x{size[1]}.png")
    if not os.path.exists(blank):
        run(["-f", "lavfi", "-i", f"color=c=black@0.0:s={size[0]}x{size[1]},format=rgba", "-frames:v", "1", blank])
    lines, cur = [], 0.0
    for a, b, png in sorted(items):
        a, b = max(a, cur), min(b, total)
        if b <= a:
            continue
        if a > cur:
            lines += [f"file '{blank}'", f"duration {a - cur:.4f}"]
        lines += [f"file '{os.path.abspath(png)}'", f"duration {b - a:.4f}"]
        cur = b
    if cur < total:
        lines += [f"file '{blank}'", f"duration {total - cur:.4f}"]
    lines.append(f"file '{blank}'")
    open(f"{d}/{name}.txt", "w").write("\n".join(lines) + "\n")
    run(["-f", "concat", "-safe", "0", "-i", f"{d}/{name}.txt", "-vf", f"fps={FPS},format=rgba", "-t", f"{total:.4f}",
         "-c:v", "qtrle", f"{d}/{name}.mov"])
    return f"{d}/{name}.mov"


def find_clap(path, search=15.0):
    """A sync clap near the start: the sound of the clap and the frame where the hands meet.

    Returns (audio_t, picture_t, info) in seconds on the file's own clock, or None if there's no clear clap.
    Sound: the sharpest broadband transient in the first `search` seconds, at least 35 dB above the 200 ms before
    it and decaying within 150 ms (a word doesn't do that). Picture: frame-to-frame motion around it peaks as the
    hands swing in and collapses when they meet; contact = the last fast frame before the collapse.
    A physical event both camera and mic recorded, so it beats any estimate from mouth movement."""
    import numpy as np
    x = pcm(path, 48000, 0, search)
    if len(x) < 48000:
        return None
    hp = x - np.convolve(x, np.ones(24) / 24, "same")          # claps are broadband; voice energy sits low
    e = 20 * np.log10(np.sqrt(np.convolve(hp ** 2, np.ones(48) / 48, "same"))[::48] + 1e-9)  # 1 ms frames
    best = None
    for i in np.argsort(e)[::-1][:400]:
        if i < 200 or i + 150 >= len(e):
            continue
        rise = e[i] - np.median(e[i - 200:i - 20])
        decay = e[i] - e[i + 150]
        if rise >= 35 and decay >= 20:
            best = (i, rise, decay)
            break
    if not best:
        return None
    ta = best[0] / 1000
    W, H = 160, 90
    a0 = max(0.0, ta - 0.8)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{a0:.3f}", "-t", "1.6", "-i", path, "-vf", f"fps={FPS},scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8)[: len(raw) // (W * H) * W * H].reshape(-1, H, W).astype(np.float32)
    if len(fr) < 10:
        return None
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))                # d[k]: motion from frame k to k+1
    moving = d[d > 0.05]
    if len(moving) < 0.7 * len(d):
        return None                                              # repeated frames (a choppy camera): the picture can't time a clap
    base = float(np.median(moving))
    pk = int(np.argmax(d))
    if base < 0.2 or d[pk] < 2.5 * base:
        return None                                              # no hand movement big enough to be the clap
    k = pk
    while k + 1 < len(d) and d[k + 1] >= 0.5 * d[pk]:
        k += 1
    tv = a0 + (k + 1) / FPS                                      # the frame the fast motion arrives at = hands meet
    if abs(ta - tv) > 0.5:
        return None
    return ta, tv, {"rise_db": round(float(best[1])), "motion_x": round(float(d[pk] / base), 1)}


def lip_lag(path, start=0.0, dur=None):
    """Mouth opening (face landmarks) vs voice energy on one file. Returns (lag_ms, r, face_share).
    lag_ms: + = picture later than sound. r: correlation at the best lag (talking heads ~0.2-0.5; < 0.1 = no signal)."""
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(TB, "face_landmarker.task")), running_mode=vision.RunningMode.VIDEO))
    Wd, Hd = 480, 320
    cut = ["-ss", str(start)] + (["-t", str(dur)] if dur else [])
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", *cut, "-i", path, "-vf", f"fps={FPS},scale={Wd}:{Hd},format=rgb24",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, Hd, Wd, 3)
    op = np.full(len(fr), np.nan)
    for i in range(len(fr)):
        r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr[i])), int(i * 1000 / FPS))
        if r.face_landmarks:
            p = r.face_landmarks[0]
            op[i] = np.hypot(p[13].x - p[14].x, (p[13].y - p[14].y) * Hd / Wd) / (np.hypot(p[10].x - p[152].x, (p[10].y - p[152].y) * Hd / Wd) + 1e-6)
    x = pcm(path, 48000, start, dur)
    k = len(x) // 1600
    rms = np.log(np.sqrt((x[:k * 1600].reshape(k, 1600) ** 2).mean(1)) + 1e-4)
    m = min(len(op), len(rms))
    if m < FPS or np.isnan(op[:m]).all():
        return 0, 0.0, 0.0
    o = np.nan_to_num(op[:m], nan=np.nanmean(op[:m]))
    r_ = rms[:m]
    o, r_ = (o - o.mean()) / (o.std() + 1e-9), (r_ - r_.mean()) / (r_.std() + 1e-9)
    sc = {L: np.dot(o[max(0, L):m + min(0, L)], r_[max(0, -L):m - max(0, L)]) / m for L in range(-15, 16)}
    L = max(sc, key=sc.get)
    return round(L * 1000 / FPS), float(sc[L]), float(np.mean(~np.isnan(op[:m])))


def run(args, **kw):
    return subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True, **kw)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def snap(t):
    """Snap a time to the 30 fps frame grid. Every cut lands on a frame so audio and video lengths agree exactly."""
    return round(round(t * FPS) / FPS, 4)


def load(name, default=None):
    if default is not None and not os.path.exists(name):
        return default
    return json.load(open(name))


def save(name, obj):
    json.dump(obj, open(name, "w"), indent=1)


def pcm(path, sr=8000, start=None, dur=None):
    """Decode mono float32 audio. NOTE: raw decode ignores stream start_time, so only use it on files prep.py made."""
    import numpy as np
    a = ["ffmpeg", "-loglevel", "error"]
    if start is not None:
        a += ["-ss", str(start)]
    a += ["-i", path]
    if dur is not None:
        a += ["-t", str(dur)]
    raw = subprocess.run(a + ["-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
