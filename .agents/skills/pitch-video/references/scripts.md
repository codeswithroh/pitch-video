# Stage B: writing the script they'll read

The script is written for one take, and it already contains the edit: every visual
is a cue in the script, anchored to the line it appears on. `script_plan.py` turns it into `project.json`,
so after they record, the video assembles without guessing.

## Length

~155 spoken words per minute, then the 1.1x speed-up.

| Target | Words |
|---|---|
| 30 s | 75–85 |
| 45 s | 110–125 |
| 60 s | 150–165 |
| 90 s | 225–245 |
| 2 min | 300–330 |

## Before writing: the first 3 seconds

Answer "in the first 3 seconds, is someone convinced they need to watch until the end?" Draft three different
openings (problem first, result glimpse, recognition first) that lead into the same body, pick one, and write
down why: the benefit, the open question, what's on screen by second three, and where it pays off. Script the hook
before recording; a take with no hook caps the edit no matter how well it's cut. See `references/house-style.md`.

## Writing rules

- **First line is the hook.** A specific claim or a number, said in under 3 seconds. Not "Hey guys", not their name.
- **Write for the mouth.** Short sentences. One idea per line. Contractions. Words they would actually say; read it aloud in their voice before handing it over.
- **Every line earns its visual.** In split layout the top half must change every 3–6 seconds: put a cue before almost every line. In pitch layout, every scene needs at least one product shot.
- **Show, then say.** Never claim something the top half can't show (a feature you can't film, a number with no source).
- **Bold 1–3 words per scene** (`**like this**`): they read them with weight and they turn accent-coloured in the captions.
- **Names and jargon spelled the way they're said** stay consistent with the product's own spelling; fix_captions.py corrects the transcript to the script.
- **One call to action**, at the end, matching their goal.
- No em dashes, no "game-changer", "revolutionary", "in today's fast-paced world", "let's dive in".
- Third-party products: describe what you saw, don't invent features. Film the real site. Say "here's what I found", not marketing copy.

## Format (script.md)

```
---
title: Cursor 2.0 in 60 seconds
layout: split            # split | pitch
accent: "#7c5cff"        # pull from the product's brand when it's about a product
url: https://cursor.com  # what film.mjs opens
end_title: Cursor 2.0
end_tagline: Eight agents. <b>One diff.</b>
end_links: cursor.com, @handle
---
## Hook
[face]
Cursor just shipped the feature I have wanted for a **year**.
[rec site: homepage hero, scroll to the new Agents panel]
It runs eight agents on your code at the same time.

## How it works
[anim lanes: eight lanes, each a task, merging into one diff]
Each agent gets its own copy of the repo, so they never step on each other.
[title ONE DIFF. | you review once]
When they finish, you review one clean diff.

## Outro
[end]
Link is in the comments. Try it on your messiest repo.
```

Cues go on their own line and apply from the next spoken line:
`[face]` · `[rec <name>: what to film]` · `[anim <name>: what it explains]` · `[cine <name> <scale>: subject]` · `[image <path>]` · `[title TEXT | subtitle]` · `[card <name>]` · `[zoom tl|tr|bl|br|c]` · `[end]`

For 16:9 walkthroughs and launch films, open with a silent cinematic cold open (see `references/cinematic.md`).
For reels, don't: speech must start in the first frames, so put the `[cine ...]` cues on the hook's lines instead
and they play on the top half under your voice.
```
## Cold open
[cine composer macro: the prompt box with a half-typed request]
[cine run xmacro: the Run button]
[cine result wide: the whole window with the finished result]
```

Shape that works for split videos: open on `[face]` for the hook (trust), cut to the product by the second line, keep the top half moving, end on `[end]` with one action.

## Hand-off

1. Show them the script as plain text (no cues) plus a one-line summary of what will be on screen.
2. Revise until they'd say it the same way out loud.
3. Run `$PY $S/script_plan.py script.md`. It writes `project.json`, `narration.md` and `shotlist.md`, and prints the estimated length. Fix any WARN lines.
4. Send them the plain script with the recording tips below.

## Recording tips to send

**Test before the real take.** Have them record 5–10 seconds of talking with the exact setup, then run
`$PY $S/check_take.py test.mov`. It measures the real frame rate (webcams drop to ~10 fps in dim light while the
file still says 30), freezes, face brightness, framing, sound and sync, and lists what to fix. Only record the
real take once it says READY: a choppy or dark take can be smoothed, but never made to look natural.

- Light IN FRONT of you (a lamp or window facing you, at eye level), never only behind you. Dim faces make webcams drop to ~10 fps, which no edit can fully fix.
- Phone (or iPhone as Continuity Camera) beats a laptop webcam. Close heavy apps while recording. Quiet room; earbuds mic is fine.
- **Clap once** right after you hit record, hands in frame, then pause a second before the first line. The clap's
  sound and the frame where your hands meet sync picture and voice exactly (it's how film crews do it); without
  it, sync falls back to a mouth-movement estimate that some faces and lighting throw off by 200+ ms.
- Record in one take. If you stumble, pause, then repeat the whole sentence; the edit removes the pause and the mistake.
- Leave a second of silence before the first line and after the last one.
- **Split layout:** frame yourself head and shoulders, centered, with space above your head. You'll be on the bottom half.
- Send the raw file. Don't trim it.
