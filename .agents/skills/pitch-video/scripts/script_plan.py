"""Stage B: turn a cued script into everything the edit needs, BEFORE anyone records.

usage: python script_plan.py script.md [--force]

script.md (the agent writes it with the user; see references/scripts.md):

    ---
    title: Cursor 2.0 in 60 seconds
    layout: split            # split (9:16, visuals top / face bottom) | pitch (16:9, face bubble)
    accent: "#7c5cff"
    url: https://cursor.com  # what film.mjs opens (optional)
    end_title: Cursor 2.0
    end_tagline: Eight agents. <b>One diff.</b>
    end_links: cursor.com, @you
    ---
    ## Hook
    [face]
    Cursor just shipped the feature I have wanted for a **year**.
    [rec site: homepage hero, scroll to the new Agents panel]
    It runs eight agents on your code at the same time.
    ## How it works
    [anim lanes: eight lanes, each a task, merging into one diff]
    ...
    ## Outro
    [end]
    Link is in the comments.

Cues (one per line, they apply from the NEXT spoken line):
    [face]                          full-frame speaker
    [rec <name>: what to show]      screen footage, filmed by film.mjs as shots/<name>/
    [anim <name>: what it explains] motion graphic, anims/<name>.html → render_anim.mjs
    [image <path>]                  still with a slow push-in
    [title TEXT | subtitle]         big statement card
    [card <name>]                   custom card overlay (cards/<name>.html) on the current shot
    [zoom tl|tr|bl|br|c]            push in on the current shot
    [cine <name> <scale>: subject]  cinematic hero shot of real UI (scale: xmacro|macro|medium|wide), see references/cinematic.md
A "## Cold open" section with only [cine ...] cues and no spoken lines becomes the silent cinematic intro.
    [end]                           this scene gets the end card
Everything else that isn't a heading or blank is spoken. **bold** = emphasis (read it with weight; shown in the accent colour).

Writes:
    project.json        scenes and shots anchored to the first words of each spoken line (edit.py resolves them)
    narration.md        spoken lines only, for fix_captions.py
    shotlist.md         every rec/anim to make, the line it covers and roughly how long it is on screen
"""
import json, os, re, sys

WPS = 2.6  # spoken words per second at a natural pace (~155 wpm)

if len(sys.argv) < 2:
    sys.exit(__doc__)
src = open(sys.argv[1]).read()
force = "--force" in sys.argv

# ── front matter ──
meta = {}
m = re.match(r"---\n(.*?)\n---\n", src, re.S)
if m:
    for line in m.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", line)
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    src = src[m.end():]

# ── parse scenes, cues and spoken lines ──
scenes = []  # {title, end_card, items: [("cue", kind, arg, desc) | ("say", text)]}
for raw in src.splitlines():
    line = raw.strip()
    if not line or line.startswith("<!--"):
        continue
    if line.startswith("#"):
        scenes.append({"title": line.lstrip("#").strip(), "end_card": False, "items": []})
        continue
    if not scenes:
        scenes.append({"title": "Intro", "end_card": False, "items": []})
    cue = re.fullmatch(r"\[(\w+)\s*([^\]:|]*)(?:[:|]\s*([^\]]*))?\]", line)
    if cue:
        kind, arg, desc = cue.group(1).lower(), cue.group(2).strip(), (cue.group(3) or "").strip()
        if kind == "end":
            scenes[-1]["end_card"] = True
        else:
            scenes[-1]["items"].append(("cue", kind, arg, desc))
        continue
    scenes[-1]["items"].append(("say", line.lstrip(">").strip()))

plain = lambda s: re.sub(r"\*\*|\*", "", s)
words = lambda s: re.findall(r"[A-Za-z0-9'’]+", plain(s))


def anchor(text, n=4):
    """First few words of a spoken line: edit.py finds the cut there."""
    return " ".join(words(text)[:n])


# ── build project.json scenes ──
out_scenes, shotlist, problems = [], [], []
LENS = {"xmacro": 2.5, "macro": 3.5, "medium": 4.5, "wide": 4.5}


def cine_shot(arg, desc):
    bits = arg.split()
    name = bits[0] if bits else f"cine{len(shotlist)}"
    scale = bits[1] if len(bits) > 1 and bits[1] in LENS else "macro"
    shotlist.append(("cine", name, f"{scale}: {desc}", ""))
    return {"cine": name, "scale": scale, "src": f"stills/{name}.png", "focus": "subject", "len": LENS[scale]}


