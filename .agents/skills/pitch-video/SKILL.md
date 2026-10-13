---
name: pitch-video
description: Turn a talking-head recording (someone reading a pitch/demo script) into a polished product demo video — pause-trimmed and sped up 1.1x, perfectly lip-synced, with app footage cut to the words, a face bubble, captions, scene chips, explainer animations, cinematic SFX and ducked music. Use when the user uploads/points to a video of themselves talking and wants a pitch, demo, launch or hackathon submission video.
---

# pitch-video

Input: a talking-head video (+ ideally the script they read, + the product: a URL, local dev server or repo).
Output: `out/demo.mp4` (1080p30) + `out/demo_small.mp4`, verified by `verify.py` before you hand it over.

All scripts live in `scripts/`. Work in a fresh dir (scratchpad): `WORK=<dir>; cd $WORK`.
`PY=~/.cache/pitch-video/venv/bin/python`, `S=<this skill dir>/scripts`.

## Pipeline (do every step, in order)

0. **Setup (once):** `bash $S/setup.sh` — checks ffmpeg/whisper-cli/node, builds the toolbox in `~/.cache/pitch-video`.
1. **Prep:** `$PY $S/prep.py <video>` → `source.mov` (CFR 30, 48 kHz, A/V offset fixed), `captions_raw.json`, `sil.json`, `face.json`.
2. **Captions:** `$PY $S/fix_captions.py <script.md>` (script optional). Read the diff it prints; hand-fix `captions.json`
   (`text` + `html`; use `<b>` for 1–4 key words per scene; fill any `(?)` lines). Never change start/end.
3. **Plan:** write `project.json` (schema below). Anchor every scene and shot to a spoken phrase. Then `$PY $S/edit.py`.
   Re-run edit.py after any change; it prints the full timeline — sanity check shot lengths against the lines.
4. **Speaker cut:** `$PY $S/cut_speaker.py` (fails loudly on any duration mismatch).
5. **Footage:** copy `templates/film.template.mjs` → `film.mjs`, script one deterministic beat per shot, run `node film.mjs`.
   Read `shots/events.json` for exact times to put in `project.json` (`"t"`/`"to"`), then re-run edit.py.
   Explainers: write `anims/<name>.html` with `window.seek(t)` keyed to `window.CUES` (see `templates/anim.example.html`),
   then `node $S/render_anim.mjs <name>`. Custom cards: `cards/<name>.html` (+ optional `cards/cards.css`).
6. **Picture:** `$PY $S/build_bg.py` → `bg.mp4` (every part must report the expected frame count).
7. **Overlays:** `node $S/render_overlays.mjs`.
8. **Sound:** `$PY $S/sfx.py` → `sfx.wav`, `music.wav`.
9. **Compose:** `$PY $S/compose.py`.
9b. **Vertical (optional):** `$PY $S/compose_vertical.py` → `out/demo_vertical.mp4` (1080x1920 for Reels/Shorts/TikTok/X: product on top, face below, captions on the seam; reuses the verified audio).
10. **Verify:** `$PY $S/verify.py` — must print `RESULT: PASS`. Also Read `out/contact.png`. Fix and re-run from the
    earliest affected step. Only then send the file (state it was checked by measurement, not by ear).

## project.json

```json
{
  "title": "NIGHTFALL", "speed": 1.1, "output": "out/demo.mp4",
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
- Shot kinds: `speaker` · `rec` (+`t` start on the recording clock, optional `to` → time-fitted) · `anim` · `image` · `title` (+`subtitle`).
  Options: `card`, `card_delay`, `zoom` (`tl|tr|bl|br|c` push-in to make small UI readable), `pip: false`.
- First and last scenes get no chip by default (`"chip": true/false` overrides).
- SFX library: boom subboom riser whoosh swing hit bighit chime ding fanfare coin blink step glitch denied success lock pop click ticks typing swell sting.
  Auto: whoosh per scene, riser→boom on the hook cut, pop+thud on cards, riser→sub-boom on titles, boom+shimmer after the last word.

## Story shape that works (~2 min, ~300 words)
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
