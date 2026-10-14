# Maker Lane — Engineering Teachers family (build-001 to build-015)

Mined 2026-10-14 at hypothesis grade (all `winner_lean` null).
Transcripts were unavailable this round (API plan), so every
question here is aimed from the engineering perspective and its
`evidence_needed` names the teacher channels whose videos would
settle it: Code Monkey, DevWorm, Goodgis, Farhan Aqeel, NOBL Games.
The family's shared ground: these are people who build games in
public, step by step, so their construction choices are on camera
in a way a pure performer's never are. The questions therefore
split into two kinds — how they *build* (architecture, tuning,
pipelines) and how building changes how they *see* a game while
playing it.

**Merge note for whoever lands this file:** the questions use
`mode: "maker"` per docs/MAKER-LANE.md, but
`tools/validate_questions.py` currently only accepts
show/coach/both and flags the nine maker-mode lines. The
validator's mode set needs "maker" added before merge; the
questions themselves are schema-complete.

## Top 5

1. **build-008 — construction-reading.** The Maker Lane's
   signature question. While playing someone else's game, does the
   commentary run on the fiction or on the probable build — state
   machines guessed, trigger volumes spotted, recycled systems
   named before they fire? It discriminates hard inside this
   family: a design-forward maker like Goodgis reads construction
   aloud constantly, a tutorial-scale builder reads it when it
   breaks. And it is the avatar's single fastest skill for entering
   a new game, which makes it behaviour-changing by definition.
2. **build-001 — architecture first vs hack first.** The founding
   split of the whole family. Code Monkey's channel is essentially
   an argument for designed, reusable systems; the jam-and-devlog
   end of the family argues by shipping. It predicts how a maker's
   game behaves at its edges, how their series age, and how much of
   their process is even imitable by a learner.
3. **build-003 — physics tuning, numbers vs feel.** Gravity and
   jump arcs are either computed or surfed, and teachers say which,
   on camera, while choosing the constant. It transfers directly to
   play: numbers-first physics can be learned exactly by the
   avatar, feel-first physics has to be ridden. Nudgeable, because
   a coach should be able to ask the avatar to trust a game's
   physics more, or less.
4. **build-013 — mechanic origin, feel-first vs trick-first.**
   Does the mechanic start as a player-feel goal the code must
   serve, or as a neat technical trick looking for its fun? Origin
   predicts fairness: feel-first mechanics read as intentional,
   trick-first mechanics produce the happy accidents. It also
   separates the design-forward teachers from the feature-first
   ones more cleanly than any topic label does.
5. **build-006 — performance budget, day one vs when it hurts.**
   Wide spread by temperament and by studio size: pooling and
   profiling as a habit versus optimisation as an emergency.
   NOBL Games' studio process against solo tutorial builds should
   land far apart. It matters to a show avatar because it predicts
   whether a game's biggest moment will hold together or fall
   over — which is when the avatar most needs to know.

## Dropped as flat (candidates considered, not shipped)

- **"Does the teacher explain while coding or narrate afterwards?"**
  Near-universal explain-while-coding across tutorial channels —
  it describes the format, not the builder. Medium fact, fails the
  discrimination test.
- **"How much formal testing (unit tests, automated checks) does
  the build use?"** Almost the entire family clusters at the low
  pole; tutorial and devlog culture tests by playing. One cluster,
  no shading — a property of the medium.
- **"Engine-native tools vs third-party assets from a store?"**
  Answers track sponsorship and video topic more than builder
  character, and flip within a single channel month to month.
  Measuring noise.
- **"Are variables and systems named for learners or for the
  builder?"** Real, but it collapses into build-008's family
  (how much of the build is performed for an audience) and added
  no independent discrimination in this family.
- **"Solo build vs team build?"** Categorical, not a spectrum, and
  inside this family it is mostly a fact about the channel, not a
  behaviour that shades.
