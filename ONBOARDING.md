# Onboarding — Coach Player

Read this first if you are new here, human or agent. It tells you what
this project is, how the pieces fit, the rules that are not negotiable,
where the work stands, and which work is open to claim. Deeper doctrine
lives in `docs/`; this file is the map, not the territory.

Companion files: `AGENTS.md` (the short version + hard rules) and
`CLAIMS.md` (who is working on what — read it before starting anything).

---

## What this is

Coach Player is a coachable auto-player for games. An avatar plays the
game moment to moment and renders the *funness* of that play —
commentary, pacing, risk flair — while a human coaches it from one level
up, the way you think strategy in an RTS: short orders, dials, and
interruption, never frame-by-frame inputs.

The avatar's personality is *developed*, not copied. It studies patterns
from many strong game creators — never cloning any one of them (the
original stays ahead of any copy, and it is not ours to take) and never
averaging the field into a homogeneous blend (the average is slop; it
has no edge). Patterns aggregate across creators before they become
traits. The end state of the study loop is a frozen, deliberately
tasteless **Professional Template**; only then does a human tastemaker
give it its edge. Professional level first, choices second.

Audience priority: **clever middle-schoolers** — not talked down to.
The real curriculum is learning to nudge an agent into being who you
want it to be: give an order, watch what changed, notice what did not,
adjust. Coaching and personality-shaping are the skill being taught,
so nudges must be legible: every order shows which dial moved, which
trait fired, what the avatar remembered. Doctrine: `README.md`,
`docs/FRONTIER-AND-TASTE.md`, `docs/QUESTIONS-FIRST.md`.

---

## The architecture — script-first

The runtime stack, bottom to top (full doctrine: `docs/SCRIPT-FIRST.md`;
the research behind it: `docs/STUDY-MINECRAFT-AGENTS.md`):

1. **Motor — scripts.** Finished, tested behaviours that drive the
   *same input object a human player drives*. No special physics, no
   cheating state. A script is code that has been verified against
   game state.
2. **Tiles.** A script (or tight script chain) exposed upward as ONE
   named choice the size of a human intention — "work the shoal",
   "hunt the pot" — the way a fighting-game button means *punch*: the
   player never thinks about the mechanics underneath. Tiles are
   *projected* from the codex work: studying expert play reveals the
   lower mechanics players actually execute, and those crystallise
   into the tile vocabulary. A tile graduates only by the
   **light-switch test**: the coach uses it for something else and
   forgets the wiring entirely — switch and light are one. Granularity
   rule: a tile is an intention, never an input, never a campaign.
3. **Overseer — Jev judges.** Cheap judges running constantly,
   scoring the questions that matter: does an existing tile fit this
   situation, and how confident are we? Which tile? Is the current
   tile failing? Is this interruption worth more than the plan? Most
   ticks, only this layer thinks, and it thinks in percentages at a
   tiny price. Its most important verdict is **"none of these are
   good enough."**
4. **Author — the LLM, in rare budgeted pulses.** Only on the
   overseer's none-fit verdict does the system call a big model to
   write a new script. The call is not cold: the question graph
   projects into it, so the author starts from hundreds of shaded
   questions about this situation instead of a blank prompt. A new
   script that verifies joins the library permanently — the LLM works
   itself a little further out of a job with every success. The
   library is pruned, with reasons recorded; it never grows
   unbounded (that is Voyager's failure mode, studied in
   `docs/STUDY-MINECRAFT-AGENTS.md`).
5. **Coach — the human.** Sets the day's intent, nudges the avatar's
   dials, and grabs the wheel in the *keyholes* — tight first-time
   passages where no overseer should be trusted to react in time.
   The coach never composes mechanics; the coach coaches.

