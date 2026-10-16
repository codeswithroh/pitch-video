# House reel style (the defaults for split / reel videos)

Adapted from Nate Herk's editing playbook in [herk-edit-kit](https://github.com/nateherkai/herk-edit-kit) (MIT),
which was measured frame by frame on his 27 top Instagram Reels and refined over dozens of note rounds. Use
these as defaults when the user gives no style; the user's brief and `rules.md` win.

## The one question first

**"In the first 3 seconds, is someone convinced they need to watch until the end?"** Everything else (effects,
polish, sound) comes after. Answer it in writing before rendering: the specific benefit, the unresolved question,
what's visible by second three, and where the video pays it off. A promise the footage can't keep fails.

## Pacing

- Speech starts within the first frames. No silent intro, no logo bumper. The file ends right after the last word
  (plus the end card hold). For reels, put cinematic shots UNDER the hook's voice, not before it.
- No dead air: pauses between phrases under ~0.25 s. Natural beats after a comma or "First," stay (0.2-0.4 s).
- **Never speed the voice up.** Tightness comes from removing gaps. (`"pace": "reel"`, the split default.)
- Cut between phrases at real silence, never inside one. A filler that runs straight into the next word stays:
  cutting it clips the words around it.
- Shots average ~1.1-1.4 s in fast reels, none much over ~3 s unless an action earns the hold. Each item in a
  spoken list gets its own shot.

## Layouts (1080x1920; every change is a hard cut)

- **Split** (visual on top, speaker below) is the backbone. The first frame is a split with the topic's tool or
  product on top, not a title card.
- **Full-face / punch-in** for pivots, conviction and the CTA, 5-15% of the reel.
- The speaker is never gone for more than ~3.5 s.

## Captions (`"captions": {"mode": "words"}`, the split default)

- 1-3 words per chunk, split on phrase boundaries; appear 2 frames before the first word; hard swap, no pop.
- One look for the whole video: all caps, heavy weight, one dark box with a thin light edge (reads on black,
  white and footage alike). Never white text on a light background.
- Emphasis colours the whole chunk, on 25-45% of chunks at most. Bold words in the script mark them.
- Position: on the seam in a split; on the shirt in a full-face shot; never over the mouth or chin, least of all
  in the first second (that's when viewers decide whether the person is real). A chunk across a cut moves with it.

## B-roll (top half) preference order

1. Real footage of the thing named (the product's demo, your own recording).
2. A real screen recording, zoomed into the part being talked about.
3. An animated UI mock (typing, rows ticking, a counter). Label mocks as examples.
4. A cinematic hero shot of the real UI (`cine`).
5. Short highlight crops of a real page (<1 s) on names, prices, badges.

Every shot moves. A whole web page shrunk to phone size is unreadable: crop to the phrase. Small UI floating in
empty space is the fastest "AI edit" tell. Never invent numbers or results to decorate a claim. Use each B-roll
scene once per video. Never click "Accept" on cookie/terms dialogs while filming; close them.

## Sound (`"sound": "soft"`, the reel default)

- Sound follows **visible actions**, not every cut: a soft air move on a real layout change, a damped tap when a
  card or logo lands, a dry click for small UI, one short warm tone for a check or payoff.
- No laser zaps, pitch-drop plops, sci-fi chirps, risers/booms, or a whoosh on every cut. Those read as cheap.
- Music bed ~12 dB under the voice (range 9-14), ducked under speech; sfx.py measures and sets it.
- Master near -14 LUFS, true peak at or below -1 dBTP, **measured on the delivered file**. Never fade the last word.

## Story shape for a reel

1. Hook in the first 3 seconds: a claim or command that names the tool or person.
2. One line of credibility or context.
3. If there's a list, show all items early (an open loop), then one shot per item.
4. Each item: a one-line definition, two or three literal visuals, a punch-in on the key line.
5. Resolution that calls back to the hook visual.
6. CTA: show the resource first, then the face with the one action.

## Open loops

Leave something visibly incomplete in the hook and close it before the CTA (empty slots that fill, a ghosted
result that resolves). One main loop at a time. A recurring object that doesn't change state is a callback, not a
loop. Never "wait for it" or withhold the basic topic.

## The note loop

When the user gives a note, fix the edit AND write the note into a rule (`rules.py add`), so they never give the
same note twice. That loop is what made these defaults good.
