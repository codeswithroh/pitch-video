"""Step 2b: drop stumbled attempts when the speaker repeated a line.

usage: python retakes.py            # list suspected retakes in captions.json
       python retakes.py --apply    # remove them (captions.json.bak keeps the original)

A retake is a caption line followed, within a few lines, by a line that starts the same way (a reader who
stumbles pauses and repeats the whole sentence). The EARLIER attempt is dropped and the later one kept.
Dropping a caption is enough: edit.py builds the kept audio from caption lines, so the bad attempt falls
into a pause and gets trimmed with it. Always read the list before --apply; re-run edit.py after.
"""
import difflib, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import load, save

caps = load("captions.json")
w = lambda s: re.findall(r"[a-z0-9']+", re.sub(r"<[^>]+>", "", s.lower()))
drop = []
for i, c in enumerate(caps):
    a = w(c["text"])
    if len(a) < 2:
        continue
    for j in range(i + 1, min(i + 4, len(caps))):
        b = w(caps[j]["text"])
        n = min(len(a), len(b), 6)
        if n < 2:
            continue
        head = difflib.SequenceMatcher(None, a[:n], b[:n]).ratio()
        whole = difflib.SequenceMatcher(None, a, b[:len(a)]).ratio()
        # same opening words, and the earlier line isn't just a short common phrase repeated later on purpose
        if head >= 0.8 and whole >= 0.6 and caps[j]["start"] - c["end"] < 12:
            drop.append((i, j, head))
            break

if not drop:
    sys.exit(print("no retakes found"))
for i, j, r in drop:
    print(f"[{i:02d}] {caps[i]['start']:7.2f}s  DROP  {caps[i]['text']}")
    print(f"[{j:02d}] {caps[j]['start']:7.2f}s  keep  {caps[j]['text']}   (match {r:.2f})")
if "--apply" in sys.argv:
    shutil.copy("captions.json", "captions.json.bak")
    gone = {i for i, _, _ in drop}
    save("captions.json", [c for k, c in enumerate(caps) if k not in gone])
    print(f"removed {len(gone)} line(s); now re-run edit.py")
else:
    print("\nlooks right? run: retakes.py --apply")
