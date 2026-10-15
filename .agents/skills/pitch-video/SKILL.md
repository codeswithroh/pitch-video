---
name: pitch-video
description: Make any talking video, from idea to verified file, with optional cinematic cold opens of the real UI. Suggests video ideas from who the person is (profile, audience, goal), writes the script with the edit cued into it and a teleprompter, then turns their single take into a finished video - product walkthroughs of new AI tools, reviews, tutorials, build-in-public updates, hot takes, launch and pitch/demo videos. Two layouts - split (9:16, product footage and motion graphics on the top half, the speaker on the bottom) and pitch (16:9 with a face bubble). Pause-trimmed, retakes removed, lip-synced, captions, explainer animations, SFX and ducked music, checked by measurement. Use when someone wants a video idea, a script, or uploads/points to a recording of themselves talking.
---

# pitch-video

Input: anything from "what video should I make?" to a finished recording (+ the script, + what to show: a URL, local dev server, repo).
Output: the video at `project.json` → `output` (split: 1080x1920; pitch: 1080p30 + `_small`), verified by `verify.py` before you hand it over.

Start where the user is:
- **No idea yet** → Stage A (ideas). **Has an idea, no script** → Stage B (script). **Has a recording** → the pipeline (step 0a on).
- The person only ever does two things: pick an idea and read the script once on camera. Everything else is yours.

## Stage A: ideas
Read `references/ideas.md`. Profile the person from what you can already see (repo, links, posts) before asking anything, show them a 4-line profile, then 5 ideas in the given format, ranked, with one recommended. Ideas must fit *them*, be timely, and have something real to put on screen.

## Stage B: script
Read `references/scripts.md`. Write `script.md` with front matter (layout, accent, end card) and cues (`[face]`, `[rec name: what to film]`, `[anim name: what it explains]`, `[title …]`, `[end]` …) on their own lines before the line they cover. Show them the plain script, revise until it sounds like them, then:
`$PY $S/script_plan.py script.md` → `project.json` (scenes and shots already anchored to the words), `narration.md`, `shotlist.md`, `teleprompter.html`. Fix any WARN. Send them the teleprompter + recording tips from `references/scripts.md`, and have them record a 5 s test first: `$PY $S/check_take.py test.mov` must say READY (real 30 fps, lit face, framing, sound) before the real take.
While they record, you can already film every `rec` and build every `anim` on the shot list (step 5); times get filled in after.

## Cinematic shots
Walkthroughs and product overviews open harder with a **cold open**: 2–4 cinematic hero shots of the real UI (tilted slab in a black void, thin focus band, slow drift, light on the subject) before the first word, then a hard cut to the face. Read `references/cinematic.md`. In a script: a `## Cold open` section with only `[cine name scale: subject]` cues; anywhere else, `[cine …]` works like `[rec …]`. Capture sharp sources with `still()` / `mark()` on a `hidpi` page in film.mjs, then `$PY $S/cine.py`. Grab a frame from each shot and check it before going on.

## Layouts
- **`"layout": "split"`**: 9:16. The canvas (footage, animations, cards, titles, end card) is **1080x960** and fills the top half; the speaker fills the bottom half; captions sit on the seam; `speaker` shots go full-frame face. Film and design animations at 1080x960 (film.template.mjs and render_anim.mjs do it automatically; write anim CSS in `vw/vh` or for 1080x960). Footage of another size sits on a blurred copy of itself. Best for Reels, Shorts, TikTok, X, and walkthroughs of new tools.
- **`"layout": "pitch"`** (default): 16:9 with a face bubble. Best for submissions, YouTube, landing pages. `compose_vertical.py` can still cut a 9:16 version from it.

All scripts live in `scripts/`. Work in a fresh dir (scratchpad): `WORK=<dir>; cd $WORK`.
`PY=~/.cache/pitch-video/venv/bin/python`, `S=<this skill dir>/scripts`.

## Pipeline (do every step, in order)

0a. **Rules first:** `$PY $S/rules.py show`, and follow every active rule. They are the user's lasting preferences from past videos; edit.py applies the numeric ones (speed, pauses, music level, accent) automatically.
0. **Setup (once):** `bash $S/setup.sh` — checks ffmpeg/whisper-cli/node, builds the toolbox in `~/.cache/pitch-video`.
1. **Prep:** `$PY $S/prep.py <video>` → `source.mov` (CFR 30, 48 kHz, A/V offset fixed), `captions_raw.json`, `sil.json`, `face.json`.
   prep also measures lip sync on the raw take and corrects the audio if it's 50 ms+ off (webcams in low light and re-encodes often are); `--av-offset <ms>` forces a shift, `--no-av-fix` skips it.
   **Choppy take** (check with ffprobe: real frame rate far below 30, freezes): first interpolate it, `ffmpeg -i take.mov -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:me=epzs:search_param=64:vsbmc=1:scd=none,tmix=frames=3:weights='1 2 1',fps=30" -c:a copy take30.mov`, then prep take30.mov. `scd=none` stops the hold-then-jump on big gaps, the wider search follows head moves, and the 60→30 blend adds the motion blur a real camera would have (measured on a 10 fps take: no jumps left, jerkiness 0.15 → 0.09). Frames the camera never captured can't be invented: tell the user that more light in front of them fixes it at the source.
