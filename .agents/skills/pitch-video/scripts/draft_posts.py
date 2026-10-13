"""Draft the launch posts from what was actually said in the video → out/posts.md

Pulls the hook, the problem, the proof and the call to action from captions.json + project.json, and writes
platform-shaped drafts: an X thread, a LinkedIn post, a Product Hunt tagline/description/maker comment,
a Reddit post (story-first, link once at the end) and a Show HN title + first comment.
These are drafts for the agent to polish with the user, not copy to paste blind. Rules in posts.md at the top
of the file list what each platform punishes.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import load

P = load("project.json")
caps = load("captions.json")
t = load("timeline.json")
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
lines = [plain(c.get("html", c["text"])) for c in caps]
bold = [re.sub(r"<[^>]+>", "", m) for c in caps for m in re.findall(r"<b>(.*?)</b>", c.get("html", ""))]

scenes = P["scenes"]
def scene_text(i):
    """All narration inside scene i (by matching its start phrase to caption index)."""
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
    starts = []
    for sc in scenes:
        k = next((j for j, l in enumerate(lines) if norm(sc["start"]) in norm(l)), 0)
        starts.append(k)
    a = starts[i]
    b = starts[i + 1] if i + 1 < len(starts) else len(lines)
    return " ".join(lines[a:b]).strip()

name = P.get("product") or (P.get("end") or {}).get("title") or P.get("title", "the product")
links = (P.get("end") or {}).get("links", [])
link = next((l.split()[-1] for l in links if "." in l), "")
repo = next((l for l in links if "github.com" in l), "")
video = P.get("video_url", "")
hook = scene_text(0)
problem = scene_text(1) if len(scenes) > 2 else ""
proof_i = next((i for i, s in enumerate(scenes) if re.search(r"proof|cheat|demo|how it works", s["title"], re.I)), min(2, len(scenes) - 1))
proof = scene_text(proof_i)
dur = f"{int(t['total'] // 60)}:{int(t['total'] % 60):02d}"
tagline = (P.get("tagline") or hook.split(".")[0])[:60]

def clip(s, n):
    s = s.strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"

out = f"""# Launch post drafts: {name}

Drafted from the video's own words. Polish with the user before posting.
- X: upload the video natively (links get throttled); put links in replies, not the first post.
- Product Hunt: never ask for upvotes; ask for feedback.
- Reddit: story first, one link at the end, check each subreddit's self-promo rules and flair.
- Hacker News: plain title, technical first comment, no marketing words.

## X thread
1/ {clip(hook, 240)}

[attach the {dur} video]

2/ {clip(problem or proof, 270)}

3/ {clip(proof, 270)}

4/ {"Try it: " + (link or repo or "<link>")}{chr(10) + "Code: " + repo if repo and repo != link else ""}

## LinkedIn
{clip(problem or hook, 300)}

{clip(proof, 400)}

{"Link: " + (link or repo or "<link>")}

What would you use it for? I read every comment.

## Product Hunt
- Tagline (≤60): {tagline}
- Description (≤260): {clip(hook + " " + proof, 260)}
- Maker comment:
  Hey Product Hunt 👋 {clip(problem or hook, 280)}
  {clip(proof, 400)}
  I'd love to hear where it breaks for you, and what you'd use it for.

## Reddit (story-first)
Title: {clip("I built " + name + ": " + (bold[0] if bold else tagline), 120)}

{clip(problem or hook, 500)}

{clip(proof, 500)}

{"Video: " + video if video else ""}
{"Link: " + (repo or link) if (repo or link) else ""}

What would make this useful for you?

## Show HN
Title: Show HN: {clip(name + " – " + tagline, 80)}
First comment: {clip(problem or hook, 400)} {clip(proof, 500)}
"""
os.makedirs("out", exist_ok=True)
open("out/posts.md", "w").write(out)
print(out)