intro = []
for sc in scenes:
    said = [x[1] for x in sc["items"] if x[0] == "say"]
    if not said and not out_scenes and all(it[1] == "cine" for it in sc["items"] if it[0] == "cue") and sc["items"]:
        intro += [cine_shot(it[2], it[3]) for it in sc["items"]]
        continue
    if not said:
        problems.append(f"scene '{sc['title']}' has no spoken line; merged into the previous scene")
        continue
    shots, pending, last_shot = [], [], None
    items = sc["items"]
    for idx, it in enumerate(items):
        if it[0] == "cue":
            pending.append(it)
            continue
        text = it[1]
        if not pending:
            continue
        shot = {}
        for _, kind, arg, desc in pending:
            if kind == "face":
                shot["speaker"] = True
            elif kind == "rec":
                shot.update({"rec": arg or "main", "t": 0})
                shotlist.append(("rec", arg or "main", desc, text))
            elif kind == "anim":
                shot["anim"] = arg or f"anim{len(shotlist)}"
                shotlist.append(("anim", shot["anim"], desc, text))
            elif kind == "image":
                shot["image"] = arg
            elif kind == "cine":
                c = cine_shot(arg, desc)
                c.pop("len")
                shot.update(c)
            elif kind == "title":
                shot["title"] = arg
                if desc:
                    shot["subtitle"] = desc
            elif kind == "card":
                (shot if shot else (last_shot or shot))["card"] = arg
            elif kind == "zoom":
                (shot if shot else (last_shot or shot))["zoom"] = arg or "c"
            else:
                problems.append(f"unknown cue [{kind}] in '{sc['title']}'")
        pending = []
        if any(k in shot for k in ("speaker", "rec", "anim", "image", "title", "cine")):
            if shots:
                shot["from"] = anchor(text)
            shots.append(shot)
            last_shot = shot
        elif last_shot is None and shot:
            shots.append({"speaker": True, **shot})
            last_shot = shots[-1]
    if not shots:
        # no visual cue: the end scene shows a dark canvas under the end card, anything else stays on the face
        shots = [{"black": True}] if sc["end_card"] else [{"speaker": True}]
    if pending:
        problems.append(f"cue(s) after the last spoken line of '{sc['title']}' were ignored: {[p[1] for p in pending]}")
    o = {"title": sc["title"], "start": anchor(said[0]), "shots": shots}
    if sc["end_card"]:
        o["end_card"] = True
    out_scenes.append(o)

# split layout: footage-free shots would leave the top half dark, so warn
layout = meta.get("layout", "split")
spoken = [x[1] for sc in scenes for x in sc["items"] if x[0] == "say"]
nwords = sum(len(words(s)) for s in spoken)
speed = float(meta.get("speed", 1.0 if meta.get("layout", "split") == "split" else 1.1))
est = nwords / WPS / speed + sum(c["len"] for c in intro)

project = {
    "title": meta.get("title", out_scenes[0]["title"] if out_scenes else "Video"),
    "layout": layout,
    **({"speed": speed} if "speed" in meta or layout != "split" else {}),
    "output": meta.get("output", "out/video.mp4"),
    "theme": {"accent": meta.get("accent", "#ffe040"), "head": meta.get("font", "Inter"), "body": meta.get("font", "Inter")},
    "music": meta.get("music", "synth"),
    "end": {"title": meta.get("end_title", meta.get("title", "")), "tagline": meta.get("end_tagline", ""),
            "links": [l.strip() for l in meta.get("end_links", "").split(",") if l.strip()], "by": meta.get("end_by", "")},
    "scenes": out_scenes,
    "sfx": [],
}
if meta.get("url"):
    project["url"] = meta["url"]
if intro:
    project["intro"] = {"shots": intro}

if os.path.exists("project.json") and not force:
    json.dump(project, open("project.from_script.json", "w"), indent=1)
    print("project.json exists: wrote project.from_script.json (re-run with --force to overwrite)")
else:
    json.dump(project, open("project.json", "w"), indent=1)
    print("wrote project.json")

# ── narration.md (for fix_captions.py) ──
open("narration.md", "w").write("\n".join("> " + s for s in spoken) + "\n")

# ── shotlist.md ──
sl = [f"# Shot list: {project['title']}", "",
      f"Layout: **{layout}** ({'film and animate at 1080x960, the top half of a 9:16 frame' if layout == 'split' else '1920x1080'}).",
      "rec shots: film them in film.mjs as shots/<name>/, log ev() times, then set each shot's \"t\"/\"to\" in project.json.",
      "anim shots: write anims/<name>.html (window.seek(t), keyed to window.CUES), then node render_anim.mjs <name>.", ""]
for kind, name, desc, text in shotlist:
    secs = len(words(text)) / WPS / speed
    if kind == "cine":
        sl.append(f"- **cine `{name}`** {desc}\n  capture: stills/{name}.png (+ .json with a \"subject\" target) via still() in film.mjs, then python cine.py")
        continue
    sl.append(f"- **{kind} `{name}`** ({secs:.0f}s+): {desc or '(describe it)'}\n  covers: \"{plain(text)}\"")
open("shotlist.md", "w").write("\n".join(sl) + "\n")

# ── report ──
print(f"{len(out_scenes)} scenes, {sum(len(s['shots']) for s in out_scenes)} shots, {nwords} words ≈ {est:.0f}s after the {speed}x speed-up")
print("wrote narration.md, shotlist.md")
if layout == "split":
    face_only = sum(1 for s in out_scenes for sh in s["shots"] if sh.get("speaker"))
    if face_only > max(2, len(out_scenes) // 2):
        problems.append(f"{face_only} full-face shots: in split layout the top half should keep changing; add rec/anim cues")
for p in problems:
    print("WARN:", p)
