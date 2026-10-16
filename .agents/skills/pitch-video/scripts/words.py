"""Step 2c: word-level timing for every caption line → captions.json gets "words": [{text, start, end, b}].

usage: python words.py            (after fix_captions.py and retakes.py; re-run if captions.json text changes)

Short-form captions show 1-3 words at a time, appear 2 frames before the first word and hard-swap on the
next, so each word needs its own onset. Whisper (one word per segment) runs on every caption line's audio;
its words are aligned to the line's corrected text (the script's spelling wins), unmatched words are
interpolated by length, and every onset is nudged onto the nearest rise in voice energy (whisper's word
times wander by ~50-100 ms). Times are SOURCE seconds, like the lines themselves; edit.py maps them.
"""
import difflib, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import TB, load, pcm, run, save

MODEL = os.path.join(TB, "ggml-small.en.bin")
caps = load("captions.json")
os.makedirs("chunks", exist_ok=True)
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
voice = pcm("voice16k.wav", 16000)
SR = 16000
hop = 160  # 10 ms energy frames
env = np.sqrt(np.convolve(voice ** 2, np.ones(320) / 320, "same"))[::hop]


def asr_words(i):
    c = caps[i]
    a, b = max(0, c["start"] - 0.15), c["end"] + 0.15
    w = f"chunks/w{i:03d}.wav"
    run(["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", "voice16k.wav", "-af", "adelay=400:all=1,apad=pad_dur=0.8", w])
    subprocess.run(["whisper-cli", "-m", MODEL, "-f", w, "-oj", "-of", w[:-4], "-t", "2", "-np", "-sow", "-ml", "1"], capture_output=True)
    try:
        segs = json.load(open(w[:-4] + ".json"))["transcription"]
    except Exception:
        return []
    out = []
    for g in segs:
        tx = g["text"].strip()
        if not norm(tx):
            continue
        s, e = g["offsets"]["from"] / 1000 - 0.4 + a, g["offsets"]["to"] / 1000 - 0.4 + a
        out.append((tx, max(c["start"] - 0.1, s), min(c["end"] + 0.1, e)))
    return out


def onset(t, lo, hi):
    """Snap a word start to the steepest energy rise within ±80 ms (never outside the line)."""
    i0, i1 = int(max(lo, t - 0.08) * 100), int(min(hi, t + 0.08) * 100)
    if i1 - i0 < 3 or i1 >= len(env):
        return t
    d = np.diff(np.log(env[i0:i1 + 1] + 1e-4))
    return (i0 + int(np.argmax(d)) + 1) / 100


with ThreadPoolExecutor(4) as ex:
    heard = list(ex.map(asr_words, range(len(caps))))

for c, hw in zip(caps, heard):
    # caption words, with **bold** / <b> emphasis carried per word
    toks, bold = [], False
    for part in re.split(r"(<b>|</b>)", c.get("html", c["text"])):
        if part == "<b>":
            bold = True
        elif part == "</b>":
            bold = False
        else:
            toks += [(w, bold) for w in re.sub(r"<[^>]+>", "", part).split()]
    merged = []
    for w, b in toks:  # punctuation split off by an emphasis tag ("<b>Claude</b>.") belongs to the word before
        if merged and not norm(w):
            merged[-1] = (merged[-1][0] + w, merged[-1][1])
        else:
            merged.append((w, b))
    toks = merged
    if not toks:
        continue
    times = [None] * len(toks)
    sm = difflib.SequenceMatcher(None, [norm(w) for w, _ in toks], [norm(x[0]) for x in hw], autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = hw[blk.b + k][1:]
    for tag, a0, a1, b0, b1 in sm.get_opcodes():  # substitutions (misheard words) take the heard word's time
        if tag == "replace" and a1 - a0 == b1 - b0:
            for k in range(a1 - a0):
                times[a0 + k] = hw[b0 + k][1:]
    # interpolate the rest by character length between known neighbours (line edges as anchors)
    known = [(-1, (c["start"], c["start"]))] + [(k, t) for k, t in enumerate(times) if t] + [(len(toks), (c["end"], c["end"]))]
    for (ka, ta), (kb, tb) in zip(known, known[1:]):
        gap = list(range(ka + 1, kb))
        if not gap:
            continue
        s0, s1 = ta[1], tb[0]
        lens = np.array([max(1, len(norm(toks[k][0]))) for k in gap], float)
        edges = s0 + (s1 - s0) * np.r_[0, np.cumsum(lens)] / lens.sum()
        for j, k in enumerate(gap):
            times[k] = (edges[j], edges[j + 1])
    words, prev = [], c["start"]
    for (w, b), (s, e) in zip(toks, times):
        s = min(max(s, prev, c["start"]), c["end"] - 0.02)
        s = onset(s, max(prev, c["start"]), c["end"])
        e = min(max(e, s + 0.06), c["end"])
        words.append({"text": w, "start": round(s, 3), "end": round(e, 3), "b": b})
        prev = s + 0.02
    c["words"] = words

save("captions.json", caps)
n = sum(len(c.get("words", [])) for c in caps)
matched = sum(1 for c, hw in zip(caps, heard) if hw)
print(f"words.py: {n} words timed across {len(caps)} lines ({matched} lines heard by the word pass)")
for c in caps[:3]:
    print("   ", " ".join(f"{w['text']}@{w['start']:.2f}" for w in c.get("words", [])))
