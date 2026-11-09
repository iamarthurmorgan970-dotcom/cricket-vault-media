# True Scale: how to make an episode

True Scale is Deepak's faceless long-form YouTube channel (8-10 minute geography, history and travel facts,
animated maps and charts, AI narration). This file is the standard every episode must meet. The weekday
scheduled task follows it; so should anyone making an episode by hand.

## The standard

- **One subject per video.** Each plan item is one video. Never merge several plan items into one.
- **Length 8-10 minutes.** About 1,100-1,250 narration words over 14-20 scenes, plus short holds.
  Check with `python3 true-scale/make.py minutes episodes/<slug>` before rendering; add a "hold" (seconds) to
  scenes in script.json, or a sentence or two, if it's under 8.0.
- **Accuracy beats everything.** Every number and claim must come from a source you fetched and read this run
  (Wikipedia, UNESCO, government sites, NOAA/NASA, Britannica, major outlets, Indiahikes for trek basics).
  Round honestly ("about 3,800 m"). If sources disagree, say so on screen ("estimates range from..."). For
  "largest / first / only" claims that are disputed, say "often described as". Never invent a figure.
  Trek days and difficulty vary by operator: give ranges and say "typical itineraries".
- **India's map.** Any map of India must use India's official boundary (`engine.india.INDIA_POV`, Natural
  Earth India point of view) with state lines from `engine.india.ST`. Never show India with the default
  international outline.
- **Hook in the first 20 seconds**: the single most surprising verified fact, shown on screen, then the
  promise of the video. End with a comment prompt ("which would you pick?") and "subscribe to True Scale".
- **Structure for comparisons (Trek vs Trek, X vs Y)**: what each is, side-by-side numbers (altitude, days,
  distance, best months, difficulty), what makes each special, then "pick A if..., pick B if...".
- **Structure for "Why you should visit"**: where it is (map zoom), the wow fact, how it formed or its history,
  3-5 reasons to go, how to get there and when, one honest caveat (permits, season, crowds, fragility).
- **Same brand**: dark navy maps, amber/cyan/pink/green accents, Poppins font, "TRUE SCALE" corner mark,
  male narrator `am_michael` (Kokoro), original synthesised music (built into make.py).

## Files

```
true-scale/
  make.py              # setup | tts | stills | render | assemble | all | minutes
  engine/core.py       # Scene: camera, world maps, highlight, mover (true-size moves), bars, text, headline
  engine/timeline.py   # TL: zoomable time axis, markers, spans, brackets (see episode 002)
  engine/extras.py     # myth cards, city dots, latitude lines, rivers, lakes, peaks_chart (mountains to scale)
  engine/india.py      # India states + official boundary, india(), pin(), place(), card(), state_tag()
  episodes/<slug>/     # script.json + scenes.py (+ out/thumbnail.png, out/upload-details.txt)
  content_plan.json    # the queue of upcoming episodes
```

Episodes 001-004 are working examples of every helper: 001 true-size moves, 002 timelines, 003 myth cards and
city dots, 004 India place zooms and the peaks chart. Copy their patterns.

## Making an episode

1. `python3 true-scale/make.py setup` (downloads map data and the voice model; a few minutes on a fresh machine).
2. Research. Collect every fact with its source URL.
3. Write `episodes/<slug>/script.json`: `[{"id": "s01_hook", "text": "..."}, ...]`. Ids are valid Python
   names. Write numbers as words when they're read aloud ("three thousand eight hundred metres") so the voice
   reads them naturally. Avoid symbols in narration.
4. Write `episodes/<slug>/scenes.py`: `from engine.core import *` (plus timeline/extras/india as needed) and one
   function per scene id. Time animations to narration with `S.c("phrase")` (the phrase must appear verbatim in
   that scene's text). Optional `def hold(sid): return seconds` for extra time at the end of scenes.
5. `python3 true-scale/make.py tts episodes/<slug>` then `make.py minutes ...` (aim 8.0-10.0).
6. Check layout: `make.py stills episodes/<slug> <scene_id> <t>` for the busiest moment of every scene, and LOOK
   at the PNGs. Fix overlaps, clipped labels and text running off screen. Poppins has no arrows (use words or
   ":"); ×, ≈, ², …, – are fine.
7. `make.py render episodes/<slug>` then `make.py assemble episodes/<slug>`. Look at `out/contact-sheet.png`.
8. Thumbnail `out/thumbnail.png` (1280x720): 2-4 huge words + one bold visual (see episodes/00x/thumb.py, run from the episode folder; copy
   their style), no small text. Must be honest about the content.
9. `out/upload-details.txt`: 3 title options (curiosity, specific, no clickbait lies), description with the
   comment prompt, chapters from `out/chapters.txt` renamed to human titles, sources list, tags,
   upload notes (Category Education or Travel & Events; Made for kids: No).

Large files (audio, video, out/*.mp4, stills, check) are git-ignored; commit script.json, scenes.py,
out/thumbnail.png and out/upload-details.txt.