2. **Captions:** `$PY $S/fix_captions.py narration.md` (or their script; optional). Read the diff it prints; hand-fix `captions.json`
   (`text` + `html`; use `<b>` for 1–4 key words per scene; fill any `(?)` lines). Never change start/end.
2b. **Retakes:** `$PY $S/retakes.py` lists lines they stumbled on and repeated; check the list, then `--apply` (drops the earlier attempt).
3. **Plan:** `project.json` came from script_plan.py in Stage B; otherwise write it (schema below). Anchor every scene and shot to a spoken phrase. Then `$PY $S/edit.py`.
   Re-run edit.py after any change; it prints the full timeline — sanity check shot lengths against the lines.
4. **Speaker cut:** `$PY $S/cut_speaker.py` (fails loudly on any duration mismatch).
5. **Footage:** copy `templates/film.template.mjs` → `film.mjs`, script one deterministic beat per shot, run `node film.mjs`.
   Read `shots/events.json` for exact times to put in `project.json` (`"t"`/`"to"`), then re-run edit.py.
   Explainers: write `anims/<name>.html` with `window.seek(t)` keyed to `window.CUES` (see `templates/anim.example.html`),
   then `node $S/render_anim.mjs <name>`. Custom cards: `cards/<name>.html` (+ optional `cards/cards.css`).
