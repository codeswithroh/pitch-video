<div align="center">

**English** · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Português (Brasil)](README_pt-BR.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [हिन्दी](README_hi.md) · [Bahasa Indonesia](README_id.md) · [Tiếng Việt](README_vi.md) · [Türkçe](README_tr.md)

<img src="docs/assets/logo.svg" alt="Pitch Video logo" width="96" />

# Pitch Video

### Record yourself reading your pitch. Your agent turns it into a launch-ready demo video.

**Talking head in → cut, captioned, scored, lip-synced product demo out. First try.**

[![skills.sh](https://img.shields.io/badge/skills.sh-pitch--video-111?style=flat-square)](https://skills.sh/codeswithroh/pitch-video)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757?style=flat-square)](#quick-start)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini_CLI-5c4ee5?style=flat-square)](#faq)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg_·_whisper.cpp_·_Playwright-007808?style=flat-square)](#requirements)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)

[Quick start](#quick-start) · [What you get](#what-you-get) · [How it works](#how-it-works) · [Showcase](#showcase) · [Why it works first try](#why-it-works-first-try) · [FAQ](#faq) · [Docs](#documentation)

<code>npx skills add codeswithroh/pitch-video</code>

<a href="https://www.producthunt.com/posts/pitch-video?utm_source=badge-featured&utm_medium=badge" target="_blank" rel="noopener"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1277696&theme=dark" alt="Pitch Video on Product Hunt" width="250" height="54" /></a>

<br /><br />

<img src="docs/assets/hero.jpg" alt="A raw talking-head recording on the left turns into a finished product demo on the right: gameplay footage, a face bubble, burned-in captions" width="1100" />

</div>

---

Hackathon submissions, launch videos and investor demos all want the same thing: **you, explaining, while the product does the talking.** Making that by hand means hours in an editor: trimming ums, syncing footage to sentences, captioning, finding sound effects, and then discovering your lips are 300 ms off.

**Pitch Video is an agent skill that does the whole edit.** Hand your agent the recording (and your script and app, if you have them). It transcribes you, trims the dead air, speeds you up 1.1× without the chipmunk effect, films your product with a scripted browser, cuts every shot to the exact words you say, adds captions, a face bubble, an animated explainer, cinematic sound effects and a ducked music bed. Then it **measures its own output** (lip sync, audio drift, loudness, voice clarity) and refuses to hand you a broken file.

Everything runs locally with ffmpeg, whisper.cpp and Playwright. No uploads, no subscriptions, no timeline editor.

> **Don't want to set it up?** [Pitch Video Studio](https://pitch-video-studio.vercel.app/) makes it for you: send your take, get the finished video in 3 hours, from $49. The first 10 orders pay only after delivery.

## Not just pitches: any talking video

Ask your agent for ideas, get a script, read it once, get the video.

1. **Ideas from who you are.** "What video should I make?" Your agent reads your repo, links and recent posts, writes a 4-line profile, then pitches 5 ideas that fit you: a walkthrough of a tool that launched this week, a build-in-public update, a hot take, a tutorial, a comparison.
2. **A script with the edit already in it.** Pick one and it writes the script in your voice, with every visual cued to the line it appears on (`[rec site: scroll to the pricing table]`, `[anim lanes: eight agents merging into one diff]`).
3. **One take.** Read it on your webcam or phone. Stumble? Pause and repeat the sentence; the stumbled attempt is cut.
4. **The video.** Split layout (9:16): the product, site footage and motion graphics on the top half, you on the bottom half, captions on the seam. Or the 16:9 pitch layout with a face bubble. Same sync and loudness checks either way.

## Quick start

### 0. Or let your agent do everything

Copy this into Claude Code (or any coding agent):

```text
Install the pitch-video skill from https://github.com/codeswithroh/pitch-video
(run its install.sh), then make a pitch video from my recording at ~/Movies/my_pitch.mov.
```

### 1. Install the skill

```bash
npx skills add codeswithroh/pitch-video
```

or, for Claude Code directly:

```bash
curl -fsSL https://raw.githubusercontent.com/codeswithroh/pitch-video/main/install.sh | bash
```

The installer copies the skill to `~/.claude/skills/pitch-video` (and `~/.agents/skills/pitch-video` for other agents) and builds the shared toolbox: a Python venv, Playwright Chromium, the Whisper `small.en` model and a face-landmark model. Restart your agent afterwards.

### 2. Record yourself

Read your script to the camera. Landscape, face and shoulders, quiet room. Pause for a breath between sections. Stumbles are fine; re-read the line.

> Need a script? Ask your agent: *"Write me a 2-minute pitch-video script for this repo using the pitch-video story shape."*

### 3. Ask your agent

```text
Make a pitch video from ~/Movies/my_pitch.mov.
The script is docs/pitch-script.md and the app runs at http://localhost:5173.
```

Your agent plans the scenes from what you said, films your app, renders, verifies and hands you `out/demo.mp4` plus a smaller `demo_small.mp4` for uploads.

## What you get

<table>
<tr>
<td width="50%"><img src="docs/assets/frame_gameplay.jpg" alt="Gameplay with face bubble and caption" /></td>
<td width="50%"><img src="docs/assets/frame_proof.jpg" alt="Zoomed-in proof shot with caption" /></td>
</tr>
</table>

| Feature | What it does |
| --- | --- |
| **Pause trimming** | Cuts dead air and keeps natural breaths, with longer beats at scene changes and holds you choose ("Until now." … *beat*). |
| **1.1× pacing** | Tighter delivery with pitch preserved. Picture and voice are sped up together, so sync stays exact. |
| **Cut-to-the-word visuals** | Every scene and shot is anchored to a *phrase you say*, so the footage changes exactly on the line that introduces it. |
| **Scripted product footage** | Generates a Playwright film script for your app: headed Chrome, a 30 fps CDP screencast and a timestamped event log to cut against. |
| **Face bubble** | Auto-framed from face landmarks, rounded, accent-bordered. Hidden on full-frame and end-card shots. |
| **Captions that are right** | Per-chunk Whisper timing, then word-aligned to your script, so "Virev" becomes **VRF** and `**bold**` in the script becomes highlighted words. |
| **Explainer animations** | HTML diagrams whose beats are keyed to your narration (`CUES.find(c => /sealed/.test(c.text))`). |
| **Cinematic sound** | 23 synthesized SFX (riser, boom, whoosh, lock, chime, glitch…), auto-placed on cuts and cards and ducked under every spoken word. Optional music bed. |
| **Cinematic cold opens** | Hero shots of your real UI before the first word: a tilted slab in a black void, a thin focus band, a slow drift and light on the subject, then a hard cut to your face. Look after [cinematic-shot](https://github.com/1weiho/cinematic-shot). |
| **Verification gate** | Lip-sync measurement, A/V drift check, decoded-sample audit, per-line voice-over-background dB, EBU R128 loudness and a contact sheet. Ships only on `PASS`. |

## How it works

<img src="docs/assets/pipeline.svg" alt="Pipeline: your video, script and product go in; the skill aligns, transcribes, trims, films, cuts, overlays, scores and verifies; demo.mp4 comes out" width="100%" />

The whole edit lives in one readable file, `project.json`. Scenes start on phrases, shots switch on phrases, and sound cues fire on phrases or on recorded app events:

```jsonc
{
  "speed": 1.1,
  "scenes": [
    { "title": "The hook", "start": "Every onchain game", "shots": [
      { "speaker": true },
      { "from": "If it lives", "rec": "main", "t": 9.8 } ]},
    { "title": "The problem", "start": "fog of war", "shots": [
      { "rec": "main", "t": 18.8, "card": "problem" },
      { "from": "Until now", "title": "UNTIL NOW." } ]},
    { "title": "How it works", "start": "Every position is sealed", "shots": [{ "anim": "diagram" }] }
  ],
  "sfx": [{ "sound": "denied", "phrase": "null", "edge": "end", "offset": -0.4 }]
}
```

See the full [project.json reference](docs/project-json.md) and the [pipeline walkthrough](docs/pipeline.md).

## Showcase

### Nightfall: a hackathon pitch for an onchain battle royale

[![Contact sheet of the Nightfall demo video](docs/assets/contact.jpg)](https://youtu.be/BbZI25i2Mgo)

A 2:25 talking-head take became a 1:53 demo with 10 scenes, 18 shots, a live-gameplay proof sequence, an animated architecture diagram and 40+ sound cues. Verification measured **0 ms** voice drift across every window, **0 ms** lip-sync offset and ≥14.6 dB voice-over-background on every line.

**[Watch it on YouTube](https://youtu.be/BbZI25i2Mgo)** · [project.json](examples/nightfall/project.json) · [script](examples/nightfall/pitch-script.md)

<img src="docs/assets/demo.gif" alt="Five seconds of the Nightfall demo: dark arena, torchlight, caption, face bubble" width="720" />

Made something with Pitch Video? [Open an issue](https://github.com/codeswithroh/pitch-video/issues) with a link and we'll add it here.

## Why it works first try

This skill was extracted from a real edit that took many painful iterations. Every failure became a rule the skill now enforces:

- **"My lips don't match."** QuickTime and phone files often start audio about 150 ms after video. The skill re-aligns explicitly before anything else.
- **"Sync drifts later in the video."** Cuts land on the 30 fps frame grid, by frame number *and* matching audio-sample number. Nothing accumulates.
- **"My voice stops before my mouth does."** One combined ffmpeg graph silently dropped 9 seconds of audio samples (loudnorm emits 192 kHz). Picture and sound now render in separate passes, every branch is resampled to 48 kHz, and the verifier decodes the final file to prove the sample count.
- **"Captions feel late."** Whole-file Whisper timestamps lag. Per-chunk transcription lands captions on the exact speech boundaries.
- **"Effects drown me out."** Sound effects duck −9 dB under every spoken line, heavy hits are low-passed if they touch speech, and the final boom lands *after* your last word.
- **"Footage looks blurry."** Playwright's built-in recorder is low-bitrate VP8. The skill uses a CDP screencast from headed, GPU-on Chrome.

The full list is in [docs/lessons.md](docs/lessons.md).

## Requirements

- macOS or Linux, with `ffmpeg`, `whisper-cli` (whisper.cpp), Node.js 18+ and Python 3.10+.
- macOS: `brew install ffmpeg whisper-cpp node python`
- About 1 GB of disk for the toolbox (Chromium, Whisper model, venv), shared across projects.

## FAQ

<details>
<summary><strong>Which agents can use it?</strong></summary>

Any agent that loads `SKILL.md` skills and can run shell commands: Claude Code, Codex, Cursor, Gemini CLI and others via `npx skills add`. The scripts are plain Python, Node and ffmpeg, so you can also run the [pipeline by hand](docs/pipeline.md).

</details>

<details>
<summary><strong>I don't have a script. Does it still work?</strong></summary>

Yes. Captions come straight from Whisper and your agent proofreads them. A script just makes jargon and product names exact, and lets you mark emphasis with `**bold**`.

</details>

<details>
<summary><strong>My product isn't a web app.</strong></summary>

Use any footage: screen recordings, simulator captures or images. Drop frames into `shots/<name>/` with a `stamps.json`, or use `image` shots. The web filming template is a convenience, not a requirement.

</details>

<details>
<summary><strong>Can I use my own music?</strong></summary>

Set `"music": "path/to/track.mp3"`. It is looped, normalized low and side-chain ducked under your voice. Use `"none"` for silence.

</details>

<details>
<summary><strong>Vertical video for TikTok, Reels or Shorts?</strong></summary>

Not yet: output is 1920×1080. 9:16 is the top item on the [roadmap](CHANGELOG.md#roadmap).

</details>

<details>
<summary><strong>Does anything get uploaded?</strong></summary>

No. Transcription, rendering and analysis all run on your machine. Your agent sees the transcript and the timeline, and its model provider has its own data policy.

</details>

## Documentation

- [Pipeline walkthrough](docs/pipeline.md): every step, its inputs and outputs, and how to re-run one.
- [project.json reference](docs/project-json.md): scenes, shots, cards, animations, sound cues, theme and music.
- [Lessons](docs/lessons.md): the failure modes this skill prevents, and why.
- [SKILL.md](.agents/skills/pitch-video/SKILL.md): the instructions your agent follows.

## Contributing

Issues and PRs are welcome, especially new SFX, caption themes, vertical output and showcase videos. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

The cinematic shot look (oblique hero shots of UI in a black void) follows Wei Ho's [cinematic-shot](https://github.com/1weiho/cinematic-shot) skill. `cine.py` is an independent implementation of that look.

The reel defaults (pacing without speed-up, 1-3 word captions kept off the mouth, the soft sound palette, the first-3-seconds test, and the final-audio word and cut-frame checks) are adapted from Nate Herk's editing playbook in [herk-edit-kit](https://github.com/nateherkai/herk-edit-kit) (MIT), measured on his top reels. See `references/house-style.md`.

## License

[MIT](LICENSE). The Whisper and MediaPipe models are downloaded from their upstream sources and keep their own licenses.
