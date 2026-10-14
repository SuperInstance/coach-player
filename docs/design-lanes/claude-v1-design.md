# Lane submission — Claude (independent V1 design)

Produced 2026-10-14 in a standalone claude.ai session (Casey's
Pro plan, model shown: Opus 5.5 Medium), working only from this
repo's public contents and the Shoalwater demo source, under the
same three-pass brief as the MiniMax lane (design → adversarial
self-critique → revised final). Saved verbatim below the line;
the comparison synthesis lives in docs/DESIGN-COMPARISON.md.

---

# V1 DESIGN — Coach Player runtime on Shoalwater

Status: build spec, revision 3 (after self-critique) · 2026-10-14
Repos: `SuperInstance/coach-player` (doctrine, questions, avatar), `SuperInstance/shoalwater` (the host game, `docs/explore.html`)

---

## 0. Summary

Coach Player is an autoplaying game avatar that a human *coaches*. The audience is clever middle-schoolers learning to steer an agent. V1 runs the four-layer stack on Shoalwater, a boat-and-drone game whose autopilot already drives the same input object as a human:

1. **Motor:** verified scripts exposed as **tiles**. One tile is one human-sized intention, such as "work the shoal".
2. **Overseer:** cheap **judges** returning percentages. They pick tiles, detect misfit, and score interruptions against the session's **A-plan**.
3. **Author:** an LLM called rarely, in budgeted **pulses**, to write a new tile. The tile joins the library only after verification in simulation.
4. **Coach:** the human. Sets intent, nudges dials, presses tiles, and takes the wheel in tight spots.

V1 also adds a small, separate LLM use: the **order interpreter**, which turns a kid's free-text order into a closed-vocabulary intention or dial change. This revision makes six structural decisions:

- **Fixed-step physics live and in simulation.** The same code runs in the browser and in Node, so verification is honest and replays are exact.
- **Fit is owned by the overseer, not by tiles.** P(fit) is an empirical success rate over similar labelled situations. Labels come from verification runs, sim counterfactuals and live outcomes. Tiles do not grade themselves.
- **Percentages are hidden from kids until a judge passes a calibration check.** Until then the coach sees words.
- **Tiles are chips the coach can press.** The light-switch test is measured on coach presses, not on overseer choices.
- **Authored code runs in a preemptible isolate** (QuickJS-wasm), never directly in the page.
- **Two-tier library:** a shared core ruled by Casey, and a per-avatar library ruled by its kid owner.

---

## 1. The host game: facts this design depends on

All from `shoalwater/docs/explore.html` at commit `3e07d93`.

**Coordinates.** Game frame metres, `(x, z)` as used in the code. Named points:

| Name | x | z | Source |
|---|---|---|---|
| `anchorage` (spawn, home) | 4641 | −779 | `SPAWN` |
| `cast-off` | 5600 | 150 | demo step 0 |
| `bay-mouth` | 7600 | 380 | demo step 1 |
| `shoal-edge` | 8300 | 445 | demo step 2 |
| `shoal` (work point) | 8380 | 430 | demo step 3 |
| `bay` (centre) | 8471 | 445 | `BAYC` |
| `cove-mouth` | 8957 | 596 | demo step 5 |
| `wreck` | 9015 | 612 | `WRECK` |
| `pot` | 8540 | 430 | `POT` (never exposed exactly; see §3) |

**Controls.** `input = {throttle: −1..1, turn: −1..1, vert: −1..1, boost: bool, brake: bool}` plus `switchVehicle('boat' | 'drone')`.

**Boat.** Throttle is shaped `sign(t)·|t|^1.4`. Top speed is 6 m/s ahead, 2 m/s astern. Acceleration is 1.1 m/s², or 3.2 m/s² when braking. Turn rate scales with speed. Grounding is checked at the bow, 3.4 m ahead.

**Drone.** Launched from the boat; recovered when the boat is within 15 m. Battery drains with effort and recharges aboard at 0.05/s. If it dies away from the boat it rests on the bottom until the boat comes within 15 m.

**Rules a tile must respect.**

- A bow grounding at more than 2.2 m/s is a hull hit. Two hits set `takingWater`, which caps speed at 1.2 m/s. Grounding below 2.2 m/s only stops the boat.
- The battery runs on thirds: a third out, a third back, a third in reserve. Recovering with less than a third left sets `reserveSpent`.

