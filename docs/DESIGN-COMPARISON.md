# Design comparison — two independent V1 designs, one synthesis

On 2026-10-14 Casey directed an experiment: give the same brief
to two fleet models in separate browser sessions, each blind to
the other, each required to critique its own design before
finalising. Submissions: docs/design-lanes/minimax-v1-design.md
(MiniMax web agent, M3.1-Flash-Preview) and
docs/design-lanes/claude-v1-design.md (Claude on claude.ai,
Opus 5.5 Medium). This document is Muse's comparison and the
merged build spec. Rule of the exercise, in Casey's framing:
convergence from a limited spec is a best-practice signal;
divergence is judged on the merits.

## Convergence — treat as settled

Eleven load-bearing points arrived independently in both:

1. **Percentages are uncalibrated until measured.** Both designs
   refuse to act on raw judge numbers before a calibration gate,
   and both hide numbers from kids until a judge earns them.
2. **Misfit must never produce dead air.** Both narrate the gap
   and keep playing something legitimate (skip to a runnable
   leg / hold station with commentary).
3. **Verification is statistical and grounded in game state** —
   many seeds, several tides, state predicates, zero tolerance
   for rail violations; declining correctly can be a pass.
4. **The host game gets fixed first.** Both read Shoalwater's
   source, both found real defects, both put host work in
   milestone zero (details differ; see unique finds).
5. **One writer for the input object; an adapter boundary**
   between runtime and game state. Everything else follows.
6. **The plan is legs the same runner executes**; bends are
   scored with hysteresis so the avatar neither jitters nor
   ignores free wins.
7. **The author is rare, budgeted, and fed reasons** — why the
   library failed, nearby verified tiles as examples, and a
   question projection; verification gates the library.
8. **Graduation means transfer + invisibility, ruled by the
   owner; pruning is proposed with reasons, never silent.**
   Both explicitly refuse Voyager's unbounded library.
9. **The first tiles are the same five intentions in the same
   order**: transit primitive → shoal objective → drone
   recovery/hold → wreck spectacle → cove creep last, as the
   keyhole tile. The wreck is deliberately left tile-less in
   both so the author has a real first job.
10. **Thresholds live as data with provenance** — a value is a
    guess until it is swept or shaded by evidence.
11. **Tension is a max() of correlated risks, not a sum**, with
    bands that shorten the planning horizon and finally
    withhold untrusted tiles in the keyhole.

## Divergence — ruled

- **Where fit lives.** MiniMax scores candidates with a judge
  and prices it; Claude makes fit an empirical rate over a
  label store (verification + counterfactual replays + live
  outcomes) with no model call in the loop. **Ruling: Claude.**
  It dissolves MiniMax's own strongest critique (the constant
  layer's cost) and makes calibration a property of data, not
  of a model's mood. A model judge survives only as the
  fallback for Claude's "unfamiliar" state.
- **What misfit is.** Claude: structural first — an intention
  with no claimant is a checkable fact, prior to any
  percentage. MiniMax: confidence bands. **Ruling: both, in
  that order** — registry check (structural misfit), then
  bands over claimants (confidence misfit).
- **The value field.** MiniMax: a hand-authored harvest map
  with a load-time falsifiability test (a corridor that is the
  straight line fails the build). Claude: a computed grid
  (objective / information / show layers) with via-point
  routing. **Ruling: MiniMax for V1** — honest, authored,
  testable at our scale — **Claude's grid is the M2 growth
  path**, inheriting the falsifiability assertion.
- **Where authoring happens.** MiniMax centres in-session
  pulses behind five gates. Claude centres offline wishlist
  authoring with up to 3 verifier-fed repairs, dedupe/adoption
  before any call, in-session pulses only for brand-new
  intentions in calm water. **Ruling: Claude's placement,
  MiniMax's packet discipline** (reasons first, hard token
  cap, graveyard with named failure states). Voyager's lesson
  is iteration with feedback; one-shot in-session authoring is
  the demo, offline repair loops are the factory.
- **Question projection.** MiniMax assumes a 20–30 question
  beam; Claude makes it an A/B experiment decided by
  verification pass rates after 20 pulses per arm. **Ruling:
  Claude, outright.** Doctrine is evidence over assertion —
  over-009 gets answered, not assumed.
