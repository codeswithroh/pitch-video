# Contributing

Thanks for helping make Pitch Video better.

## Good first contributions

- **Showcases:** made a video with it? Open an issue with the link and we'll feature it.
- **Sound effects:** add a synthesized sound to `sfx.py` (pure numpy, no samples) and list it in `docs/project-json.md`.
- **Caption themes:** new looks for `templates/overlay.html`.
- **Vertical output (9:16):** the most requested feature. See the roadmap in `CHANGELOG.md`.

## Development

The skill lives in `.agents/skills/pitch-video/`. To test local changes, copy it over your installed copy:

```bash
cp -R .agents/skills/pitch-video ~/.claude/skills/
bash ~/.claude/skills/pitch-video/scripts/setup.sh
```

Then run the [pipeline by hand](docs/pipeline.md) on any short talking-head clip. A change is ready when `verify.py` prints `RESULT: PASS` and the contact sheet looks right.

## Rules that keep it "first try"

- Never weaken a check in `verify.py` to make a render pass. Fix the cause.
- If you hit a new failure mode, add it to `docs/lessons.md` along with the code that prevents it.
- Keep every step a standalone script that reads and writes plain files.
