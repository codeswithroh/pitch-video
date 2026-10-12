# Pipeline walkthrough

Your agent runs these steps for you. You can also run them by hand. Every step reads and writes plain files in a work directory, so you can re-run any step on its own.

```bash
PY=~/.cache/pitch-video/venv/bin/python
S=~/.claude/skills/pitch-video/scripts      # or wherever the skill is installed
mkdir work && cd work
```

| # | Command | Reads | Writes |
| --- | --- | --- | --- |
| 0 | `bash $S/setup.sh` (once per machine) | | `~/.cache/pitch-video/` toolbox |
| 1 | `$PY $S/prep.py ~/Movies/take.mov` | your recording | `source.mov`, `captions_raw.json`, `sil.json`, `face.json` |
| 2 | `$PY $S/fix_captions.py script.md` | `captions_raw.json`, script | `captions.json` (then proofread it) |
| 3 | write `project.json`, then `$PY $S/edit.py` | `captions.json`, `project.json` | `timeline.json` |
| 4 | `$PY $S/cut_speaker.py` | `source.mov`, `timeline.json` | `speaker_cut.mov` |
| 5 | `node film.mjs` (from `templates/film.template.mjs`) | your app | `shots/<name>/`, `shots/events.json` |
| 5b | `node $S/render_anim.mjs <name>` | `anims/<name>.html` | `anims/<name>.mp4` |
| 6 | `$PY $S/build_bg.py` | shots, anims, speaker | `bg.mp4` |
| 7 | `node $S/render_overlays.mjs` | `timeline.json`, `cards/` | `ov/*.png` |
| 8 | `$PY $S/sfx.py` | `timeline.json`, `project.json` | `sfx.wav`, `music.wav` |
| 9 | `$PY $S/compose.py` | everything above | `out/demo.mp4`, `out/demo_small.mp4` |
| 10 | `$PY $S/verify.py` | final + stems | report, `out/contact.png`, exit code |

## What "verified" means

`verify.py` fails the build when:

1. The video and audio lengths differ, or the **decoded** audio sample count doesn't match the stated duration.
2. The voice in the final mix drifts more than 30 ms from the speaker track in more than 10% of 8-second windows.
3. Mouth opening (MediaPipe face landmarks) and voice energy are offset outside −70…+140 ms. Natural speech sits around 0 to +100 ms because the mouth opens slightly before the sound.
4. Any caption line has the voice less than 8 dB above the music and effects.

It also prints integrated loudness (aim for −16 to −11 LUFS; YouTube normalizes to −14) and writes a 16-frame contact sheet to check by eye.

## Iterating

- Change wording or emphasis: edit `captions.json`, then re-run steps 3, 7, 9 and 10. If timing anchors moved, also re-run 4, 6 and 8.
- Change which footage plays: edit `project.json`, then re-run 3, 6, 7, 8, 9 and 10.
- Re-film one beat: re-run that shot in `film.mjs` (each shot writes its own folder), then step 6 onward.