**The A-plan model.** A session follows Casey's Sitka trolling day:
before the day begins there is a complete default route worth running
uninterrupted. Interruptions (a strike, a tip, a better opportunity)
are scored by the overseer; the plan bends toward the better option
*through* the highest-value water — never a beeline that wastes the
water in between, because every hour counts. As the situation
tightens, the planning horizon shortens — an hour, ten minutes, five
— until the keyhole, where the human drives by design.

Three product layers sit on this stack and stay separate (module, not
brain): **Pilot** plays (same input object as a human), **Personality**
renders the funness (sheet, dials, commentary), **Coach** is the
human's seat. See `README.md`.

---

## Repo map

```
README.md               The concept, audience, three layers, V0 spec.
ONBOARDING.md           This file.
AGENTS.md               Short rules + claiming protocol for agents.
CLAIMS.md               Lane board: OPEN / CLAIMED / DONE.
docs/
  QUESTIONS-FIRST.md    Why questions shape the system more than answers.
  FRONTIER-AND-TASTE.md The frontier loop; clone and average both banned.
  SCRIPT-FIRST.md       The runtime stack (motor/tiles/overseer/author/coach).
  STUDY-MINECRAFT-AGENTS.md  Mineflayer, Voyager, STEVE-1, Mindcraft — what each proves and lacks.
  QUESTION-GRAPH.md     How questions cluster; the visual track note.
  ITERATOR.md           How the character iterator answers the database.
  MAKER-LANE.md         The game-making/design lane doctrine.
  DESIGN-COMPARISON.md  The two blind V1 designs, the synthesis, M0/M1/M2, the five open rulings.
  design-lanes/         The two raw V1 design submissions (minimax, claude), filed verbatim.
codex/
  README.md             The codex entry schema.
  ROSTER-PROPOSED.md    Player/show rosters (Show core, Coach core 8 + Phase 2) — PROPOSED, owner's ruling pending.
  ROSTER-MAKER-LANE.md  Maker-lane roster (devlogs, design analysts, engineering teachers) — PROPOSED.
  entries/              The evidence: show-mode-v0.jsonl, coach-mode-v0.jsonl,
                        maker-v0.jsonl (+ maker-v0-NOTES.md), AGGREGATE-v0/v1/v2.md,
                        AGGREGATE-maker-v0.md, and inbox/ staging sets.
  transcripts/          RAW TRANSCRIPTS. Local only, gitignored. Never commit, never quote from here into the repo.
questions/
  questions.jsonl       THE question database (271 questions). See below.
  inbox/                Mined question sets land here first (one file per lane + NOTES.md);
                        the merge step validates, renames colliding ids, appends survivors.
skills/                 Ten granular skills, one job each (SKILL.md + skill.yaml per folder):
                        roster_curator, codex_sampler, question_miner, jev_shader,
                        character_iterator, frontier_gap, tastemaker, coach_nudge,
                        session_debrief, evidence_checker.
avatar/
  SHEET.md              The avatar's sheet: dials, owned commentary moves, guardrails.
                        (memory.md / sessions/ / proposed.md are the planned folder shape —
                        see "Avatar sheet evolution" below; only SHEET.md exists so far.)
characters/             Iterator outputs — generated avatar sheets (e.g. sparrow-seed7.md, a test artifact).
profiles/               Field shading profiles built from codex evidence (currently hypothesis grade).
tools/
  validate_questions.py Schema + flatness check for the question database. Run it before committing questions.
  iterator.py           Grows a rounded avatar by answering the database (stdlib only).
  gap_report.py         Compares an avatar's answers against the field frontier, per question. Never averages.
```

The sister repo is **SuperInstance/shoalwater** — the host game where
the runtime actually lives and plays (`docs/coach/` there: adapter,
tiles, judges, overseer, session runner; `docs/demo.js` is the page's
demo choreography over the same core). This repo is the brain and the
evidence; shoalwater is the boat.

---

## The question database

