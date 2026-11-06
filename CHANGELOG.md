# Changelog

## Unreleased

- `clean.py`, the last pipeline step: keeps the finished videos and deletes every work file. It runs only after `verify.py` passed on the current output, and never in a home or git folder.
- Long blank stretches in an overlay track no longer get ffmpeg killed for running out of memory. `alpha_track` splits them into 2 s pieces, with the same frames in the track.

## 1.1.0 (2026-10-13)

- End-card credit line ("Edited by an agent · pitch-video"), on by default. Opt out with `"credit": false`.
- README in 13 more languages.
- Copy-paste agent prompt in the Quick start.

## 1.0.0 (2026-10-12)

First public release.

- Full pipeline: prep, caption fixing, edit, speaker cut, filming template, animations, picture, overlays, SFX and music, compose, verify.
- Phrase-anchored scenes, shots and sound cues in a single `project.json`.
- Script alignment for captions, with `**bold**` carried through as emphasis.
- Verification gate: decoded-sample audit, voice drift, lip-sync measurement, per-line voice-over-background level, loudness and a contact sheet.
- Showcase: Nightfall (Solana Blitz hackathon).

## Roadmap

- 9:16 vertical output with a face-top or face-bottom layout.
- Word-level karaoke captions.
- A filming template for iOS Simulator and Android emulator footage.
- Multiple speakers.
