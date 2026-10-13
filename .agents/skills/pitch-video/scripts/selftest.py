"""Pipeline sync self-test: proves the cut + speed-up + audio chain + mux keep picture and sound together,
before any real footage is judged. (Suggested by u/vincent_sch on r/ClaudeCode.)

Builds a synthetic "talking head": black frames with a white FLASH and a 1 kHz CLICK on the same frame, at
known times near the start and the end. Runs it through the real cut_speaker.py (frame/sample-exact cuts and
the atempo speed-up), the real final mix from common.audio_graph (voice chain, loudnorm, sidechain, limiter)
and the same separate-pass encode + AAC mux as compose.py. Then decodes the finished mp4 and checks:
  - every flash and its click still land together (A/V offset per event),
  - the offset at the end matches the offset at the start (no drift),
  - each event lands where the cut list says it should (timing).
The real-footage lip-sync check can't separate pipeline drift from face-tracker noise; this can.

usage: python selftest.py        (exit 0 = PASS, 1 = FAIL; verify.py runs it as check [0])
"""
import json, os, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import FPS, audio_graph, pcm, probe

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = 40.0
KEEP = [[0.0, 8.0], [10.0, 18.5], [21.0, 30.0], [32.0, 40.0]]  # cuts like a real take with pauses removed
EVENTS = [2.0, 6.0, 12.0, 16.0, 24.0, 28.0, 34.0, 38.0]         # source times, all well inside kept spans
SPEED = 1.15
TOL_AV = 0.040   # flash vs click, seconds (one frame is 33 ms; frame rounding alone gives up to ±17 ms)
TOL_DRIFT = 0.020
TOL_POS = 0.050


def ff(args, cwd):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], cwd=cwd, check=True)


def expected(ts):
    out = 0.0
    for a, b in KEEP:
        if a <= ts < b:
            return (out + ts - a) / SPEED
        out += b - a
    raise ValueError(ts)


def flashes(path):
    W, H = 64, 36
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-vf", f"scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    lum = np.frombuffer(raw, np.uint8).reshape(-1, H * W).mean(1)
    on = lum > 128
    starts = np.flatnonzero(on & ~np.r_[False, on[:-1]])
    pts = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=pts_time",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.split()
    t = np.array([float(x.strip(",")) for x in pts if x.strip(",") not in ("", "N/A")])
    return [float(t[i]) if i < len(t) else i / FPS for i in starts]


def clicks(path):
    # energy at 1 kHz only: loudnorm lifts the room tone in long gaps, so broadband onsets give false clicks
    x = pcm(path, SR)
    k = np.hanning(240) * np.exp(-2j * np.pi * 1000 * np.arange(240) / SR)
    env = np.abs(np.convolve(x, k, "same"))
    on = env > 0.25 * env.max()
    idx = np.flatnonzero(on & ~np.r_[False, on[:-1]])
    keep = [i for k, i in enumerate(idx) if k == 0 or i - idx[k - 1] > SR * 0.3]
    st = next(s for s in probe(path)["streams"] if s["codec_type"] == "audio")
    start = float(st.get("start_time") or 0)  # raw decode ignores start_time; add it back so both clocks match
    return [i / SR + start for i in keep]


def run_selftest(verbose=True):
    log = print if verbose else (lambda *a, **k: None)
    with tempfile.TemporaryDirectory(prefix="pv_selftest_") as d:
        # 1. synthetic source: 30 fps CFR video + 48 kHz PCM, flash and click on the same frame/sample
        frames = [round(e * FPS) for e in EVENTS]
        lit = "+".join(f"between(N,{f},{f + 2})" for f in frames)
        a = np.zeros(int(DUR * SR), np.float32)
        tone = 0.8 * np.sin(2 * np.pi * 1000 * np.arange(int(0.03 * SR)) / SR)
        for f in frames:
            s = f * (SR // FPS)
            a[s:s + len(tone)] = tone
        a += 0.002 * np.random.default_rng(0).standard_normal(len(a)).astype(np.float32)  # room tone, so loudnorm behaves
        (a * 32767).astype("<i2").tofile(os.path.join(d, "src.raw"))
        ff(["-f", "lavfi", "-i", f"color=c=black:s=640x360:r={FPS}:d={DUR}",
            "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "src.raw",
            "-vf", f"format=yuv420p,geq=lum='if({lit},235,16)':cb=128:cr=128", "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-shortest", "source.mov"], d)
        # 2. the real cut + speed-up
        total = sum(b - a_ for a_, b in KEEP) / SPEED
        json.dump({"keep": KEEP, "speed": SPEED, "total": total}, open(os.path.join(d, "timeline.json"), "w"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "cut_speaker.py")], cwd=d, capture_output=True, text=True)
        if r.returncode:
            log("[0] self-test: cut_speaker.py failed:", (r.stderr or r.stdout).strip()[-300:])
            return False
        # 3. the real final mix (silent music/sfx beds) + separate picture/sound passes + AAC mux, as compose.py
        for n in ("music.wav", "sfx.wav"):
            ff(["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-t", f"{total:.4f}", n], d)
        ff(["-i", "speaker_cut.mov", "-an", "-frames:v", str(round(total * FPS)), "-c:v", "libx264",
            "-preset", "ultrafast", "-crf", "18", "-r", str(FPS), "_video.mp4"], d)
        ff(["-i", "speaker_cut.mov", "-i", "music.wav", "-i", "sfx.wav", "-filter_complex", audio_graph(),
            "-map", "[aout]", "-t", f"{total:.4f}", "-c:a", "pcm_s16le", "-ar", str(SR), "_audio.wav"], d)
        ff(["-i", "_video.mp4", "-i", "_audio.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
            "-b:a", "192k", "-ar", str(SR), "-movflags", "+faststart", "out.mp4"], d)
        # 4. measure on the finished file
        out = os.path.join(d, "out.mp4")
        fl, cl = flashes(out), clicks(out)
    exp = [expected(e) for e in EVENTS]
    if len(fl) != len(EVENTS) or len(cl) != len(EVENTS):
        log(f"[0] self-test FAIL: expected {len(EVENTS)} events, found {len(fl)} flashes and {len(cl)} clicks")
        return False
    av = [c - f for f, c in zip(fl, cl)]
    pos = [f - e for f, e in zip(fl, exp)]
    # After the speed-up an event can only show on the nearest frame, so each offset jitters by up to half a
    # frame (±17 ms). Drift is the TREND across all events, not last minus first.
    drift = float(np.polyfit(fl, av, 1)[0] * (fl[-1] - fl[0]))
    log(f"[0] pipeline self-test: A/V offset per event (ms, + = sound later) {[round(x * 1000) for x in av]}")
    log(f"    drift trend start->end {drift * 1000:+.0f} ms; worst timing error vs cut list {max(map(abs, pos)) * 1000:.0f} ms")
    ok = max(map(abs, av)) <= TOL_AV and abs(drift) <= TOL_DRIFT and max(map(abs, pos)) <= TOL_POS
    if not ok:
        log("    self-test FAIL: the pipeline itself moves sound against picture; fix this before judging real footage")
    return ok


if __name__ == "__main__":
    ok = run_selftest()
    print("\nSELF-TEST:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