`questions/questions.jsonl` — one JSON object per line, 271 questions.
**We are shaping the system based on the questions more than the
answers.** Answers expire and clone; questions compound and shape
(`docs/QUESTIONS-FIRST.md`). A question earns its place only if it is
a spectrum with two named poles, discriminates between successful
creators, is not a coin flip, moves behaviour, and can gather evidence.

### Schema (enforced by `tools/validate_questions.py`)

| Field | Meaning |
|---|---|
| `id` | Stable unique id, `<prefix>-<NNN>` (e.g. `premise-001`, `show-013`, `over-007`, `visual-004`). |
| `category` | The trait family it probes (`premise`, `failure`, `risk`, `spectacle`, `overseer`, `tiles`, …). |
| `question` | The question itself, phrased so answers land on the spectrum. |
| `pole_low` | What 0 means, in words. |
| `pole_high` | What 100 means, in words. |
| `why` | Why the answer moves behaviour — a question whose answer changes nothing is trivia. |
| `winner_lean` | 0–100 estimate of where the *winners* (best-in-field) sit on this spectrum — or `null` when no creator shading exists yet (design, overseer, and visual questions are null; the iterator skips nulls). |
| `spread` | How widely creators distribute: `narrow`, `medium`, or `wide` (the iterator reads these as standard deviations 6 / 12 / 20). |
| `nudgeable` | `true` if a coach may move this live. `false` marks a rail — nudges never move rails. |
| `mode` | `show`, `coach`, `both`, or `maker` — which lane the question belongs to. |
| `status` | `hypothesis` until timestamped evidence graduates it. |
| `evidence_needed` | What evidence would shift the estimate. Unfalsifiable questions belong in docs, not here. |

### Shading rules (Jev)

- A **shading** is a judge's percentage estimate of where a creator
  (or our avatar) sits on a question, Jev-style: a real percentage
  with evidence behind it, not an exact fifty-fifty shrug.
- **A shading at exactly 50 is legitimate ONLY as a documented
  evidence split** — the evidence genuinely pulls both ways — **with
  a named tie-breaker**: the observation that would settle it. A bare
  50 with neither is not a judgment; re-aim or gather more evidence.
- Shadings start as hypotheses. Per the shading workflow, a shading
  is provisional until segments from different videos agree, and **a
  behaviour is a trait only if it survives a format change** (the
  aggregate rule from the codex waves).
- **Flat questions:** the validator flags every question whose
  `winner_lean` sits at 45–55 — currently **29** of them. A question
  that keeps returning a coin flip is badly aimed or measuring noise:
  re-aim it at a situation that distinguishes, or prune it with the
  reason recorded. Pruning is real work, done in the open.

### Adding a question

1. Mine with the `coach_player_question_miner` skill; land the set in
   `questions/inbox/<lane>.jsonl` with a `<lane>-NOTES.md` beside it.
2. The merge step checks the schema with
   `python3 tools/validate_questions.py`, renames colliding ids, and
   appends survivors to `questions/questions.jsonl`. Inbox files
   stay in place as provenance.
3. Run the validator on the merged database before committing. It
   must print `OK`.

---

## Evidence + copyright rules (hard — not guidelines)

These bind every contributor, human or agent, in every lane.

- **Codex entries are paraphrased patterns only.** An entry records
  trigger → move → timing → what it reveals, in your own words
  (schema: `codex/README.md`; worked examples: the `*.jsonl` files in
  `codex/entries/`). Patterns, never people.
- **Brief quotes only: at most ~50 words from any one work, across
  everything you ever file.** No substantial quoted transcript text
  in this repo, ever. No exceptions for "just one long excerpt".
- **Raw transcripts never enter this repo.** They live only on the
  owner's machine under `codex/transcripts/` (gitignored). If you
  obtained transcript text to do your sampling, it stays there.
- **No creator catchphrases or signature lines are collected for
  copying.** No impersonation, no likeness as product. A creator's
  name appears for provenance only.
