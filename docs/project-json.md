# project.json reference

`project.json` is the whole edit in one file. Every time is either a **phrase you say**, which is matched case- and punctuation-insensitively against `captions.json`, or a time on a **recording clock** from `shots/events.json`.

## Top level

| Key | Default | Meaning |
| --- | --- | --- |
| `title` | | Used on the end card if `end.title` is not set. |
| `speed` | `1.1` | Global speed-up. Pitch is preserved, and picture and voice stay in sync. |
| `output` | `out/demo.mp4` | Final file. A `_small.mp4` is written next to it. |
| `theme.accent` | `#ffe040` | Caption emphasis, chips, face-bubble frame, end-card button. |
| `theme.head` / `theme.body` | `Inter` | Google Fonts families for headings and body text. |
| `theme.google_fonts` | | Full Google Fonts query, e.g. `family=Inter:wght@500;800&family=Silkscreen:wght@400;700`. Use it when a font lacks weights 400/700. |
| `background` | `0x05070f` | Fill color for title shots and letterboxing. |
| `pause.scene` | `1.0` | Seconds of pause kept at scene changes, and at any pause of 1.8 s or more. |
| `pause.long` | `0.6` | Seconds kept for pauses between `short_max` and 1.8 s. |
| `pause.short_max` | `0.8` | Pauses up to this length are kept whole (natural breaths). |
| `pause.head` / `pause.tail` | `0.25` / `2.5` | Lead-in before the first word; hold after the last word (for the end card). |
| `holds` | `[]` | `[{ "after": "Until now", "keep": 1.8 }]`: a dramatic beat after a line. |
| `music` | `"synth"` | `"synth"` (soft pad), `"none"`, or a path to an audio file. |
| `music_gain` / `sfx_gain` | `0.55` / `0.85` | Bed levels before ducking. |
| `end` | | `{ title, tagline, links: [..], by }`. Tagline accepts `<b>`. |
| `sfx_auto` | all `true` | Turn off automatic `whoosh`, `hook`, `title`, `card` or `end` cues. |

## Scenes

```jsonc
{ "title": "Gameplay", "start": "Out here", "chip": true, "end_card": false, "shots": [ ... ] }
```

- `start`: the phrase that opens the scene. The first scene always starts at 0.
- `chip`: show the numbered scene label. Defaults to true except for the first and last scene.
- `end_card`: overlay the end card and hide the face bubble.

## Shots

The first shot starts with its scene. Each later shot needs `"from": "<phrase>"`. A shot runs until the next one starts.

| Kind | Fields | Notes |
| --- | --- | --- |
| speaker | `"speaker": true` | Full-frame you, cover-cropped around your face. |
| recording | `"rec": "main", "t": 12.4, "to": 18.0` | Frames from `shots/main/`, starting at recording time `t`. With `to`, the slice is time-fitted to the shot (sped up or slowed down). |
| animation | `"anim": "diagram"` | `anims/diagram.mp4` from `render_anim.mjs`. |
| image | `"image": "path.png"` | Slow push-in on a still. |
| title | `"title": "UNTIL NOW.", "subtitle": "…"` | Big statement on a dark background. |

Options for any shot:

- `"card": "problem"`: overlays `cards/problem.html`. `card_delay` sets the delay (default 0.4 s).
- `"zoom": "tl" | "tr" | "bl" | "br" | "c"`: push in toward a corner so small UI is readable.
- `"pip": false`: hide the face bubble, e.g. when it would cover the zoom target.

## Sound cues (`sfx`)

```jsonc
{ "sound": "step",   "phrase": "footsteps", "offset": 0.3, "repeat": 5, "every": 0.36, "pan": -0.75 }
{ "sound": "denied", "phrase": "null", "edge": "end", "offset": -0.4 }
{ "sound": "blink",  "rec": "main", "t": 87.32 }
{ "sound": "lock",   "anim": "diagram", "t": 1.8 }
{ "sound": "boom",   "at": 42.0 }
```

Sounds: `boom subboom riser whoosh swing hit bighit chime ding fanfare coin blink step glitch denied success lock pop click ticks typing swell sting`.

All effects are ducked −9 dB while you speak. `boom`, `subboom`, `riser`, `sting`, `bighit` and `glitch` are also low-passed if they overlap speech. Put big hits in pauses.

## Cards and animations

- `cards/<name>.html`: an HTML fragment drawn on a transparent 1920×1080 layer. Optional shared styles go in `cards/cards.css`.
- `anims/<name>.html`: a page that defines `window.seek(t)` and draws frame `t` deterministically. `window.CUES` holds the narration lines inside the shot (`[{t, end, text}]`, shot-relative), so beats can be tied to words. See [`templates/anim.example.html`](../.agents/skills/pitch-video/templates/anim.example.html) and [`examples/nightfall`](../examples/nightfall).
