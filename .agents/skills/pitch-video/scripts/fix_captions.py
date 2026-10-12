"""Step 2: turn captions_raw.json into captions.json.

usage: python fix_captions.py [script.md|script.txt]
With a script: word-aligns the transcript to the script and replaces each line's text with the script's words
(fixes mishearings like "face-off"→"face up", "Virev"→"VRF"), carrying **bold** from the script into <b> emphasis.
In markdown, only "> " blockquote lines are treated as narration when any exist.
Without a script: copies the raw text. Either way, READ the printed result and hand-fix anything still wrong
(and any "(?)" lines) directly in captions.json: fields start/end/text/html.
"""
import difflib, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import load, save

raw = load("captions_raw.json")
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())

if len(sys.argv) < 2:
    for c in raw:
        c["html"] = c["text"]
    save("captions.json", raw)
    sys.exit(print(f"captions.json: {len(raw)} lines copied without a script"))

src = open(sys.argv[1]).read()
quotes = [l[1:].strip() for l in src.splitlines() if l.startswith(">")]
text = "\n".join(quotes) if quotes else re.sub(r"^#.*$", "", src, flags=re.M)
# Script words with a bold flag.
sw = []
for k, part in enumerate(re.split(r"\*\*", text)):
    for w in re.split(r"\s+", part.replace("*", "").replace("—", " — ").replace("…", "… ")):
        if w and w not in ("—", "-", "–"):
            sw.append((w, k % 2 == 1))
# Transcript words, remembering which caption each belongs to.
rw, owner = [], []
for ci, c in enumerate(raw):
    for w in c["text"].split():
        rw.append(w)
        owner.append(ci)

# Expand hyphen/compound differences ("on-chain" vs "onchain") by comparing normalized, de-hyphenated tokens.
A = [norm(w) for w in rw]
B = [norm(w) for w, _ in sw]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
mp = [0] * (len(A) + 1)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    for i in range(i1, i2 + 1):
        mp[i] = j1 + round((i - i1) * (j2 - j1) / max(1, i2 - i1))
mp[len(A)] = len(B)
ratio = sm.ratio()

out = []
j = 0
for ci, c in enumerate(raw):
    idx = [k for k, o in enumerate(owner) if o == ci]
    if not idx:
        out.append({**c, "html": c["text"]})
        continue
    end = mp[idx[-1] + 1] if ci + 1 < len(raw) else len(B)
    words = sw[j:max(end, j)]
    j = max(end, j)
    html, bold = [], False
    for w, b in words:
        if b and not bold:
            html.append("<b>")
        if not b and bold:
            html[-1] += "</b>"
        html.append(w + " ")
        bold = b
    s = "".join(html).strip().replace(" </b>", "</b> ").replace("</b> .", "</b>.").replace("</b> ,", "</b>,").strip()
    if bold:
        s += "</b>"
    s = s.replace("<b> ", "<b>")
    plain = re.sub("<[^>]+>", "", s)
    out.append({**c, "text": plain or c["text"], "html": s or c["text"]})
# A line can end up with no words (e.g. heard "No." where the script said "null" at a different spot):
# move the previous line's last word onto it so every caption has text.
for i in range(1, len(out)):
    if not re.search(r"[A-Za-z0-9]", out[i]["text"]):
        prev = out[i - 1]["html"].rsplit(" ", 1)
        if len(prev) == 2:
            out[i - 1]["html"], moved = prev[0], prev[1]
            out[i - 1]["text"] = re.sub("<[^>]+>", "", out[i - 1]["html"])
            if moved.startswith("<b>") and not moved.endswith("</b>"):
                moved += "</b>"
            out[i]["html"] = moved.rstrip(".,") + "."
            out[i]["text"] = re.sub("<[^>]+>", "", out[i]["html"])
save("captions.json", out)
print(f"aligned to script (similarity {ratio:.2f}); review these:")
for i, (r, c) in enumerate(zip(raw, out)):
    mark = "  " if norm(r["text"]) == norm(c["text"]) else "≠ "
    print(f"{mark}[{i:02d}] {c['start']:7.2f}  {c['html']}" + (f"      (heard: {r['text']})" if mark != "  " else ""))