- **Private/public boundary:** detailed per-artist documentation
  (dossiers, per-creator shadings) goes in the **private** repo
  `SuperInstance/coach-player-artists`. Patterns, questions, and
  aggregates go **here**. Nothing that reads as a recipe for copying
  one person goes public.
- **Public by default:** this repo is public on purpose. Pushes are
  timestamps — prior art on a third party's clock — and the push
  history reads as the story of the development. Secrets (keys,
  credentials) never go public, here or anywhere.

---

## Where the build stands

Two independent fleet designs were written blind against the same
brief, critiqued themselves, and were synthesised in
`docs/DESIGN-COMPARISON.md` — read it; it is the build spec. The
merged order:

- **M0 — SHIPPED** on Shoalwater and live
  (https://superinstance.github.io/shoalwater/). Fixed-step sim core
  extracted so browser and headless runs are byte-identical;
  fail-closed terrain adapter; the first tiles (make-way,
  work-the-shoal, hunt-the-pot, wreck-look) under the overseer with
  calibration bands, hold-count exits, a shadow author, and four
  control judges; session story + trace logs. The page demo flies
  the full mission; headless mission tests complete all six
  objectives at a working tide and fail honestly on a dry bar.
- **M1 — next.** Intention registry (misfit becomes structural: an
  intention with no claimant is a fact, not a percentage), label
  store + counterfactual replays (fit becomes an empirical rate),
  the coach surface (tile chips the coach presses, intent strip,
  order interpreter into a closed vocabulary — model prose never
  reaches the kid), and an offline authoring proof on the film
  wreck, then one live end-to-end session.
- **M2 — after M1.** Via-point routing on the computed value field
  (with the falsifiability assertion), hunting without the
  exact-coordinate cheat, creep-in with flair envelopes, first
  calibration gate, first graduation ruling, first threshold sweep.

### The five open rulings — the owner's calls

From `docs/DESIGN-COMPARISON.md`. Defaults exist for all five and
none of them gates building — but **agents do not decide these**:

1. **Prices** — the point values every plan-bend spends (shoal 30,
   pot 100, home 40, wreck 50, hull hit −60, reserve spent −25,
   taking water −200).
2. **In-session authoring for kids** — automatic, or behind an
   "ask me first" chip?
3. **Models + daily spend cap** per avatar, for the author and the
   order interpreter.
4. **Two-tier library ownership** — confirm: a core library ruled
   by the owner; a per-avatar library ruled by its kid.
5. **Privacy/consent review** — required before any public release
   involving minors (the order interpreter sends kid-typed text to
   an LLM).

Also pending the owner, same status: the roster ruling (Show core,
Coach core 8 + Phase 2, in `codex/ROSTER-PROPOSED.md`), the
Tesseract pick in the maker roster (@TesseractDev vs
@TesseractGames), and the avatar's name and temperament seed.

---

## Open work lanes (claimable)

Claim a lane before you start — protocol below. Everything here is
real, scoped work; none of it needs the owner's ruling first.

### Maker wave 2 — second videos + the unsampled roster

Wave 1 (six makers, one video each, 52 entries, aggregate in
`codex/entries/AGGREGATE-maker-v0.md`) is hypothesis grade. Wave 2:

- **Second videos** for Juniper Dev, CodyCantEatThis, Goodgis, Jack
  Sather, Code Monkey, Indie Game Clinic — the graduation path: a
  pattern from wave 1 either survives a second video (and ideally a
  format change) or gets demoted in the aggregate.
- **First samples** for the rest of `codex/ROSTER-MAKER-LANE.md`:
  Barji, Its Rascal, NathanOnDev, Zoteling, RookieDev (devlogs);
  Game Design Library, The Game Overanalyser (analysts); DevWorm,
  Farhan Aqeel, NOBL Games (teachers).

Method (the TranscriptAPI plan is exhausted; this is the working
route): use the **signed-in browser** on the video page. Try the
transcript panel first (description → "Show transcript") — two
honest attempts, one reload. If the panel won't load, fall back to
reading the player's auto-captions at ~25-second intervals.
**Declare the method in every entry's `method` field — never
silently.** One video per browser session. **Never sample a video
the day it drops** (captions aren't ready). File paraphrased entries
in `codex/entries/` in the maker format, update the wave NOTES, and
extend the aggregate — flagging sponsored content when you meet it.

### The 29 flat questions

`python3 tools/validate_questions.py` lists them (winner_lean
45–55). For each: re-aim it at a concrete situation that separates
creators, or prune it with the reason recorded in the question's
history. Either outcome is progress; leaving them flat is not.

### The visual track

`visual-001` … `visual-012` — how the picture is built (cut pace,
zooms, on-screen text, thumbnail grammar) — sit unshaded with
`winner_lean: null` because the evidence is frames, not transcripts,
and **frame tooling does not exist yet** (see
`docs/QUESTION-GRAPH.md`). The lane: build a small frame-sampling
tool, sample roster videos' frames + thumbnails, and shade the
twelve. The visual track is learned separately from the audio track
on purpose — do not try to answer these from transcripts.

### The Professional Template

Unbuilt. The loop is `docs/FRONTIER-AND-TASTE.md`: profile the
field per question from timestamped evidence, profile Our Guy,
iterate on the gaps (largest first, never the mean) with
`tools/gap_report.py`, and freeze the answer set that meets the
professional floor on every metric. Know the floor test for what it
is: aiming the question database at one creator produces a knock-off
and aiming it at the centroid produces slop — both are useful *only*
as proof the questions have power. Neither is the product.

### Avatar sheet evolution

`avatar/SHEET.md` is the seed sheet (dials: chattiness 6, boldness
5, caution 5, humour 6, showmanship 6 — all provisional; the avatar
is unnamed). The rule is the **owner rite**: after sessions, the
avatar *proposes* sheet diffs ("I got braver", "I talk too much
during hard bits") and the owner approves, edits, or rejects each.
**Write proposed diffs to `avatar/proposed.md` (create it when the
first diff exists); never edit SHEET.md to apply your own proposal.**
Nudges are temporary and expire with the session; ruled edits are
permanent. Guardrails on the sheet are not nudgeable, ever.

---

## How to work here

- **Verify before claiming.** Run the validator before committing
  questions; run the relevant test suite before saying a build
  works; cite timestamps and video ids in evidence. If your route
  failed (a transcript panel that never loaded), say so in the
  entry's `method` field — a declared fallback beats a quiet one.
- **File results in the existing formats.** Codex entries as
  `.jsonl` in `codex/entries/`, aggregates as `AGGREGATE-*.md`
  beside them, mined questions through `questions/inbox/`, sheet
  proposals in `avatar/proposed.md`. Match the field names of the
  file you're appending to.
- **Commit messages say what + why.** The push history is the
  project's public story; write like it.
- **Claiming protocol.** Before starting a lane: read `CLAIMS.md`
  *and* the recent `git log` (a claim lands in a commit, so the log
  is the freshest board). Mark your lane **CLAIMED** with your name
  and date in your first commit. When you finish, mark it **DONE**
  with a pointer to the result (file, aggregate, commit). If you
  abandon a lane, set it back to OPEN with a note saying where you
  stopped.
- **The owner's calls stay the owner's.** The five rulings, the
  roster, sheet diffs, library promotions — propose, never decide.
  A blocked lane gets one line in your report and gates nothing
  else; keep other work moving.
- **Read order for newcomers:** this file → `README.md` →
  `docs/QUESTIONS-FIRST.md` → `docs/SCRIPT-FIRST.md` →
  `docs/DESIGN-COMPARISON.md` → the doc for your lane
  (`docs/MAKER-LANE.md`, `docs/FRONTIER-AND-TASTE.md`,
  `docs/ITERATOR.md`, `docs/QUESTION-GRAPH.md`) → the relevant
  `skills/*/SKILL.md`.
