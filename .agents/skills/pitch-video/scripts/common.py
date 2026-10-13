"""Shared helpers for the pitch-video pipeline. Every script runs with cwd = the project's work dir."""
import json, os, subprocess

TB = os.environ.get("PITCH_VIDEO_HOME", os.path.expanduser("~/.cache/pitch-video"))
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
W, H = 1920, 1080


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