**Scene objectives** (the game's own flags; the ground truth for success):

| Objective | Flag |
|---|---|
| Cast off | boat more than 60 m from anchorage |
| Make Jamestown Bay | boat within 350 m of `bay` |
| Work the shoal | `shoalTime ≥ 10` (drone within 350 m of `bay`, under 2.5 m above bottom, more than 1.5 m below the surface) |
| Find the pot | `potFound` (drone within 10 m of the pot, under 3 m above bottom, held 3 s) |
| Bring her home | boat within 40 m of anchorage with `potFound` |
| ★ Log the wreck | `wreckSeen` (drone out, within 18 m of wreck horizontally, within 8 m vertically of 1 m above bottom) |

**What a player can see.** Use this as the observation boundary:

- The minichart (12 m per pixel) plots the anchorage, the pot and the wreck.
- The HUD shows the pinger range in metres when within 150 m.
- The nav line shows bearing and distance (to 0.1 km) to the next objective.

So the pot's position is visible to about 12 m. The existing autopilot reads it exactly, which is a small cheat, not a large one.

**Practice starts:** `?start=jamestown` (8200, 445), `?start=pot` (8410, 430), `?start=cove` (8900, 612). All heading −90°.

**Known code issues this design must fix** (§2): any `keydown` triggers takeover, including typing in a text box. `switchVehicle` from non-demo code triggers takeover. `sampleBottom` scans terrain tiles linearly. Physics functions also move meshes. The loop uses variable `dt`.

---

## 2. Required changes to Shoalwater

These are the first commits (milestone M0). Nothing else works without them.

1. **Extract `core.js`.** Make it an ES module, importable by the page and by Node, holding:
    - state, terrain loading and sampling, `stepBoat`, `stepDrone`;
    - vehicle switching rules and objective flags;
    - `snapshot()` and `load(snapshot)`.

    No three.js scene objects inside it; `THREE.Vector3` and `MathUtils` are fine. Mesh, camera and HUD updates move into a `syncRender()` in the page.
2. **Fixed-step physics, live too.** The page accumulates frame time (capped at 0.25 s) and runs `core.step(1/60)` as many times as fit. The controller (keys, or the runtime) is sampled once per step. Rendering stays once per frame. Cosmetic bobbing may keep using wall time. Result: the browser and Node run identical physics, and a session is reproducible from its seed, initial snapshot and coach inputs.
3. **Takeover scope.**
    - The game's `keydown` handler returns early when `e.target` is inside an `input` or `textarea`.
    - Takeover fires only on control keys: W A S D, arrows, R, F, V, Space, Shift. Touch stick, vertical buttons, vehicle buttons and the demo pill also take over.
    - `switchVehicle(v, source)` takes `source ∈ {'player', 'runtime'}`; only `'player'` triggers takeover.
4. **Terrain index.** `sampleBottom` looks up its tile by grid index (O(1)), not by scanning `tileGrids`.
5. **Sim entry point.** `tools/sim.mjs` loads the terrain pack from disk, applies a practice start or a snapshot, and steps headless. Same seed, same inputs → byte-identical `snapshot()`.
6. **Coach mode.** `?coach=1` loads the runtime instead of the demo autopilot. In coach mode there is no 90 s idle auto-demo, and saving is disabled for runs the avatar drives.

---

## 3. Observation and action contract

The runtime never sees `core` state directly. The adapter builds a frozen `obs` once per physics step, containing only what a player could see:

```js
obs = {
  t, step,                              // game seconds, step index
  vehicle: 'boat' | 'drone',
  tide,                                 // m
  boat:  { x, z, heading, speed, aground,
           keelBow,                     // m: tide − bottom, 3.4 m ahead
           keelAhead10,                 // m: same, 10 m ahead
           hullHits, takingWater },
  drone: { aboard, x, y, z, heading, depth, altitude, battery, dead, distToBoat },
  pinger: null | { range },             // integer m, when range < 150; measured from the drone if out, else from the boat
  chart: { anchorage:{x,z}, wreck:{x,z}, pot:{x,z} },   // rounded to 12 m grid
  objectives: { castOff, bay, shoal, shoalTime, pot, home, wreck },
  flags: { reserveSpent },
  places: { /* the named points of §1, minus pot */ }
}
```

**Action.** Each step, the active tile returns `{ input: {...}, vehicle: null | 'boat' | 'drone' }`. The runner:

- copies only the fields the tile's manifest declares in `writes`;
- clamps them to range;
- calls `switchVehicle(v, 'runtime')` if `vehicle` is set.

An undeclared field in the return value is a rail violation. Tiles never touch game state.

**Safe hold.** The adapter declares a null action with a safety note. Shoalwater's `hold` is throttle 0 and brake on. It is safe because the game has no wind, current or enemies. A second game must declare its own `hold` and say whether it is safe; if it is not, the keyhole rule in §6.5 changes for that game.

---

## 4. Intentions

An **intention** is what the coach or the plan wants, independent of how. Tiles *claim* intentions. Misfit means no claimant can do the job, which is a fact the overseer can check, not a feeling.

`runtime/intentions.json`, one entry per intention:

| Field | Example |
|---|---|
| `id` | `film-wreck` |
| `say` | "log the wreck in the cove" (shown to the coach) |
| `phrases` | ["show me the wreck", "film the wreck", "go see the wreck"] |
| `params` | none, or a named enum such as `place` |
| `done` | predicate over `obs`: `objectives.wreck` |
| `value` | points (§7.2) |
| `features` | the situation features fit is judged on: `[distToTarget, vehicle, battery, keelBow, tide, headingError]` |

**V1 intentions:**

| Intention | Done when | Tile in V1 |
|---|---|---|
| `reach(place)` | boat within 16 m of `place` | `make-for` |
| `recover-drone` | `drone.aboard` | `drone-home` |
| `work-shoal` | `objectives.shoal` | `work-the-shoal` |
| `find-pot` | `objectives.pot` | `hunt-the-pinger` (M2) |
| `enter-shallows(place)` | boat stopped within 20 m of `place`, keel ≥ 1.2 m | `creep-in` (M2) |
| `film-wreck` | `objectives.wreck` | none: the author's first job |
| `hold` | always | `heave-to` (built in) |

---

## 5. Tiles

### 5.1 Module and manifest

A tile is one JS module and one JSON manifest in `library/<tier>/<id>/`.

```js
// tile module — runs inside the isolate (§5.3)
export function start(ctx) {}             // ctx: { params, style, rng, helpers, sub }
export function tick(obs, ctx) {          // called every physics step (1/60 s)
  return {
    input:   { throttle, turn },           // only declared fields
    vehicle: null,                         // or 'boat' | 'drone'
    status:  'running',                    // | 'done' | 'failed'
    progress: 0.42,                        // 0..1, monotone where possible
    beat:    null                          // or 'narrate-plan' | 'quiet-before-hard' | 'own-the-miss' | 'celebrate'
  };
}
```

Tiles have no `fit()`. The overseer owns fit (§6.2).

- `ctx.helpers`: `steerTo(obs, x, z, speed)`, `droneTo(obs, x, y, z)`, `keelAhead(obs, m)`, `returnCost(obs)` (battery needed to reach the boat), `pingerStep(obs, mem)`. All are pure functions over `obs`.
- `ctx.sub(tileId, params)`: runs one other library tile as a sub-step. Chains are limited to 2 sub-tiles (the V1 answer to `over-005`).
- `ctx.rng`: a seeded PRNG. `Math.random` is not available.
- `beat` feeds the Personality layer. Tiles never write caption text. Until that layer lands, `captions.json` maps tile + beat to lines lifted from the current demo captions.

**Manifest fields:**

| Field | Example | Rule |
|---|---|---|
| `id`, `version`, `name` | `make-for`, 3, "make for…" | name is what a person would say |
| `claims` | `["reach"]` | intentions this tile can achieve |
| `params` | `place ∈ places` | named enums only |
| `style` | `{boldness: [0,10], caution: [0,10]}` → speed cap, keel margin | verified at both ends of every range |
| `flair` | boldness ≥ 7: min keel 0.8 m at ≤ 1.2 m/s, with `quiet-before-hard` | see §5.6 |
| `vehicle`, `writes` | `boat`, `[throttle, turn, brake]` | enforced by the runner |
| `pre` | `vehicle == 'boat' && !takingWater` | hard gate, not a percentage |
| `success`, `fail` | intention's `done`; `hullHits increased` or `aground > 5 s` | predicates over `obs` |
| `expect` | duration 40–180 s; progress = 1 − dist/startDist | feeds `J.progress` and grace |
| `provenance` | `{source, from, questions, pulse, parent, author}` | `source ∈ hand, demo-port, codex-projected, authored-pulse, adopted` |
| `verify` | fixtures, seeds, results, code hash, date | written by the verifier only |
| `stats` | coach presses, overseer picks, successes, takeovers, surprise flags | written by sessions only |
| `status` | `draft → verified → probation → library → graduated`, or `retired` | §5.5 |

### 5.2 Fixtures

A fixture is a start (a practice start, a named place, or a stored snapshot), a target intention with params, and a time limit. Fixtures come from four sources:

1. hand-written per tile;
2. author-proposed;
3. **harvested from live play:** every live tile start saves a snapshot, deduplicated by situation signature, capped at 50 per tile;
4. the snapshot that triggered an authoring pulse.

The verifier jitters each start by seed: position ±20 m, heading ±30°, tide −1 to +3 m, and battery 0.4 to 1.0 where relevant.

### 5.3 Isolation

All tiles run in **QuickJS-wasm** (`quickjs-emscripten`), called synchronously from the page's physics step and from Node in sim.

- **Interrupt deadline:** 2 ms per `tick`. A tile that exceeds it twice in a row is killed, and the overseer treats it as failed.
- The isolate holds the helper library and the tile source. It has no DOM, network, timers or host objects.
- `obs` is passed as JSON each step; the return value is parsed and checked.
- One runtime for every tile keeps live and sim behaviour identical.
- **Fallback:** if QuickJS misses the M0 performance gate, run core tiles under SES `Compartment` and authored tiles in sim only.

### 5.4 Machine verification (`tools/verify.mjs`, Node)

A tile reaches `verified` only if all gates pass, in this order:

1. **Static.**
    - Parses; exports `start` and `tick`.
    - Imports nothing.
    - At most 300 lines.
    - Manifest is schema-valid; `writes` covers what the code returns.
2. **Fixtures.** Every fixture, 200 seeds, at both ends of every `style` range and with flair on and off.
    - Pass: at least 181 of 200 successes per fixture (Wilson 95% lower bound ≥ 0.85).
    - Zero rail violations across all runs (95% upper bound ≈ 1.5%). Rail violations are:
        - a hull hit;
        - `takingWater`;
        - the drone dead away from the boat, or `reserveSpent` (unless the manifest declares it);
        - an undeclared write or out-of-range value;
        - a deadline kill, an exception, or a timeout.
3. **No regression.** For each other tile claiming the same intention, rerun its fixture suite with this tile in the library and the overseer selecting. The intention's pass rate must not fall.
4. **Labels.** Every run is written to the label store (§6.2) as `(tile, intention, features, success)`. Verification is also the fit prior.

**Compute budget.** One fixture is 200 seeds × 2 dial ends × about 90 s of game time = 36,000 game-seconds. M0 must reach 1,000× real time per Node process, so that is 36 s per fixture per process. A 4-fixture tile on 8 processes verifies in under a minute.

### 5.5 Lifecycle and graduation (the light-switch test)

| Status | Reached when | Runs live? |
|---|---|---|
| `draft` | written | no |
| `verified` | §5.4 passes | no (staging) |
| `probation` | owner approves, or an authored tile verified in-session (§8) | yes, marked "new" |
| `library` | 5 live uses, ≥ 4 successes, 0 takeovers during it | yes |
| `graduated` | light-switch test below, ruled by the owner | yes, trusted in tight spots |
| `retired` | owner rules on a proposed retirement | no |

**The light-switch test.** It is measured on **coach presses** (§9.1), because the test is about the coach's mind, not the overseer's choices. All four must hold:

1. **Reliable:** ≥ 18 of the last 20 coach-pressed runs succeed.
2. **Invisible:** 0 takeovers in the last 10 coach-pressed runs, and at most 1 surprise flag ("huh?", §9.4).
3. **Transferred:** pressed in at least 2 different plans, or in situations with different signatures (the switch used for something else).
4. **Unopened:** its code was not opened in the workshop during those 10 runs.

**Teach-back.** At debrief the kid writes the tile's one-line caption in their own words. The owner sees it beside the stats when ruling. A caption that names the outcome ("gets us into the cove") rather than the mechanics ("slows down near the bottom") is the human evidence that the wiring disappeared.

**Retirement** is proposed automatically, never applied without a ruling:

- unused for 10 sessions;
- live success below 70% over 20 uses;
- superseded (another tile claims the same intention and beats it on the same fixtures).

### 5.6 Flair: where personality reaches the motor

Risk in V1 is not only a cost. The game's rules make some showy moves safe: grounding below 2.2 m/s is not a hull hit. A tile may declare a `flair` envelope, a verified band of reduced margins that boldness can unlock:

- a close pass at 0.8 m keel clearance below 1.2 m/s;
- a hold for drama before a reveal;
- an orbit before the look.

The tile emits `quiet-before-hard` before entering it. Verification covers flair on and off. This gives the `risk-004` question ("how close does the player deliberately sail to failure for entertainment") a place to act without breaking the rails.

### 5.7 The first five tiles, in build order

Plus `heave-to` (built in, claims `hold`): `hold` input, writes nothing else, no verification needed.

| # | Tile | Claims | Built from | Fixtures | Success |
|---|---|---|---|---|---|
| 1 | `make-for(place)` | `reach` | `demoBoatTo` + unstick back-off (reverse 0.5 for 1.2 s after 2 s stalled), plus look-ahead: cap speed at 1.5 m/s when `keelAhead10 < 2.0` | anchorage → cast-off, cast-off → bay-mouth, bay-mouth → shoal-edge, `?start=cove` → bay-mouth; tide −1 and +3 | within 16 m; time ≤ 1.3× straight-line at 5.4 m/s; 0 hull hits |
| 2 | `drone-home` | `recover-drone` | `demoDroneTo(boat at depth 2 m)` then `vehicle: 'boat'` inside 15 m | drone 30–150 m out, battery 0.35–1.0, over shoal and deep water | aboard; battery never 0; ≤ 60 s |
| 3 | `work-the-shoal` | `work-shoal` | demo step 3: dive to 1.2 m above bottom at `shoal`, slow circle (throttle 0.12, turn 0.1) until `shoalTime ≥ 10`, then `sub('drone-home')` | `?start=jamestown`, `?start=pot`, harvested | `objectives.shoal`; not `reserveSpent`; aboard |
| 4 | `hunt-the-pinger` | `find-pot` | new: fly to `chart.pot` (12 m precision), then pinger descent: step along the axis that shrinks `pinger.range`, then hold under 3 m altitude for 3.5 s; then `sub('drone-home')` | `?start=pot`, `?start=jamestown`, `chart.pot` jittered ±12 m | `objectives.pot`; not `reserveSpent`; the verifier asserts the module never sees exact pot coordinates |
| 5 | `creep-in(place)` | `enter-shallows` | demo step 5: 1.3 m/s toward `place`, stop when `keelBow < 1.35` or arrived or stalled 2.5 s; flair 0.8 m | `?start=cove` approaches from the bay at tide −1, 0, +3 | 0 hull hits; stopped with keel ≥ 1.2 m (≥ 0.8 m in flair) |

Tiles 1–3 are enough for M1. `film-wreck` is deliberately left without a tile so the author has a real first job.

---

## 6. Overseer

### 6.1 Judges

A judge is a pure function `(obs, ctx) → p` that also returns `why`. V1 has four:

| Judge | Returns | How |
|---|---|---|
| `J.fit(tile, intention)` | P(tile achieves intention from here) | kNN over the label store (§6.2) |
| `J.progress(tile)` | P(running tile succeeds), given its trace so far | kNN over the tile's verification traces at the same elapsed fraction, on features (progress, progress rate, elapsed/expected) |
| `J.tight` | τ, 0 to 1 | max of four terms: keel term `clamp((2.0 − keelAhead10)/1.5)` while speed > 1; battery term `clamp(1 − (battery − returnCost)/(1/3))` with the drone out; hull term 0.4 per hit, 1.0 when taking water; stall term 0.5 while aground |
| `J.option(option)` | P(an interruption option succeeds) | `J.fit` of the option's first tile |

τ is hand-built in V1 and is labelled as such everywhere. §12 says how it gets fitted.

### 6.2 Fit as an empirical rate

**Label store** (`labels.sqlite` on the workshop service, cached per session in the browser). Each label row: `tile, intention, params, features (normalized vector), success, source`.

Sources:
- every verification run;
- **counterfactual replays:** after each session, every selection snapshot is reloaded in sim, and every tile claiming that intention runs 20 seeds from it;
- live outcomes.

Counterfactuals are what make fit learnable: the overseer sees what the tiles it did *not* pick would have done. Because §2 makes sim and live the same physics, these labels are valid.

**P(fit):**

```
neighbours = up to k = 20 labels for (tile, intention) within radius r of features(obs)
P(fit) = (successes + α · p0) / (n + α),   α = 4,   p0 = tile's overall verification success rate
```

If fewer than 5 neighbours fall within r, the situation is **unfamiliar**: P is mostly the prior, and the tile is treated as "shaky" (below), however high P is.

**Calibration gate.** Bucket predictions into fifths; each judge has its own reliability table. A judge is **calibrated** when it has at least 50 live outcomes and every bucket with 10 or more cases is within 10 points of its observed rate. Until then its numbers are shown only in debug and the workshop (§9.2).

### 6.3 Cadence

The loop runs on game steps (1/60 s):

| Loop | Rate |
|---|---|
| Motor (`tile.tick`) | every step |
| Overseer beat | every 15 steps (4 Hz) |
| Event beat | the step an event happens: coach order, takeover, hand-back, hull hit, battery reserve, objective flag, pinger first contact, tile status change |
| Interruption scan | every 4th beat (1 Hz), plus every event beat |
| Plan rescore | every 40 beats (10 s), plus every event beat |
| Counterfactual replay | after the session, on the workshop service |

These rates are per-game settings. A faster game needs a faster beat.

### 6.4 The beat, in order

The first step that acts ends the beat; every step logs what it scored.

0. **Coach.**
    - Takeover → the runner stops returning input that step, and the overseer goes to **shadow mode**: it keeps scoring but does not act.
    - A pressed tile chip → that tile runs now, inserted into the plan as a leg.
    - A parsed order → a new or changed intention, applied this beat. Orders beat the plan, always.
1. **Rails.** Hard predicates. They are not nudgeable.
    - Drone out and `battery < returnCost + 1/3` → run `drone-home`.
    - One hull hit → boat speed cap 2.0 m/s for the session.
    - `takingWater` → the plan collapses to `reach(anchorage)` at ≤ 1.2 m/s.
2. **Tile health.** Skipped during the grace period, max(3 s, 25% of expected duration) (V1 answer to `over-008`). `J.progress` < 30% for 2 beats → mark failing; go to 5.
3. **Tightness.** τ sets the horizon (§7.5). At τ ≥ 0.85, if no **graduated** tile claiming the current intention has P(fit) ≥ 85%, run the keyhole hand-off (§6.5).
4. **Interruptions.** Score each option (§7.3). Bend when its rule holds on 2 consecutive scans.
5. **Selection.** Only when the leg changed, the tile finished, or it is failing. Candidates are tiles claiming the leg's intention whose `pre` holds.

| Best candidate | Action |
|---|---|
| P(fit) ≥ 70% and familiar | Run it. |
| 50–70%, or unfamiliar | Run it, marked "shaky"; counts as misfit evidence. |
| < 50%, or no candidate | **Misfit:** skip to the next runnable leg and narrate it ("No move for that yet — doing the shoal while I think"). `heave-to` only when no leg is runnable. Open an escalation check (§8). |

**Swaps.** A challenger replaces a running tile only if it beats it by 10 points for 2 beats. Among candidates within 5 points of the best, the runner picks the less-used one 1 time in 5 (V1 answer to `over-010`).

**Hand-back.** When the coach presses "Hand back", the overseer rescores every leg against the game's flags and resumes at the first unfinished one. It does not assume the old leg still applies.

**Budget.** The whole beat must take < 2 ms. kNN runs over at most a few thousand labels per (tile, intention) with a flat array scan, which is enough for V1.

### 6.5 Keyhole hand-off

When τ ≥ 0.85 and no graduated tile is trusted:

1. The caption reads "Tight bit — your wheel?" and a chime plays. The strip pulses.
2. The current tile is replaced by `heave-to`, which is safe in Shoalwater (§3).
3. The avatar narrates while holding, about every 4 s ("Holding off the rocks till you take her"). It never goes silent and never moves on its own.
4. If τ falls below 0.6 while holding (the boat drifted or the coach changed nothing), planning resumes.

---

## 7. The A-plan

### 7.1 Stored form

`sessions/<id>/plan.json`. Every bend writes a new version with `parent` set.

```json
{
  "plan_id": "s0142-p3", "parent": "s0142-p2",
  "intent": "work the shoal and get home safe",
  "author": "default | coach | bend", "clock_budget_s": 900,
  "legs": [
    {"id": "L1", "intention": "reach",     "params": {"place": "shoal-edge"}, "value": 0,  "status": "done"},
    {"id": "L2", "intention": "work-shoal", "params": {},                    "value": 30, "status": "running"},
    {"id": "L3", "intention": "reach",     "params": {"place": "anchorage"},  "value": 20, "status": "pending", "via": []}
  ],
  "value_field": {"cell_m": 25, "layers": ["objective", "information", "show"], "lambda": 0.5},
  "bends": [{"at_s": 212, "option": "film-wreck", "gain": 21.5, "needed": 18.0, "taken": true, "why": "coach order"}]
}
```

Legs name **intentions**, not tiles. The overseer picks the tile each time a leg starts.

### 7.2 Value

Prices in points: shoal 30, pot 100, home with pot 40, wreck 50. M1 only: home safe without the pot is 20. Costs: hull hit −60, `reserveSpent` −25, `takingWater` −200.

These numbers are Casey's call (§13). They live in `runtime/prices.json` and are shown in the workshop as the plan's "prices".

Expected value of the remaining plan:

```
V(A) = Σ_legs P_leg · value_leg  −  Σ_risks P_risk · cost_risk
```

where `P_leg` is the tile's verification success rate on fixtures nearest to the leg's start, not the current-situation fit. Legs that no longer fit in the remaining clock are dropped from the end, lowest value first.

### 7.3 Interruptions

An interruption is an event that produces an **option**, a proposed plan edit. V1 option generators are hand-written per event:

| Event | Option |
|---|---|
| Coach order with a new intention | insert that leg now |
| Pinger first contact during another leg | insert `find-pot` next |
| Wreck chart mark within 300 m and `film-wreck` claimable | insert `film-wreck` before the next transit |
| Hull hit | lower boat speeds; drop legs that need `enter-shallows` |
| Battery reserve | insert `recover-drone` now (also a rail) |

V1 only notices interruptions someone wrote a generator for. That limits how opportunistic the avatar can be, and the design accepts it.

**Bend rule.** For option O, build plan A′ and compute gain = V(A′) − V(A). Bend when all hold:

- gain ≥ max(10 points, margin × V(A)). Margin is 15% by default (V1 answer to `over-002`), set by the coach's **Detours** dial from 40% at 0 to 5% at 10. The absolute floor stops jitter late in a session, when V(A) is small.
- `J.option` ≥ 60%.
- Both hold on 2 consecutive scans.

A coach order skips the margin.

A declined option is shown in words: "Saw the wreck; sticking with the shoal (+8, needs +12)." That sentence is part of the lesson.

### 7.4 Routing through good water (M2)

M1 legs go straight using a keel-aware A*. M2 adds via points.

**Value field.** A 25 m grid with three layers; each cell's value is harvested once:
- **Objective:** cells where an unfinished objective progresses (the shoal area while `shoalTime < 10`).
- **Information:** the pinger ring (≤ 150 m around `chart.pot`) until first contact; the wreck's 18 m ring.
- **Show:** points of interest for commentary, weighted by the showmanship dial.

**For each `reach` leg:**

1. Compute the beeline time `t0` with A*. Edge cost = distance / allowed speed, where allowed speed is the boldness speed cap, or 1.5 m/s where keel clearance at the current tide is under 2 m.
2. Take the top 8 unharvested cells within the leg's corridor.
3. Evaluate routes with 0, 1 or 2 of them as via points: 65 candidates.
4. Choose the route maximizing harvested value − λ × extra seconds, subject to time ≤ 1.25 × `t0`. λ is the V1 answer to `over-003`, set by the coach's **Scenic route** dial.

### 7.5 Horizon by tightness

V1 answer to `over-004`; not nudgeable.

| τ | Rescore plan | Plans ahead | Tiles allowed | Author pulses |
|---|---|---|---|---|
| < 0.3 | every 10 s | whole session | probation and up | allowed |
| 0.3–0.6 | every 1 s | next 2 legs | probation and up | no |
| 0.6–0.85 | every beat | current leg | library and graduated | no |
| ≥ 0.85 | — | — | graduated with P ≥ 85%, else keyhole hand-off | no |

---

## 8. Escalation: the author

### 8.1 Where authoring happens

- **In session:** only for **new intentions** with no claimant (almost always from a coach order), and only when calm. Fast and visible, with one repair.
- **Offline, in the workshop:** everything else. Misfits in tight or shaky situations and failed in-session pulses go to `workshop/wishlist.jsonl`. They are authored after the session, or overnight, with up to 3 repair rounds each, fed verifier output each time. This is the main growth path. It gives the author the execution feedback that iterative agents like Voyager depend on.

### 8.2 What authorizes an in-session pulse (all must hold)

1. **Misfit:** the leg's intention has no claimant, or misfit (§6.4) has held for 3 beats.
2. **Calm:** τ < 0.3.
3. **New:** situation signature = intention + params + vehicle + 100 m region cell + bucketed battery, tide and keel. No pulse is in flight for it, and it has not been rejected twice in the last 10 sessions of this avatar.
4. **Not already solved elsewhere (dedupe):** no core tile or other avatar's tile claims this intention. If one does, the workshop service verifies it against the triggering snapshot in sim, with no LLM. If it passes, it is adopted into this avatar's library as `probation` (`source: adopted`) and no pulse is spent.
5. **Budget:** §8.3.
6. **Visible:** the strip says "No move for this — writing one (1 of 3)". A coach setting "Ask me first" turns this into a yes/no chip. Default is go (Casey's call, §13).

### 8.3 Budget

| Limit | Value |
|---|---|
| In-session pulses | 3 per session, ≥ 120 s apart, 1 in flight |
| All authoring calls | 10 per avatar per day (in-session + offline) |
| Repairs | 1 per in-session pulse; 3 per wishlist item offline; each counts as a call |
| Tokens per call | ≤ 30k in, ≤ 4k out |
| Health metric | authoring calls per hour of play, per avatar. It must fall as the library grows. If it is flat or rising for 3 weeks, stop and investigate. |

Over budget → wishlist.

### 8.4 The authoring packet

Saved whole as `authoring/<pulse>/packet.json`. Built by the workshop service; the LLM key never reaches the browser.

| Part | Contents | Cap |
|---|---|---|
| Situation card | the triggering `obs`, the last 20 s of events, the intention and its `done`, the plan legs, misfit evidence (each claimant's P and `why`, or "no claimant") | 2k tokens |
| Game card | §1 rules and objectives, §3 contract, the physics constants of §1 | 3k, static |
| Tile contract | §5.1 interface and manifest schema, helper signatures, `ctx.sub` and its library list, the 2 nearest tiles' code | 8k |
| Rails | §3 action rules; no state access; `ctx.rng` only; beats from a fixed list; ≤ 300 lines | 0.5k |
| Question projection (A/B arm) | §8.5 | ≤ 2k |
| Output contract | exactly one manifest JSON and one module; ≥ 3 proposed fixtures | 0.5k |

### 8.5 The question projection is an experiment, not doctrine

`questions.jsonl` holds 271 questions, mostly about commentary craft. The `over-*` runtime questions are all unshaded. Nothing yet shows that projecting questions into a code-writing call helps, so V1 tests it:

- **Arm A:** every `nudgeable: false` question, plus up to 15 questions matching the tile's `style` dials and the intention's category (for example `risk-002`, `risk-004`, `over-005`, `commentary-001`). Each is one line: id, poles, the avatar's current answer.
- **Arm B:** the rails only.
- Pulses alternate arms. After 20 pulses per arm, compare verification pass rates and keep the better arm. Record the result as evidence on `over-009`.

### 8.6 Verifying a proposed tile

The same gates as §5.4, plus two:

- **Triggering fixture first.** The snapshot that caused the pulse must pass before the others are run.
- **Fit sanity.** On the triggering snapshot, `J.fit` for the new tile (computed from its own verification labels) must be ≥ 70%.

**Outcomes:**
- **Pass.** In session → `probation`, usable at once, marked "new", owner rules at debrief. Offline → `verified`, waiting for the owner.
- **Fail.** Reason codes to `authoring/<pulse>/verify.json`, then one repair call (in session) or up to 3 (offline), else wishlist with the reasons attached.

The audit trail per pulse is the folder `authoring/<pulse>/`: `packet.json`, `response.js`, `manifest.json`, `verify.json`, and the library diff.

---

## 9. Coach surface

### 9.1 Tile chips

Under the caption pill is a row of chips for tiles whose `pre` holds right now, showing their `name`. Pressing a chip runs that tile now as an inserted leg. Coach presses are what graduation measures (§5.5). The chip row is the light switch.

### 9.2 Status strip

One line:

- **Kid view:** the running tile's name, a confidence word, the leg ("2 of 3: work the shoal"), and a tightness bar.
    - The word is "sure" (≥ 70%, familiar), "trying" (shaky), or "no move yet" (misfit).
    - Once a judge is calibrated (§6.2), its number appears too, with a small mark meaning "checked". The agent earns the right to show a number.
- **Debug view** (`?debug=1`) and **workshop:** all numbers, always: top-3 P(fit) with familiarity, τ and its terms, gain vs needed for the last option.

### 9.3 Orders

A text box. Typing never takes over (§2.3).

1. **Phrase table first:** the `phrases` of every intention plus about 20 dial phrases ("play it safe" → caution +3, "show off" → showmanship +3 and boldness +2, "hurry" → detours −3).
2. **Unmatched → order interpreter.** One small LLM call through the workshop service.
    - Input: the order text, the closed vocabulary (intention ids with `say` and params, place names, dial names and ranges), and a one-line plan summary.
    - Output: JSON `{kind: intention | dial | both | unknown, intention, params, dials: {name: delta}}`, schema-checked. Deltas are clamped to ±3. Rail settings are not in the vocabulary, so they cannot be touched.
    - Budget: 30 per session, ≥ 5 s apart, ≤ 2k tokens in, ≤ 200 out.
    - Order text passes a family-friendly filter before the call.
3. **Echo.** The confirmation is built from a template over the parsed fields, never from model prose: "I heard: **film the wreck** (new goal). No move for that yet." For dials: "I heard: **braver** → boldness 5 → 7 (this session)". `unknown` → "Didn't catch that — pick one:" plus the chips.

Order effects expire with the session, matching the avatar sheet's rule that nudges are temporary and rulings are permanent.

### 9.4 Takeover, hand-back, "huh?"

- **Takeover:** any control key, stick or button. Instant. The strip reads "Your wheel".
- **Hand back:** a button; the overseer resumes at the first unfinished leg (§6.4). In coach mode there is no automatic resume.
- **"huh?"**, meaning "that's not what I meant". Raises a surprise flag on the running tile, with an optional reason chip (wrong move, wrong place, too slow, too fast). Limited to one per tile run. Takeovers are the primary invisibility signal; flags are secondary (§5.5, §9.4).

### 9.5 Dials

From the avatar sheet: chattiness, boldness, caution, humour, showmanship. Boldness and caution feed tile `style` and `flair`; showmanship feeds the value field's show layer; chattiness and humour feed only the Personality layer.

New in V1 on the coach surface: **Detours** (`over-002`) and **Scenic route** (`over-003`). Workshop only: **Patience** (`over-008`) and **Variety** (`over-010`). Rails are never dials.

---

## 10. Libraries and ownership

| Tier | Holds | Rules on it | Notes |
|---|---|---|---|
| **Core** (shared) | hand-written and demo-ported tiles; promoted tiles | Casey | read-only to avatars |
| **Avatar** (per kid) | authored and adopted tiles, copies of core tiles the kid tuned | the kid (the avatar's owner), at debrief, like sheet diffs | cap 40 tiles; at the cap a new tile needs a proposed retirement |

**Promotion to core:** graduated in at least 3 different avatars, then Casey rules. Tiles contain no kid text, so code can be shared. Adoption copies a tile and the adopting kid rules on it, so one kid's taste never silently enters another's avatar.

---

## 11. Logging and replay

| File | Contents |
|---|---|
| `sessions/<id>/meta.json` | seed, start, versions of core, thresholds, prices, intentions, and each library tile's code hash |
| `sessions/<id>/snapshot0.json` | initial `core.snapshot()` |
| `sessions/<id>/coach.jsonl` | every coach event with step index: takeover, raw control input per step during takeover, hand-back, chip press, order text and parsed result, dial change, "huh?" |
| `sessions/<id>/beats.jsonl` | every beat: step, tile, P(fit) top 3 with familiarity, τ and terms, leg, decision and why |
| `sessions/<id>/plan.json` | all plan versions |
| `sessions/<id>/snapshots/` | snapshot at every selection (for counterfactual replay and fixture harvest) |
| `authoring/<pulse>/` | §8.6 |
| `labels.sqlite` | the label store (§6.2) |

`tools/replay.mjs sessions/<id>` re-runs the session in Node from `snapshot0`, the seed, `coach.jsonl`, and cached LLM responses. It asserts that the same beats come out.

---

## 12. Thresholds

All live in `runtime/thresholds.json`. Each entry carries its question id and `status: guess | swept | shaded`. Every value below starts as `guess`.

| Key | Value | Question | Nudgeable |
|---|---|---|---|
| `run_p`, `misfit_p` | 0.70, 0.50 | over-001 | no |
| `familiar_min_neighbours`, `knn_k`, `alpha` | 5, 20, 4 | over-001 | no |
| `swap_margin`, `swap_beats` | 0.10, 2 | over-001 | no |
| `rotate_band`, `rotate_rate` | 0.05, 1/5 | over-010 | yes (Variety) |
| `grace` | max(3 s, 0.25 × expected) | over-008 | yes (Patience) |
| `kill_p`, `kill_beats` | 0.30, 2 | over-008 | no |
| `tau_bands` | 0.3, 0.6, 0.85 | over-004 | no |
| `keyhole_fit` | 0.85, graduated only | over-004 | no |
| `bend_abs`, `bend_rel`, `option_p`, `bend_scans` | 10 pts, 0.15 (dial 0.40–0.05), 0.60, 2 | over-002 | yes (Detours) |
| `route_cell`, `route_k`, `route_vias`, `route_slack` | 25 m, 8, 2, 1.25 | over-003 | λ yes (Scenic route) |
| `chain_max` | 2 sub-tiles | over-005 | no |
| `verify_seeds`, `verify_pass` | 200, 181/200 | over-006 | no |
| `probation_uses`, `probation_success` | 5, 4 | over-006 | no |
| `grad_window`, `grad_success`, `grad_clean`, `grad_flags`, `grad_transfer` | 20, 18, 10, ≤ 1, 2 | over-006 | no |
| `codex_entry_status` | codex-projected tiles enter as `draft` only | over-007 | no |
| `packet_questions` | arm A ≤ 15 / arm B 0 | over-009 | no |
| `beat_hz` | 4 | — | per game |
| `calibration_min`, `calibration_err` | 50 outcomes, 0.10 | — | no |

**How guesses become `swept`.** `tools/sweep.mjs` replays stored session snapshots in sim across a grid of values for one threshold and scores each setting by takeovers + rail violations + authoring calls − value harvested. It runs once at least 20 sessions exist.

**How guesses become `shaded`.** The repo's own method: the question gets a `winner_lean` from evidence (session logs), with the reason recorded.

τ itself becomes `swept` once takeovers and near-strikes can serve as labels for "tight".

---

## 13. Decisions that are Casey's

1. **Prices** (§7.2): shoal 30, pot 100, home 40, wreck 50, hull hit −60, reserve −25, taking water −200, home-safe 20 (M1 only). They drive every bend.
2. **In-session pulses for kids:** automatic (default here) or "Ask me first".
3. **Models and spend:** which LLM for the author, which for the order interpreter, and the daily spend cap per avatar.
4. **Library promotion:** confirm the two-tier ownership in §10.

---

## 14. Milestones

### M0 — Shoalwater core and sim (no avatar yet)

**Build:** §2 items 1–6.

**Done when:**

- [ ] `node tools/sim-selftest.mjs` passes: the same seed and inputs give byte-identical snapshots across 2 runs and across 2 machines.
- [ ] `node tools/bench.mjs` reports ≥ 1,000× real time per process (physics + adapter + one QuickJS tile, no render). If not, profile; the fallback in §5.3 applies.
- [ ] **Human check:** play `explore.html` by hand for 2 minutes, then the pre-M0 build for 2 minutes. Steering, speed, grounding and the drone feel the same. Typing in a text field does not stop the demo.

### M1 — One plan, one misfit, one pulse (all four layers)

**Build, in order:**

1. Tiles 1–3 and `heave-to` as modules and manifests; `tools/verify.mjs`; all three verified.
2. Intention registry (§4), label store fed from verification, `J.fit`, `J.progress`, `J.tight`.
3. Runner and overseer beat (§6), a hard-coded default plan from `?start=jamestown`: `reach(shoal-edge)` → `work-shoal` → `reach(anchorage)`. Logs (§11) and `replay.mjs`.
4. Coach surface: chips, strip (kid and debug views), order box with phrase table and order interpreter, takeover, hand-back, "huh?".
5. Workshop service: packet builder, author call, verifier, wishlist, counterfactual replay after each session.
6. **Offline proof of authoring:** run the author offline on `film-wreck` (up to 5 attempts with up to 3 repairs each).

**Done when the human checks below all pass.**

Offline, before the live session:

- [ ] At least one authored `film-wreck` tile reached `verified` within 5 attempts. `authoring/<pulse>/` shows packet, response and verify report, and the packet shows which arm (§8.5) it used. This tile is then removed for the live test, so the live pulse is real.

Live, at `explore.html?start=jamestown&coach=1`:

- [ ] The avatar casts off without input. The strip shows tile name, a confidence word, "1 of 3", and the tightness bar.
- [ ] Type `wasd wasd` slowly into the order box, then clear it without pressing Enter: the boat keeps going while you type and the strip never reads "Your wheel".
- [ ] Press W mid-leg: control is yours that step and the strip reads "Your wheel". Drive about 20 m off. Press "Hand back": the avatar resumes the first unfinished leg from where you are.
- [ ] Press the `make-for` chip with a place: it runs as an inserted leg; the plan shows it.
- [ ] The scene's own list ticks "Work the shoal".
- [ ] While still in the bay, type `show me the wreck`. You see "I heard: film the wreck (new goal). No move for that yet", then "writing one (1 of 3)". The boat continues the plan meanwhile; no silent stop.
- [ ] Within about 2 minutes, either "new move ready (verified 192/200)" and the plan bends with its numbers, the boat goes to the cove, and the scene's ★ wreck objective ticks. Or "couldn't make that move — saved for the workshop", and the plan continues.
- [ ] The session ends within 40 m of the anchorage with 0 hull hits and ≤ 1 in-session pulse.
- [ ] `node tools/replay.mjs sessions/<id>` passes.
- [ ] After the session, `labels.sqlite` has counterfactual rows for every selection snapshot.
- [ ] Debrief shows proposed changes (a new tile in probation, any retirement) for the owner to rule on.

### M2 — Honest search and the first graduation

- Tile 4 (`hunt-the-pinger`): the autopilot no longer reads exact pot coordinates. Tile 5 (`creep-in`) with flair.
- Via-point routing and the value field (§7.4); the default A-plan becomes the full scene: cast off → bay → shoal → pot → home, with the wreck as an interruption.
- The first calibration gate passes for `J.fit`, so numbers appear on the kid strip.
- The first graduation ruling, from chip presses.
- The first `sweep.mjs` run on `run_p` and `bend_rel`.

---

## 15. Known limits (accepted for V1)

- **Fit needs volume.** Until labels accumulate, P(fit) is mostly the verification prior, and kids see words, not numbers. Counterfactual replays fill the store quickly, but only in situations that have been visited.
- **τ is hand-built** until there are enough takeovers and near-strikes to fit it.
- **Prices are guesses** until Casey sets them; every bend depends on them.
- **Interruptions are only the ones someone wrote a generator for** (§7.3). The avatar cannot notice an opportunity nobody anticipated.
- **The Personality layer is stubbed** to beats and a caption table. Flair (§5.6) is the only place personality shapes motion.
- **Shoalwater is forgiving:** no wind, current or enemies, so `hold` is safe and a 4 Hz beat is fast enough. Neither holds for most games.
- **Porting cost.** A second game needs, in rough order of cost:
    1. a fixed-step core runnable in Node;
    2. the `obs` contract and a safe-hold declaration;
    3. intentions, prices and fixtures;
    4. rail predicates;
    5. a game card for the author;
    6. a beat rate.

    The adapter is small; the harness is most of the work.
- **The order interpreter sends kid-typed text to an LLM.** It is filtered first, and the model's words are never shown, but the deployment still needs a privacy and consent review for minors before any public release.

---

## Appendix A — What changed from the first draft, and why

| Critique | Revision |
|---|---|
| Percentages uncalibrated; refits learn only from chosen tiles | Fit = kNN rate over verification, counterfactual-sim and live labels (§6.2); calibration gate; words for kids until calibrated (§9.2) |
| Light-switch test measured the overseer | Tile chips; graduation counts coach presses (§5.5, §9.1) |
| Free-text orders would mostly fail | Order interpreter with closed vocabulary and template echo (§9.3) |
| Misfit as a percentage hid a missing index | Intention registry; tiles claim intentions (§4) |
| Question projection unproven | A/B arms, decided by verify pass rate (§8.5) |
| `heave-to` assumed safe | Adapter declares `hold` and its safety (§3); keyhole narrates and holds (§6.5) |
| Pot-hunt "cheat" overstated | Corrected in §1; `obs` exposes chart marks at 12 m (§3) |
| Typing stole the wheel; `switchVehicle` coupling | Takeover scope and `source` param (§2.3) |
| Dead air on misfit and keyhole | Misfit skips to next runnable leg; keyhole narrates (§6.4–6.5) |
| Resume assumed the old leg | Hand-back rescores all legs (§6.4) |
| Replays not reproducible | Fixed-step live physics + coach log (§2.2, §11) |
| Fixtures didn't match live starts | Harvested fixtures from live snapshots (§5.2) |
| "huh?" noisy | Takeovers primary; ≤ 1 flag tolerated; one per run (§5.5, §9.4) |
| One-shot authoring will mostly fail; M1 could pass without it | Offline authoring with 3 repairs is the main path (§8.1); M1 requires an offline-verified authored tile (§14) |
| 18/20 bar statistically weak | 200 seeds, Wilson lower bound ≥ 0.85, 0 violations (§5.4) |
| Bend margin relative only | Absolute floor of 10 points (§7.3) |
| Verify cost linear in library | Regression only over same-intention tiles; compute budget stated and gated in M0 (§5.4, §14) |
| Author graded its own fit | Tiles have no `fit()`; overseer owns it (§5.1, §6.2) |
| AST allowlist is not a sandbox | QuickJS-wasm isolate with an interrupt deadline (§5.3) |
| Curator bottleneck; library ownership undecided | Two tiers; kid rules the avatar library; auto-proposed retirements (§5.5, §10) |
| Motor ignored personality | Flair envelopes inside the game's safe rules (§5.6) |
| LLM spend per kid | Dedupe/adoption before any pulse (§8.2); daily cap; falling-rate health metric (§8.3) |
| Thresholds arbitrary | One config file with status per value; sweep tool; shading path (§12) |

---

Session note: claude.ai, signed in as Casey (Pro plan), model shown
in the picker: Opus 5.5 Medium. All requested repo files opened.
