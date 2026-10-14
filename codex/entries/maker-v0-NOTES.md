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

Second sample (2026-10-14): CodyCantEatThis, "Can AI Make A
Better Game Than Me?" (kRSB-Y3kT7g, published 2026-10-10,
18:43) — his first upload after ~2 years away. The panel failed
again (two attempts, spinner), so: caption fallback again.
RUNNING METHOD TALLY: panel succeeded 1 of 3 maker-route
videos (the Gray test); the caption fallback is the de facto
workhorse and its entries have held up in quality.

The video is a controlled experiment: a 3D platformer built
twice, once by a new ChatGPT model, once by Cody. His verdict
favours the human build. Patterns:
1. Scope as experimental control — both builds kept small and
   parallel so the comparison stays fair; he scopes to learn.
2. Judgement by intent and feel — the only AI work praised
   shows intent (area transitions); condemned work is
   purposeless (dead areas, dull corridors). Ugly-but-good
   beats polished-but-empty.
3. Design-first, tools-second — AI welcomed for asset
   production where he admits weakness (art, effects, sound),
   never for design decisions; prompting itself iterated as a
   design skill (full-context feeds after stalling).

Bears on (provisional): design-007 again — his own build is
anchored on ONE core mechanic (collectibles change the world's
state) chosen before implementation; maker-003's neighbour —
an AI's purposeless output is read as failed design, not
failed execution; and directly on the Coach Player author
layer: a maker's field evidence that an LLM's game output
without a prior design reads as a testing scene, not a game.
Still no shading updates — two videos, two makers, both
caption-grade.

Third sample (2026-10-14): Goodgis, "Finishing My Indie Game
After 6 Years" (WNYE69ZITB8, published 2026-06-01, 6:27) —
the panel WORKED this time (first attempt; the video is
auto-dubbed, panel text is the English dub track). Panel
tally now 2 of 4. The game is Dewdrop Dynasty, a lighthearted
Metroidvania, six years in the making. Patterns:
A. Tune-by-feel iteration — completion criteria are sensory
   (the world "feels alive", the game gains "soul"); multiple
   passes plus trusted feedback over formal metrics.
B. Tools-over-hacks architecture — rotting systems (cutscene
   if-chains) trigger paradigm learning and a reusable
   data-driven engine, not patching. Note the shape: each
   cutscene beat is a small composable unit — tile-like.
C. Honest, restrained self-marketing — no fabricated trailer
   shots, bosses unspoiled, feedback from a tight trusted
   circle; credibility is the asset.

Bears on (provisional): maker-005/006 again, differently —
his feedback loop is friends/family on PRESENTATION material,
not playtesters on systems; build-00x tooling questions (the
cutscene engine is build-the-tool-when-the-hack-rots, with a
named trigger); maker-011 sideways — the fun bar is
experiential ("alive"), resistant to the loop/arc framing.
Cross-maker echo worth watching: Juniper's feel-first
communication and Goodgis's tune-by-feel are cousins; Cody's
feel-over-polish judging makes three feel-forward makers in
three samples. Still no shading updates.

Fourth sample (2026-10-14): Jack Sather, "The Most Unique
FPS You'll Play This Year — MOUSE: P.I. For Hire"
(UhPJEY7DYn8, published 2026-04-16, 9:18) — first design-
ANALYST sample. Panel worked (tally 3 of 5). Caveat: the
video is sponsored (#ad, publisher PlaySide), disclosed by
Sather up front; flagged in the entries since praise may be
shaded — his METHOD is the evidence we want, and it is
unaffected. His method, as a reading discipline:
1. Find the load-bearing constraint — here, ammo scarcity;
   every other system (rotation, movement, pacing) is read as
   downstream of that one pressure point. This is design-007
   demonstrated as a reading skill, i.e. what build-008 wants
   the avatar to do while playing unfamiliar games.
2. Judge by cadence and craft density, not feature counts —
   reward staging over time, variety extracted from a limited
   palette, animation effort as the visible signature of
   intent.
3. Evidence = his own felt response — lineage comparisons,
   the urge to savour an animation, perceptual after-effects
   of hours in monochrome. Subjective experience used as a
   calibrated instrument.
The feel-forward echo now spans all four makers AND the
analyst lane: feel is the verdict currency across the maker
perspective so far. If Indie Game Clinic and Code Monkey
confirm, the wave's aggregate should propose it as a
maker-lane law and a candidate template for the avatar's own
game-reading.
