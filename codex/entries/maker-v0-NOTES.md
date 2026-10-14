# Maker codex v0 — method notes

First maker-lane sample, 2026-10-14, via the browser route
(TranscriptAPI plan exhausted; see docs/DESIGN-COMPARISON.md era
notes in MEMORY for the route tests).

Sample: Juniper Dev, "I Made A Roguelike Game About Beavers"
(OsfylQuaYSE, published 2026-04-29, 12:49). The game is "Dam",
a beaver roguelike built as a four-person course final.

METHOD CAVEAT — read before trusting granularity: the watch
page's "Show transcript" panel never loaded for this video
(infinite spinner across six attempts, including reloads). The
worker fell back to reading the player's auto-captions at
~25-second intervals plus viewer timestamp links. Entries are
therefore coarser than the API-era samples (timestamps are
approximate, wording is caption-level) but the decisions and
their order are faithfully covered. The panel route is thus
proven-but-flaky per video; the caption fallback is the standing
backup and must be declared in the `method` field, as here.

Strongest patterns (worker synthesis, paraphrased):
1. Feel-first communication — state and identity conveyed
   through atmosphere and visuals (dimming light for time,
   off-centre UI for art) rather than numbers and menus.
2. The team as a design instrument — recruiting specialists,
   art integrated early as morale infrastructure, read-before-
   you-write discipline; the post-mortem targets process.
3. Small proven tools, tight loops — quota/route core loop,
   dictionaries for data, single-item modifiers for variety.

Questions this sample bears on (provisional, single video):
- maker-011 (fun in the 30-second loop vs the long arc): the
  quota + route-optimisation loop is the whole design spine —
  leans loop, with the run structure as the arc's servant.
- maker-005/006 (playtest stance): the post-mortem names
  untested siloed mechanics as the project's core failure —
  evidence that this maker prices playtesting as process, not
  polish.
- design-007 (find the load-bearing trick first): the trick
  here (quota pressure making procedural runs legible) was
  settled in the first minute of design talk.
No shadings updated yet — one video, caption-grade evidence.
