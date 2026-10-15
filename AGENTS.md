# AGENTS.md — Coach Player

A coachable auto-player for games: an avatar plays and renders the
funness; a human coaches at strategy level. Personality is developed
from patterns across many creators — never cloned from one, never
averaged into slop. Audience: clever middle-schoolers learning to
steer an agent.

## Read order

1. This file.
2. `ONBOARDING.md` — architecture, repo map, question DB, open lanes.
3. `docs/DESIGN-COMPARISON.md` — the build spec (M0 shipped, M1 next)
   and the five open rulings.
4. The lane doc for your task (`docs/MAKER-LANE.md`,
   `docs/FRONTIER-AND-TASTE.md`, `docs/QUESTIONS-FIRST.md`,
   `docs/SCRIPT-FIRST.md`) + the matching `skills/*/SKILL.md`.

## Hard rules

- **Copyright:** codex entries are paraphrased patterns only. Brief
  quotes only (~50 words max per work, total, ever). No substantial
  transcript text in this repo. No creator catchphrases collected
  for copying.
- **Transcripts never get committed.** Raw transcripts live only on
  the owner's machine in `codex/transcripts/` (gitignored).
- **Private/public boundary:** per-artist dossiers and per-creator
  shadings go in the PRIVATE repo `SuperInstance/coach-player-artists`.
  Patterns, questions, aggregates go here (public by default —
  pushes are timestamps).
- **The owner's calls are the owner's:** the five rulings in
  `docs/DESIGN-COMPARISON.md`, roster approval, library promotions,
  and avatar sheet changes. Propose; never decide.
- **Sheet diffs are proposed, never self-applied:** write them to
  `avatar/proposed.md`; `avatar/SHEET.md` changes only on the
  owner's ruling.
- **Verify before claiming:** run `tools/validate_questions.py`
  before committing questions; declare your sampling `method` in
  every codex entry; a declared fallback beats a quiet one.

## Claiming protocol

Before starting a lane: read `CLAIMS.md` **and** recent `git log`.
Mark your lane **CLAIMED** (name + date) in your first commit.
On finish, mark **DONE** with a pointer to the result. Abandoning a
lane: set it back to OPEN with a note on where you stopped.

## Where things live

Questions: `questions/questions.jsonl` (inbox staging in
`questions/inbox/`). Evidence: `codex/entries/`. Rosters:
`codex/ROSTER-PROPOSED.md`, `codex/ROSTER-MAKER-LANE.md`. Avatar:
`avatar/SHEET.md`. Tools: `tools/` (validator, iterator, gap
report). The running game/runtime is the sister repo
`SuperInstance/shoalwater`.
