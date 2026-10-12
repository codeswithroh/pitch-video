# Lessons

Each of these failure modes happened on a real edit. Each one is now prevented by code and checked by `verify.py`.

## Sync

**The source file's audio starts late.** QuickTime and phone recordings often carry an audio `start_time` of about 0.15 s. Raw decoders and some filters drop that offset, so the voice lands early.
*Prevention:* `prep.py` re-times both streams to zero and re-inserts the offset with `adelay`/`atrim`. Everything after works from `source.mov`, where the offset is already applied.

**Drift accumulates across cuts.** Trimming each segment by timestamp and then running `fps=30` rounds each piece differently, and dozens of cuts add up.
*Prevention:* cut points snap to the 30 fps grid and are cut by `start_frame`/`end_frame` on video and the matching `start_sample`/`end_sample` (1600 samples per frame at 48 kHz) on audio. `cut_speaker.py` refuses to continue on any length mismatch.

**Timestamps say 114 s, but there are only 105 s of audio.** `loudnorm` outputs 192 kHz. Mixed unconverted inside one big filter graph with looped image inputs, the AAC track came out with fewer samples than its timestamps claimed. Players showed lips moving with no voice, and the voice ended 9 s early.
*Prevention:* every audio branch is resampled to 48 kHz, intermediate audio stays PCM, and picture and sound render in separate passes before being muxed. `verify.py` decodes the final file and compares the sample count with the duration.

**Speed-up breaks sync.** Speeding picture and voice separately, or using a resampling speed-up for audio, drifts or chipmunks.
*Prevention:* `setpts=PTS/S` and `atempo=S` run on the same already-cut file, in one graph.

## Words

**Captions feel late.** Whisper timestamps on a whole file lag by 0.3–1 s.
*Prevention:* transcribe each speech chunk (found by silence detection) separately, padded with silence on both sides. Whisper often returns nothing for clips that start on a word.

**Jargon gets misheard.** "VRF" came out as "Virev", "Ephemeral Rollup" as "If-Moral Roll-Out", and "setup" as "sit-ups".
*Prevention:* `fix_captions.py` word-aligns the transcript to your script and keeps the script's spelling and `**bold**` emphasis. Timings always come from the audio.

## Mix

**Music masks the voice.** A constant bed competes with quiet phrases.
*Prevention:* the voice chain (HPF 85 Hz, −2 dB at 250 Hz, +4 dB at 3.2 kHz, 4:1 compression, loudnorm −14 LUFS) runs alongside a music bed side-chain-ducked by the voice.

**Impacts cover words.** A boom on "Until now." or "Come play." erased the words.
*Prevention:* SFX duck −9 dB under every caption span, heavy sounds are low-passed when they overlap speech, and the end boom lands 0.1 s after the last word. `verify.py` flags any line under 8 dB voice-over-background.

## Picture

**Footage is blurry.** Playwright `recordVideo` is low-bitrate VP8.
*Prevention:* a CDP `Page.startScreencast` of JPEG frames with timestamps, from headed Chrome (GPU on), at 30 fps.

**Rendering is painfully slow.** Feeding about 50 looped PNG overlays into one filter graph crawled.
*Prevention:* overlays are concatenated into three qtrle alpha tracks (captions, cards, chips) with the concat demuxer, then overlaid once.

**ffmpeg can't draw text.** Many builds lack `drawtext`/`libass`.
*Prevention:* all text is HTML rendered to transparent PNGs by Playwright. This also gives real fonts and CSS.

**The face bubble covers the thing being zoomed.**
*Prevention:* `"pip": false` per shot, and captions shift left while the bubble is showing.