- **The foundation.** MiniMax builds on the page as-is
  (adapter shadows, NaN for unmapped). Claude extracts a
  fixed-step core runnable identically in browser and Node.
  **Ruling: Claude's extraction is M0's first job.** Claude's
  counterfactual labels — the thing that makes fit learnable —
  are fiction without sim-equals-live physics; the extraction
  is mechanical and self-tested. MiniMax's milestone contents
  (two tiles, shadow author, four controls) then stand as
  written.
- **The light switch, literally.** Claude's tile chips —
  pressable tiles on the coach surface, graduation measured
  on coach presses — is an invention neither the repo nor
  MiniMax had. **Ruling: adopt.** It makes over-006 measurable
  and hands the kid the switch itself.
- **Isolation.** Claude runs authored tiles in a QuickJS-wasm
  isolate with a kill deadline; MiniMax runs trusted code in
  the page. **Ruling: Claude.** LLM-written code in a product
  for minors does not run unboxed.
- **Tension's unknown term.** MiniMax feeds bathymetry
  confidence and NaN into tension; Claude's τ has no
  provenance term. **Ruling: MiniMax's term joins Claude's
  formula** — a judge that cannot distrust its chart is the
  fail-open defect wearing a formula.

## Unique finds worth keeping whole

MiniMax: the fail-closed bathymetry fix and the setup
assertion that catches it in one line; decisions-per-minute
as the architectural budget, alarm at 15; the dead-band
control judge (a constant 0.5 judge must terminate cleanly —
the control that tests the thresholds themselves); story.md /
trace.jsonl split (the kid reads one, the debrief reads the
other); the shadow author in M0 (escalation-rate evidence for
zero tokens); reasons-first on the coach strip, number second.

Claude: the order interpreter (closed vocabulary, schema-
checked, template echo — model prose never reaches the kid);
flair envelopes (personality reaches the motor only inside
verified safe bands); harvested fixtures from live snapshots;
two-tier library ownership (kid rules the avatar library,
promotion to core needs graduation in 3 avatars + Casey's
ruling); the teach-back (the kid captions the tile in their
own words as graduation evidence); the health metric
(authoring calls per hour of play must fall as the library
grows — if it is flat for 3 weeks, stop and investigate).

## Host-game defects on record (both lanes, from source)

- sampleBottom returns −60 outside the pack: unmapped water
  reads as safe. (MiniMax; verified by Muse against the local
  file, line 188, 2026-10-14.) Fail closed instead.
- The pack's bathymetry-confidence tiers are discarded by the
  consumer. (MiniMax.)
- ?pack=demo reportedly places all demo waypoints outside the
  pack, pinning the boat at the clamp edge. (MiniMax, read on
  commit 64ffb49; not yet re-verified on the current build.)
- Typing in any text field triggers takeover; switchVehicle
  from runtime code triggers takeover. (Claude.)
- sampleBottom scans tiles linearly; physics uses variable dt
  and is entangled with rendering. (Claude.)

## Merged build order

M0: extract the fixed-step core; fix takeover scope and
terrain indexing; sim self-test (byte-identical replays);
adapter with fail-closed bottom + confidence; setup
assertion. Then MiniMax's M0 contents: make-way +
work-the-shoal tiles with 3-tide harnesses, band logic with
hold_count exits, shadow author, four control judges, story +
trace logs.
M1: intention registry, label store + counterfactual replays,
coach surface (chips, strip, order box + interpreter), offline
authoring proof on film-wreck, then one live end-to-end
session against Claude's checklist.
M2: via-point routing on the computed value field (with the
falsifiability assertion), hunt-the-pinger without the exact-
coordinate cheat, creep-in with flair, first calibration gate
passed, first graduation ruling, first threshold sweep.

## Open rulings for Casey

1. **Prices** (Claude §7.2): the point values every bend
   spends — shoal 30, pot 100, home 40, wreck 50, hull hit
   −60, reserve −25, taking water −200. His call by design.
2. **In-session authoring for kids**: automatic, or "ask me
   first" chip? Both designs default to automatic-with-
   visibility; the choice is his.
3. **Models and daily spend cap** per avatar for author and
   order interpreter.
4. **Two-tier library ownership** as in Claude §10 — confirm.
5. **Privacy gate**: the order interpreter sends kid-typed
   text to an LLM (filtered; model prose never shown). Both
   designs accept it for V1; a consent/privacy review is
   required before any public release involving minors.
