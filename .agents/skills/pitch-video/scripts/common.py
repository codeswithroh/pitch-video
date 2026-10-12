"""Shared helpers for the pitch-video pipeline. Every script runs with cwd = the project's work dir."""
import json, os, subprocess

TB = os.environ.get("PITCH_VIDEO_HOME", os.path.expanduser("~/.cache/pitch-video"))
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
W, H = 1920, 1080


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
