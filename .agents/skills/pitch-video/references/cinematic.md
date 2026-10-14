# Cinematic hero shots (`cine`)

A cinematic shot films the product's real interface like an object on a set: the UI is a slab in a black void,
tilted back and rotated so lines of text cross the frame diagonally, with only a thin band in focus. The camera
creeps toward the subject and is still moving at the cut. A soft pool of light sits on the slab around the
subject. It's what makes a walkthrough open like a launch film instead of a screen recording.

The look follows Wei Ho's [cinematic-shot](https://github.com/1weiho/cinematic-shot) skill. `scripts/cine.py`
is an independent renderer for it (perspective homography, per-pixel depth of field, light in plane coordinates,
vignette and grain), driven from the same shot list as the rest of the video.

## Where to use it

- **Cold open** (`project.json` → `"intro": {"shots": [...]}`; in a script, a `## Cold open` section with only
  `[cine …]` cues): 2–4 shots, 8–12 s total, before the first spoken word. No voice, no music, no captions; a quiet
  swell and a sub-boom land the cut to the speaker's face. In split layout it fills the whole 9:16 frame.
- **Inside the video**: `[cine name scale: subject]` on any line, like `rec`. Good for the one moment the product
  does something remarkable.

## Writing the shots

Think in subjects, not pages. Each shot has exactly one thing in focus.

| Scale | Magnification | Use for | Length |
|---|---|---|---|
| `xmacro` | 6× | one control: a button, a tab, a badge, a status chip | 2–3 s |
| `macro` | 3.2× | a line of text, a composer, a few rows, a code hunk | 3–4 s |
| `medium` | 2× | a panel at work: a list, a diff, a document | 4–6 s |
| `wide` | 0.95×, near-frontal | the payoff only: the whole window | 4–6 s |

- Alternate scales (a short close shot, then a longer one) and the diagonal flips automatically on every cut.
- Save `wide` for the last shot of the cold open, where it lands as the reveal.
- `xmacro` on a big heading just shows blurred giant glyphs. Use `macro` for headlines and `xmacro` for small controls.
- Pick subjects that have something on them. Empty header space or page margins render as black.

## Capturing the sources (film.mjs)

```js
const { ctx, page } = await newPage({}, { hidpi: true });       // 2x pixels: cine magnifies up to 6x
await page.goto(URL);
// dismiss cookie banners, sign in, set dark mode if the product has one, fill realistic data
await still(page, "deploy", { subject: "button:has-text('Deploy')", status: ".build-status" });
```
`still()` saves `stills/<name>.png` and `stills/<name>.json` with each target's position. Targets must be on
screen (scroll first). For moving UI (typing, streaming, a list filling in), record with `recorder()` on a hidpi
page and save positions with `mark(page, "<rec>", "subject", selector)`; then use `"src": "shots/<rec>"` with `"t"`/`"to"`.

## Shot spec

```json
{"cine": "deploy", "src": "stills/deploy.png", "focus": "subject", "scale": "xmacro", "len": 2.5}
{"cine": "logs", "src": "shots/main", "t": 12.0, "to": 17.0, "focus": "subject", "track": [0.6, 0.55],
 "scale": "medium", "rack": [0.6, "status"]}
```
`focus` / `track` / `rack` take a named target or `[x, y]` fractions of the page. Optional overrides: `pitch`,
`roll`, `yaw`, `push`, `frame` (where the subject sits on screen). `len` is for cold-open shots; shots inside the
video get their length from the words.

Render: `$PY $S/cine.py` (all) or `$PY $S/cine.py deploy logs`. About 10 s of 1080x1920 takes ~2 minutes.

## Check every shot

Grab a frame from the middle of each `cine/<name>.mp4` and look at it:
- One sharp subject, and the eye lands on it at once. Bokeh both nearer and farther.
- Text runs diagonally and visibly shrinks into the distance (except `wide`).
- At least a quarter of the frame is black or near-black.
- The only colour is the product's own.
- Light-themed pages are exposed down automatically. If one still looks like a spotlight on paper, move the
  focus onto denser content or use `medium`.
