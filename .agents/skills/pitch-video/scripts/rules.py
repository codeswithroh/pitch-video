"""Rules memory: notes on one video become rules for every future video.

Rules live in ~/.pitch-video/rules.md (global) and, optionally, ./rules.md in the work dir (this project only).
Each rule is one line: "- [id] [scope] rule text  (from: note, date)". The agent reads them before planning.

usage:
  python rules.py show                     # print every active rule (global + project)
  python rules.py note "too fast at 0:42"  # log a note on the current video (notes.md in the work dir)
  python rules.py add "Hold 1.5s on every title card" [--project] [--from "note text"]
  python rules.py retire 7                 # retire rule 7 (kept in the file, marked ~~retired~~)
  python rules.py apply                    # print the project.json overrides the rules imply (for edit.py)

Conflict handling: a new rule that matches the topic of an older one (same key, see KEYS) retires the older one
automatically and says so, so rule 89 never silently fights rule 12.
"""
import datetime, json, os, re, sys

GLOBAL = os.path.expanduser("~/.pitch-video/rules.md")
LOCAL = "rules.md"
NOTES = "notes.md"
HEADER = "# Pitch Video rules\n\nRead before every edit. One rule per line. Newer rules on the same topic retire older ones.\n\n"

# Topic keys: rules on the same key conflict. Each maps to a project.json override when it carries a number.
KEYS = {
    "speed": (r"\b(speed|pace|faster|slower)\b", r"(\d+(?:\.\d+)?)\s*x", lambda v: {"speed": float(v)}),
    "pause": (r"\b(pause|breath|gap)s?\b", r"(\d+(?:\.\d+)?)\s*s", lambda v: {"pause": {"long": float(v)}}),
    "title_hold": (r"\btitle", r"(\d+(?:\.\d+)?)\s*s", lambda v: {"title_hold": float(v)}),
    "music": (r"\bmusic\b", r"\b(none|off|quiet|louder)\b", lambda v: {"music": "none"} if v in ("none", "off") else {"music_gain": 0.35 if v == "quiet" else 0.75}),
    "sfx": (r"\b(sfx|sound effects?|whoosh|boom)\b", r"\b(none|off|fewer|less)\b", lambda v: {"sfx_auto": {"whoosh": False, "hook": False}} if v in ("none", "off") else {"sfx_gain": 0.5}),
    "captions": (r"\bcaptions?\b", None, None),
    "accent": (r"\b(accent|colou?r)\b", r"(#[0-9a-fA-F]{6})", lambda v: {"theme": {"accent": v}}),
    "pip": (r"\b(face bubble|pip|bubble)\b", None, None),
    "vertical": (r"\b(vertical|9:16|shorts|reels)\b", None, None),
}


def path(project):
    p = LOCAL if project else GLOBAL
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    if not os.path.exists(p):
        open(p, "w").write(HEADER)
    return p


def parse(p):
    out = []
    if not os.path.exists(p):
        return out
    for line in open(p):
        m = re.match(r"- \[(\d+)\] \[([a-z_]+)\] (~~)?(.+?)(~~)?(  \(from: .*\))?$", line.rstrip())
        if m:
            out.append({"id": int(m[1]), "key": m[2], "retired": bool(m[3]), "text": m[4], "meta": m[6] or "", "file": p})
    return out


def all_rules():
    return parse(GLOBAL) + parse(LOCAL)


def key_of(text):
    t = text.lower()
    for k, (pat, _, _) in KEYS.items():
        if re.search(pat, t):
            return k
    return "general"


def write(p, rules):
    body = HEADER + "".join(
        f"- [{r['id']}] [{r['key']}] {'~~' if r['retired'] else ''}{r['text']}{'~~' if r['retired'] else ''}{r['meta']}\n" for r in rules)
    open(p, "w").write(body)


def add(text, project=False, source=""):
    p = path(project)
    rules = parse(p)
    nid = max([r["id"] for r in all_rules()] + [0]) + 1
    k = key_of(text)
    for r in rules:
        if not r["retired"] and r["key"] == k and k != "general":
            r["retired"] = True
            print(f"retired [{r['id']}] (same topic '{k}'): {r['text']}")
    meta = f"  (from: {source or 'manual'}, {datetime.date.today()})"
    rules.append({"id": nid, "key": k, "retired": False, "text": text, "meta": meta})
    write(p, rules)
    print(f"added [{nid}] [{k}] {text}  -> {p}")


def apply():
    over = {}
    for r in all_rules():
        if r["retired"]:
            continue
        pat, num, fn = KEYS.get(r["key"], (None, None, None))
        if num and fn:
            m = re.search(num, r["text"], re.I)
            if m:
                v = fn(m[1].lower() if not m[1][0].isdigit() and m[1][0] != "#" else m[1])
                for kk, vv in v.items():
                    if isinstance(vv, dict):
                        over.setdefault(kk, {}).update(vv)
                    else:
                        over[kk] = vv
    return over


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "show":
        rs = [r for r in all_rules() if not r["retired"]]
        print(f"{len(rs)} active rules" + ("" if rs else " (none yet)"))
        for r in rs:
            print(f"  [{r['id']}] [{r['key']}] {r['text']}" + ("  (project)" if r["file"] == LOCAL else ""))
    elif a[0] == "note":
        open(NOTES, "a").write(f"- {datetime.datetime.now():%Y-%m-%d %H:%M} {' '.join(a[1:])}\n")
        print("noted. If it should apply to every future video, run: rules.py add \"<rule>\" --from \"<note>\"")
    elif a[0] == "add":
        project = "--project" in a
        src = a[a.index("--from") + 1] if "--from" in a else ""
        text = " ".join(x for i, x in enumerate(a[1:], 1) if x not in ("--project", "--from") and (i < 2 or a[i - 1] != "--from"))
        add(text, project, src)
    elif a[0] == "retire":
        rid = int(a[1])
        for p in (GLOBAL, LOCAL):
            rs = parse(p)
            if any(r["id"] == rid for r in rs):
                for r in rs:
                    if r["id"] == rid:
                        r["retired"] = True
                write(p, rs)
                print(f"retired [{rid}]")
    elif a[0] == "apply":
        print(json.dumps(apply(), indent=1))
