# The Character Iterator — how a rounded avatar is grown

The iterator is the calculator this repo builds. It takes the question
database and produces a person-shaped set of answers.

## Inputs

- `questions/questions.jsonl` — every question with its poles, its
  provisional winner shading (`winner_lean`, `spread`), and whether a
  coach may nudge it.
- A **mode** — `show`, `coach`, or `both`. Mode biases categories:
  show mode pushes premise, spectacle and showmanship questions toward
  the high-energy poles; coach mode pushes think-aloud, caution and
  interruptibility.
- **Coach nudges** — plain instructions from the player ("braver",
  "funnier", "quieter during hard bits") translated by the
  `coach_player_coach_nudge` skill into category biases with amounts.
  Nudges move the sampling centre. They never touch `nudgeable: false`
  questions (the rails).
- A **seed** — so a character is reproducible and diffable. Same seed,
  same inputs, same character.

## Algorithm (v0, deliberately simple)

For each question:
1. Start at `winner_lean` — where successful creators cluster.
2. Apply mode bias, then nudge bias (points on the 0 to 100 scale).
3. Sample a position from a distribution centred there, with width
   from `spread` (narrow 6, medium 12, wide 20 points, clamped).
4. Clamp to 0 to 100. Record the value *and* the forces that produced
   it (base, mode shift, nudge shift, sampled offset), so the player
   can see exactly why their avatar is the way it is. Legibility is
   a product requirement, not a debug feature.

Then compute the familiar dials (chattiness, boldness, caution,
humour, showmanship) as means of their question categories, and write
a character sheet: dials first, then the strongest leans (answers
furthest from 50) as plain-language traits, then the full answer
table in a details section.

## Why this produces roundness, not a clone

- No creator's answer set is ever loaded. The centre of the
  distribution is an *aggregate* across the roster, per question.
- Sampling means two runs with different seeds differ the way
  siblings differ — same upbringing, different person.
- Nudges make the coach a genuine authorial force without letting
  them (or the system) paste a real person's sheet over the avatar.

## Evolution across sessions

After a session, the debrief skill proposes *answer changes*, not
free-text personality rewrites: "risk-004 moved 62 → 74, because the
avatar attempted the tight line three times and narrated it first."
The owner rules on each proposed change. Approved changes update the
character's stored answer set, which becomes the sampling centre for
that character next time — nudges from play, permanence by ruling.

## Tool

`tools/iterator.py` implements v0 (stdlib only). `tools/validate_questions.py`
checks the database: schema, unique ids, and a flatness report that
flags questions whose `winner_lean` sits near 50 with a narrow spread
(the coin-flip smell) for re-aiming or pruning.

## Standing correction (2026-10-14) — read docs/FRONTIER-AND-TASTE.md

The sampling-centre method above produces an *average* character.
Casey ruled that out as a finished product: the average is slop and a
single-creator aim is a clone. Iterator v0 is therefore a floor-test
and diagnostic instrument only. The production path is: iterator
answer set → frontier gap loop against the field until the
professional gate → tastemaker deviations, recorded with reasons.
Do not ship an averaged character as Our Guy.