5c. **Cinematic shots** (if any `cine` shots or an `intro`): `$PY $S/cine.py` → `cine/<name>.mp4` at the exact shot length. Check a frame of each.
6. **Picture:** `$PY $S/build_bg.py` → `bg.mp4` (every part must report the expected frame count).
7. **Overlays:** `node $S/render_overlays.mjs`.
8. **Sound:** `$PY $S/sfx.py` → `sfx.wav`, `music.wav`.
9. **Compose:** pitch layout: `$PY $S/compose.py`. Split layout: `$PY $S/compose_vertical.py` (writes the 9:16 video and its own audio; compose.py refuses split).
9b. **Vertical cut of a pitch video (optional):** `$PY $S/compose_vertical.py` → `out/<name>_vertical.mp4` (16:9 picture on top, face below; reuses the verified audio).
9c. **Posts:** `$PY $S/draft_posts.py` → `out/posts.md`: X thread, LinkedIn, Product Hunt, Reddit and Show HN drafts built from what was actually said. Polish them with the user; never post unreviewed.
10. **Verify:** `$PY $S/verify.py` — must print `RESULT: PASS`. Check [0] is a pipeline self-test (synthetic flash+click clip through the same cut, speed-up, mix and mux); if it fails, the pipeline itself is out of sync, so fix that before touching the footage. Run it alone with `$PY $S/selftest.py`. `UNVERIFIED` means a check could not run or was inconclusive (no face found, or mouth movement doesn't track the voice: a still image, a tiny or hidden face): fix the cause or tell the user plainly; never call it passed. Also Read `out/contact.png`. Fix and re-run from the
    earliest affected step. Only then send the file (state it was checked by measurement, not by ear).

## project.json

```json
{
  "title": "NIGHTFALL", "layout": "pitch", "speed": 1.1, "output": "out/demo.mp4",
  "theme": {"accent": "#ffe040", "head": "Inter", "body": "Inter"},
  "pause": {"scene": 1.0, "long": 0.6, "short_max": 0.8, "head": 0.25, "tail": 2.5},
  "holds": [{"after": "Until now", "keep": 1.8}],
  "music": "synth",                      // "synth" | "none" | path to a track
  "credit": true,                        // small "Edited by an agent · pitch-video" line on the end card; false removes it
  "end": {"title": "NIGHTFALL", "tagline": "Everyone's in the dark. <b>Even the server.</b>",
          "links": ["▶ app.example.com", "github.com/you/repo"], "by": "Built with …"},
  "scenes": [
    {"title": "The hook", "start": "Every onchain game", "shots": [
      {"speaker": true},
      {"from": "If it lives", "rec": "main", "t": 9.8}]},
    {"title": "The problem", "start": "fog of war", "shots": [
      {"rec": "main", "t": 18.8, "card": "problem"},
      {"from": "Until now", "title": "UNTIL NOW."}]},
    {"title": "How it works", "start": "Every position is sealed", "shots": [{"anim": "diagram"}]},
    {"title": "Outro", "start": "Nightfall", "end_card": true, "shots": [{"rec": "main", "t": 133, "to": 141}]}
  ],
  "sfx": [
    {"sound": "step", "phrase": "Footsteps", "offset": 0.5, "repeat": 5, "every": 0.36, "pan": -0.75},
    {"sound": "blink", "rec": "main", "t": 87.32},
    {"sound": "denied", "phrase": "null", "edge": "end", "offset": -0.5},
    {"sound": "lock", "anim": "diagram", "t": 1.8}
  ]
}
```
- Scene `start` / shot `from` = a phrase from captions.json (case/punctuation-insensitive). First shot starts with its scene.
- Cold open: `"intro": {"shots": [{"cine": "hero", "src": "stills/hero.png", "focus": "subject", "scale": "macro", "len": 3.5}, …]}` plays before the first word (edit.py shifts everything after it; cut_speaker.py pads the speaker track to match).
- Shot kinds: `cine` (see references/cinematic.md) · `speaker` · `rec` (+`t` start on the recording clock, optional `to` → time-fitted) · `anim` · `image` · `title` (+`subtitle`) · `black` (empty canvas, e.g. under the end card).
  Options: `card`, `card_delay`, `zoom` (`tl|tr|bl|br|c` push-in to make small UI readable), `pip: false`.
- First and last scenes get no chip by default (`"chip": true/false` overrides).
- SFX library: boom subboom riser whoosh swing hit bighit chime ding fanfare coin blink step glitch denied success lock pop click ticks typing swell sting.
  Auto: whoosh per scene, riser→boom on the hook cut, pop+thud on cards, riser→sub-boom on titles, boom+shimmer after the last word.

## Story shapes
Split videos: see the format table in `references/ideas.md` (walkthrough, review, tutorial, update, hot take…): hook on the face, product on screen by the second line, top half changes every 3–6 s.

Pitch/demo (~2 min, ~300 words):
Hook (face, 1 bold claim) → Problem (show it, 1 card) → "Until now." beat → Meet the product → Onboarding →
Core experience → **Proof** (show the hard thing actually working) → How it works (one animated diagram) → Outro (end card + "come play/try it").
Open on the face (trust), cut to product within ~4 s, keep the face bubble on during product shots, return to full-frame face for the close.

## Lessons baked in (do not regress these)
- **A/V offset in the source:** phone/QuickTime audio often starts 0.1–0.2 s after video. prep.py re-aligns explicitly; never decode raw audio from the original file for timing.
- **Cut on the frame grid,** by frame number and matching sample number (1600 samples/frame @48k). Per-segment `trim`+`fps` drifts.
- **Keep intermediate audio PCM;** **resample every audio branch to 48 kHz** (loudnorm emits 192 kHz). Skipping this produced an AAC track whose timestamps said 114 s but held 105 s of samples: lips drifted and the voice ended early. verify.py check [1] catches it.
- **Render picture and sound in separate ffmpeg passes, then mux.** In one combined graph (looped PNG inputs + loudnorm/sidechain) ffmpeg dropped ~9 s of audio samples. compose.py does this; verify.py [1]/[2] prove it.
- **SFX are ducked -9 dB under every spoken line** automatically; end-card boom lands 0.1 s after the last word.
- **Speed-up:** `setpts=PTS/S` + `atempo=S` on the *same* cut file — pitch stays natural, sync stays exact. 1.1x feels tighter without sounding rushed.
- **Transcribe per speech chunk** (padded) — whole-file whisper timestamps lag. Then align to the script; whisper mishears jargon/brand names.
- **Voice must win:** voice chain (HPF, -2 dB@250, +4 dB@3.2k, compressor, loudnorm -14) + music side-chain-ducked + heavy SFX low-passed when they overlap words; land big hits in pauses, the final boom *after* the last word. Target ≥10 dB voice-over-background per line.
- **Footage:** CDP screencast frames from headed Chrome, not Playwright recordVideo. Log events; drive the edit from logged times. Film each beat 2–3x longer than needed.
- **Overlays** are HTML→PNG (ffmpeg here has no drawtext/libass) baked into 3 qtrle alpha tracks via the concat demuxer — never 50 looped PNG inputs.
- Captions shift left while the face bubble is on; the bubble is hidden on full-frame speaker shots and the end card.
- Check the end card doesn't sit on top of busy UI (name tags etc.) and that zoomed shots aren't covered by the bubble (`pip:false`).
- Explainer animations: deterministic `seek(t)`, beats keyed to spoken words via `CUES`, rendered at the exact shot length.

## Feedback → rules (do this every time the user reacts to a video)
- Log every note: `$PY $S/rules.py note "too fast at 0:42"`.
- If the note is about taste rather than this one video ("always", "never", "I prefer", or the same note twice), turn it into a rule: `$PY $S/rules.py add "<rule in imperative voice>" --from "<the note>"`. Use `--project` for rules that only fit this product.
- A new rule on the same topic retires the old one automatically, so rules never contradict. Tell the user when that happens.
- Re-run from the earliest affected step, show the new version, and keep the previous output (rename it `out/demo_v<N>.mp4`).

