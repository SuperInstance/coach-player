# Lane submission — MiniMax (independent V1 design)

Produced 2026-10-14 in a standalone MiniMax web-agent session
(agent.minimax.io, Max plan, model shown: M3.1-Flash-Preview),
working only from this repo's public contents and the Shoalwater
demo source, under the same three-pass brief as the Claude lane
(design → adversarial self-critique → revised final). Saved
verbatim below the line; the comparison synthesis lives in
docs/DESIGN-COMPARISON.md once both lanes are in.

---

V1 DESIGN

Coach Player — runtime design. Self-contained: a builder needs only this document. Revision 2, 2026-10-14. Supersedes the first pass; changes are marked [R] where they fix a defect found by adversarial review of revision 1.

0. Ground truth

Everything here is grounded in two places: the repo SuperInstance/coach-player (read at main, 2026-10-14) and the host game SuperInstance/shoalwater @ 64ffb49, docs/explore.html (50,731 B, md5 7deeb4965d04c8ef57412f49b520d3e1). A builder who has read neither can build from this document.

0.1 What the repo gives us
docs/SCRIPT-FIRST.md — the four-layer runtime: motor (verified scripts as "tiles"), overseer (cheap Jev judges returning percentages), author (LLM in rare budgeted pulses), coach (human). Tiles carry projection provenance and Jev confidences. The A-plan is "a route you hope gets interrupted," and replanning routes through high-value states, never direct.
docs/QUESTIONS-FIRST.md — five tests a question must pass to earn a place in the database: spectrum, discriminates, not a coin flip, moves behaviour, can gather evidence.
docs/QUESTION-GRAPH.md — questions form a graph: clusters (premise, energy, failure), tensions (strategic silence vs. near-constant energy), dependencies. Mining finds new questions on edges.
docs/FRONTIER-AND-TASTE.md — profile the field, profile Our Guy, iterate on gaps against the frontier not the mean, hit a professional gate, then a human tastemaker applies recorded deviations with reasons. An average is slop; a clone is unethical.
docs/STUDY-MINECRAFT-AGENTS.md — the lineage. Mineflayer/Baritone: a scripted motor makes whole classes of problem disappear. Voyager: verified skills accumulate into a library, verification grounded in game state, not the model grading its own homework. Mindcraft: parameterized commands won because they were the size of an intention. The bot-army pattern: scripts carry the hours, models carry the exceptions.
avatar/SHEET.md — dials (chattiness 6, boldness 5, caution 5, humour 6, showmanship 6), five commentary moves (narrate-plan, quiet-before-hard, own-the-miss, callback, mini-goal), and four non-negotiable guardrails: no impersonation, no claiming a memory it lacks, no talking over a coach order, family-friendly.
questions/questions.jsonl — 271 questions, all status: hypothesis, 157 with a winner_lean (median 62), spread narrow/medium/wide. 179 nudgeable: true, 92 false.
questions/inbox/overseer-tiles.jsonl — 10 questions (over-001..over-010) that are exactly the design questions below, all winner_lean: null, all status: hypothesis. Section 9 answers all ten.

0.2 The host game

A bathymetric boat simulator over Sitka Sound. Real bathymetry, quantized-mesh terrain tiles, 65×65 Float32 grids decoded once at load, bilinear sampling. Verified: there is no RNG anywhere in explore.html (Math.random count = 0). The simulation is deterministic given inputs. This matters: it means a test harness can replay exactly, and all session divergence comes from the judge.

The motor contract — five fields, one writer:

const input = { throttle: 0, turn: 0, vert: 0, boost: false, brake: false };

Frame loop, explore.html:720:

if (demo.on) demoControl(dt); else readKeys();

Any keydown calls stopDemo(true) first (explore.html:365-368). Keyboard, touch stick and gamepad all funnel into input via readKeys(). This single line is the product. Tiles are not a special interface; they are code that writes input instead of readKeys(). Coach surface, tile runner and human keyboard are three writers competing for five fields, and possession is one boolean. Every takeover guarantee follows for free.

Boat state: state.boat = { pos: Vector3, theta, speed, aground }.

shaped  = sign(throttle) * |throttle|^1.4
target  = shaped * (shaped > 0 ? 6 : 2)      // 6 m/s ahead, 2 m/s astern
rate    = brake ? 3.2 : 1.1
b.speed += clamp(target - b.speed, -rate*dt, rate*dt)
b.theta += turn * (0.12 + 0.38*min(|speed|/3, 1)) * sign(speed || 1) * dt
bow      = pos + fwd(theta) * 3.4
b.aground = groundAt(bow) > tide - 0.45 && |b.speed| > 0.01
keelBow   = tide - groundAt(bow)             // depth of water at the bow

Turn authority scales with speed. Grounding forces speed = 0.

Drone state: { pos, theta, vel, battery, aboard, diveMin, dead }.

maxF   = boost ? 4.5 : 2.6                   // horizontal
effort = min(1, |throttle| + |vert| + (boost ? 0.5 : 0))
battery -= dt * (1/600 + effort/240)          // hover 600 s, working 120 s
battery += dt * 0.05   (while aboard)        // FLAT TO FULL IN 20 SECONDS
floor   = groundAt(pos) + 0.8

switchVehicle('drone') refuses if aboard && battery <= 0.02, and launches at max(groundAt(b.pos)+1.5, tide-6) — at the boat's position. The drone has no independent mobility; the boat carries her. Horizontal 2.6 m/s vs the boat's 5.4, so she is slower than the carrier. Any drone tile is a positioning tile with a payload.

Battery 0 → she settles, and if she touches bottom, dead = true. Recovery is automatic: bring the boat within 15 m and she is recovered aboard at battery = 0.03. diveMin < 1/3 sets reserveSpent — the game's own "thirds" discipline, surfaced in the HUD at 1/3 and 2/3.

Objectives (OBJS, explore.html:792-797):

shoalTime += dt  when  hDist(drone, BAYC) < 350
                  && (drone.pos.y - groundAt) < 2.5
                  && (tide - drone.pos.y)      > 1.5
['Cast off',      hDist(boat, SPAWN) > 60]
['Jamestown Bay', hDist(boat, BAYC) < 350]
['Work the shoal',shoalTime >= 10]
['Find the wreck',hDist(drone, WRECK) < 18 && |drone.y - (groundAt(WRECK)+1)| < 8 && !drone.aboard]
['Bring her home',hDist(boat, SPAWN) < 40 && hDist(boat, BAYC) >= 350 && shoalTime >= 10]

Constants: SPAWN (4641, −779), BAYC (8471, 445), WRECK (9015, 612). Anchorage→bay transit is 4,021 m at 5.4 m/s = 12.4 minutes. Bay centre→wreck is 569 m. Tide is a slider, min −1.5, max 4.0, step 0.1.

Derivation the whole tile layer rests on. Both shoalTime depth conditions are upper bounds on y, and the drone's floor is groundAt + 0.8:

feasible  y ∈ ( gnd + 0.8 ,  min(gnd + 2.5 , tide − 1.5) )
non-empty  iff  gnd < tide − 2.3

The shoal must carry at least 2.3 m of water at the current tide. The shipped demo hardcodes groundAt + 1.2, which works at tide 1.4 and is silently wrong at tide −1.5 — the tile runs fine and the counter never moves. Section 5.2 turns this into a precondition instead of a failure.

0.3 Two host-game defects to fix before any tile runs

[R] HOST-DEFECT-01 — bathymetry fails open. explore.html:179:

return -60;   // outside the pack: assume deep water

Out-of-bounds reads as 60 m of water, i.e. safe. Every safety signal in this design — keel clearance, tension, the corridor probability P — inherits that lie.

Fix: the adapter shadows groundAt and returns NaN for unmapped. Fail closed. NaN makes requires false (tile is not a candidate), forces tension to 1, and forbids corridors from routing through it. One-line change, three consumers.

Consequence already visible: the page picks its pack from the URL (explore.html:123, default real-pack, ?pack=demo selects demo-pack). The demo-pack's extent is X ∈ [−2737, 2913]; the boat spawns at X = 4641 and waypoints run to 9015. All seven demo waypoints resolve to −60 under ?pack=demo, and because stepBoat clamps pos.x to [extent.minX+5, extent.maxX−5], the boat is pinned at X = 2908 every frame and the entire demo is unreachable. Fix by regenerating demo-pack over the play area. Until then real-pack is canonical.

[R] HOST-DEFECT-02 — the confidence layer is discarded. The pack manifest declares extensionsSupported: ["bathymetry-bottomtype", "bathymetry-confidence"] with tiers proMultibeam / fleet / interpolated. A tile cannot tell a multibeam survey from an interpolation, so it cannot know which readings are the ones a grounding incident comes from. Fix: the adapter exposes confidenceAt(x,z); tension reads it (section 3.4).

Both defects are caught by a single setup assertion that runs before any tile executes — section 8.1. It should have existed in revision 1.

0.4 The commitment, restated honestly

Facts are cheap; judgments cost; and neither of those means facts are trustworthy.

Revision 1 said "facts are free" and built everything on it. The cost half survives verification: grids are decoded once at load, sampleBottom is a linear scan over ~14–39 tiles plus a bilinear read, so groundAt is genuinely free to call 480 times a minute. The trust half was wrong, and 0.3 is how it fails. The correct statement:

Read state for anything the state can answer. But state readings carry provenance, and a provenance-free constant is a judgment in disguise. Every threshold inside requires and costs is an authored decision, and section 1 makes authoring one a gated, measured activity rather than a constant someone typed.

1. Cost model and the calibration gate

This section is first because in revision 1 it was missing, and its absence invalidated the thresholds everything else depended on.

1.1 [R] The overseer is the expensive layer, not the author

Revision 1 priced the author (4k in / 2k out, one pulse per 12 min) and never priced the judge, while arguing the whole time that the author was the expensive one. The arithmetic does not support that:

rate | tokens/call | tokens / 12.4 min session
Overseer (API small model) | ≤ 1 per 3 s, ≤ 20/min | ~600 | up to 36,000
Author | ≤ 1 per 12 min | ~6,000 | 6,000

The layer that runs constantly is 1–6× the layer that runs once. Revision 1's framing — "the LLM has worked itself a little further out of a job" — is about frequency, not price, and should be stated that way.

The design budget is therefore decisions per minute, not tokens. Frequency is a property of the architecture and is measurable before anyone picks a model; price is a deployment detail. The architectural claim is testable as: a competent session makes under 12 decisions per minute and authors 0–2 scripts. Instrument decisions_per_min and alarm at 15. If it alarms, the tick loop is thrashing and the fix is fewer calls, not a cheaper model.

Deployment choice, made explicit because it changes the loop:

Local model (recommended for M0): 0 tokens, 200–400 ms per eval, but shares the main thread with a 60 fps WebGL render loop. Must run off the render thread or be budgeted at ≤ 1 call / 3 s.
API model: no main-thread cost, 20–40× the tokens. Acceptable at the frequency cap above.

1.2 [R] Thresholds are derived, not chosen

Revision 1 asserted 0.62 and 0.45 as "the economic crossover" with no loss function. It was a story with a number in it. Thresholds are now quantiles of the judge's measured output distribution, produced by a calibration gate that must pass before the runtime is trusted.

C0 — the calibration gate. Build a labelled situation set: 60 situations spanning tide × anchor × vehicle × battery × hazard, each hand-labelled with best_tile, acceptable[], or none_acceptable. Run the judge on all 60 and record (confidence, correct).

MISFIT   = the confidence below which the judge's "acceptable" verdict is wrong > 50% of the time
RUN_FLOOR= the confidence above which the judge's top pick is correct ≥ 80% of the time

Gate: if no confidence value achieves 80% top-1, the judge is not usable and the fix is a better judge, not a different threshold. Do not ship thresholds derived from an uncalibrated judge.

Provisional defaults until C0 runs — deliberately wider bands than revision 1, because an uncalibrated judge should be distrusted:

MISFIT 0.30   RUN_FLOOR 0.70   HOLD 0.30–0.70

Rationale for the direction: uncalibrated ⇒ run less, hold more. Revision 1's 0.45/0.62 was confidently narrow on an unmeasured scale.

Re-calibration triggers: re-run C0 when library size doubles, or every 20 sessions, whichever comes first. The library sizes that invalidate the thresholds are the sizes the system reaches fastest, so this is not a someday item.

1.3 Session logs, split

The session log at 8 Hz over 12.4 minutes is ~6,000 lines. Revision 1 promised it was "readable top to bottom by a kid," which is false at that volume. Two artifacts instead:

sessions/<id>/trace.jsonl — machine. Every beat, every decision, every confidence and reason.
sessions/<id>/story.md — the coach's document. Beat-level, one line per event (tile started, tile aborted, offer made, offer taken, keyhole opened), each with the reason text a human can read.

The kid reads story.md. The debrief reads trace.jsonl. Nobody pretends the raw log is legible.

2. The value field

[R] Revision 1's H (harvest en route) was a tautology. Harvest was defined as "sample objective predicates along the corridor," which means routing through the shoal makes H high — the definition encodes the conclusion. V1 has no anti-beeline mechanism; it has an anti-beeline intention and a term that means "the good stuff."

2.1 host/harvest.json — authored, not derived

Value density is a property of the host game, so it is authored data, exactly as a designer would author a treasure map. It ships with the adapter and is a port tax: the second host game authors its own.

{
  "version": 1,
  "authored_independently_of": "OBJS — see 2.2",
  "anchors": {
    "SPAWN": {"value": 0.0, "why": "home; nothing to harvest here"},
    "BAYC":  {"value": 0.6, "why": "transit hub, shallow, safe to hold"},
    "shoal": {"value": 2.4, "why": "best water in the sound"},
    "WRECK": {"value": 0.0, "why": "spectacle only — no harvest, but worth watching"},
    "cove":  {"value": 0.0, "why": "spectacle and hazard together"}
  },
  "corridors": [
    {"from": "BAYC", "to": "WRECK", "via": ["shoal_flank"],
     "value": 0.9, "why": "the shoal flank lies between the bay and the cove"},
    {"from": "BAYC", "to": "SPAWN", "via": ["mid_anchorage"],
     "value": 0.0, "why": "open water homeward; nothing en route"}
  ]
}

Authority order: requires (may not run) → wants (what it makes true) → harvest.json (what the planner may prefer) → costs (what it spends). harvest.json never overrides a requires and never creates an objective. It only prices the route between things the game itself already scores.

2.2 [R] The anti-tautology constraint

Authoring the value map from OBJS recreates the circularity. Rule: the value of every anchor is authored as a property of the water, and must be defensible without reference to any objective. WRECK scores 0.0 despite being a listed objective — the wreck is a destination for spectacle, and the planner may prefer to skip it. shoal scores 2.4 because the water is good, which is the same reason a human pilot would say it, and is checkable by asking a pilot.

2.3 [R] The test that makes H falsifiable

A value field is decorative if the corridors it defines are the straight lines. Assert it:

For every corridor in harvest.json, the via-waypoints must be geometrically off the straight line (> 50 m lateral), and corridor.value must be strictly greater than the value of the straight-line path between the same endpoints.

If a corridor adds nothing over the beeline, the file is decoration, the test fails at load, and the bend rule is not implemented. This turns "never beeline" from a preference into a property that can fail the build.

2.4 [R] value_rate has an owner

Revision 1's legs carried a value_rate with no recompute rule, so the planner was confidently wrong within minutes of a tide change. Now:

Owned by the beat layer, recomputed from harvest.json + live state. Zero judgment, zero tokens — it is arithmetic over authored data.
Refreshed on: a 30 s cadence, and immediately on any event that can invalidate it (tide change beyond 0.1 m, battery crossing 1/3 or 2/3, a tile abort, an offer taken or refused).
A leg whose recomputed rate falls below 0.2 × its value at plan time is flagged stale and must be re-scored before the plan is extended through it.

3. The overseer tick loop

3.1 Cadence

Layer | Rate | May do | Decision cost
Frame | 60 Hz | write input | none
Beat | 8 Hz (125 ms) | read free predicates, recompute tension, refresh value_rate | none
Decision | event-triggered, ≤ 1 per 3 s, ≤ 20/min | score fit / interruption | 1
Author | event-triggered, ≤ 1 per 12 min, ≤ 3/session | write a tile | 1 (large)

8 Hz is chosen against the game's own clocks: the demo's stall detector fires at stuck > 2 s, so a 125 ms poll yields 16 samples inside a recoverable stall. (Revision 1 said four; that was wrong arithmetic, and it was the only number supporting the cadence.) Beat cost is ~0.4 ms/eval, ~3.2 ms per minute against a 16.7 ms frame budget — measured, and the reason the layer is free rather than assumed free.

3.2 Order — each step cheaper than the next

1. Possession (free, hard veto). A human is driving ⇒ stand down, suspend the tile (do not destroy it), run nothing below. Standing down is not a failure state.
2. Rails (free, hard veto). A rail trip is an override, not a score, and costs no decision. Rails outrank the A-plan: a coach order is an interruption the system may not argue with.
3. Safety cap [R]. If tension > 0.45 ⇒ no HOLD, no second look, no decision calls except hard-abort evaluation, and the plan may not extend past the current leg. Revision 1 left HOLD unguarded in exactly the tight spots the keyhole regime exists to distrust: HOLD costs 2 s of latency, the cove creep is 1.3 m/s, so 2 s is 2.6 m against an abort line 0.9 m above grounding.
4. Keyhole (free). tension ≥ 0.70 ⇒ planner stands down, coach surface pulses, tiles are withheld, not merely deprioritised.
5. Liveness (free, only after the tile's own settle.s). Before settle.s, liveness is not judged — a troll pass needs its full pass. After it, progress toward wants is read straight off state. Progressing ⇒ return, zero decisions. Not progressing and not yet past abort ⇒ drift++; at drift ≥ 3 the tile has failed and the loop resumes at 7 with its confidence forced to 0.
6. Offer (DECISION). Only if an offer exists. Scored against the A-plan — section 6.
7. Fit scan (DECISION). Only at tile boundaries or after a step-5 failure.
8. Band (derived, free).

3.3 Bands, and [R] the livelock fix

best ≥ RUN_FLOOR (0.70)          RUN     run the best tile
MISFIT ≤ best < RUN_FLOOR        HOLD    look once more (2 s), then commit
best < MISFIT (0.30)             MISFIT  none good enough → safe default + arm author

Revision 1 livelocked here. HOLD was "re-observe 2 s later," the author gate required "no candidate ≥ 0.45," and there was no bound on re-observation — so at best = 0.50 the system held forever, spending 6 decisions/minute, never running cleanly and never escalating. Fix:

hold_count: increments on each HOLD; resets on RUN.
  hold_count == 1  → one re-look (single decision, 2 s later)
  hold_count >= 2  → FORCE: run the most-proven eligible tile, mark session exploratory
  hold_count >= 3  → FORCE ARM: the author gate opens regardless of candidate confidence

The forced arm at 3 decouples "stuck" from "library is short," which is what created the dead band. hold_count ≥ 3 is also logged as a judge-quality signal — a library that sits in HOLD that often is a bad judge or a bad library, and the debrief says so.

3.4 [R] tension — an actual formula

Revision 1 named five inputs and gave no formula, on the most safety-critical path in the system. Worse, the inputs are correlated (a shoal is shallow ⇒ keel clearance low and unmapped bottom close and time pressure), so a sum double-counts. Use max, not sum — these are alternative expressions of one or two underlying risks, not independent axes.

tension = max(
  keel    = clamp((1.50 - keelBow) / 1.05, 0, 1),        // 0 at 1.50 m, 1 at 0.45 m grounding
  ahead   = clamp((30 - clearanceAhead200m) / 25, 0, 1),
  battery = drone_out ? clamp((0.45 - battery) / 0.35, 0, 1) : 0,
  unknown = (isNaN(bottomAt(bow)) ? 1
            : confidenceTier(bow) === 'interpolated' ? 0.6 : 0),   // HOST-DEFECT-02
  time    = clamp(1 - horizonRemaining / horizonNominal, 0, 1)
)

Both keel numbers are the game's own: 0.45 m is where aground fires, 1.35 m is the demo's conservative line. Thresholds sit just outside them. unknown is what makes HOST-DEFECT-01 and -02 harm the planner rather than only the motor.

Ladder: < 0.25 horizon 60 min · < 0.45 horizon 10 min · < 0.70 horizon 5 min · ≥ 0.70 KEYHOLE. Keyhole self-closes at tension < 0.35 held 4 s, or on coach clear.

3.5 [R] Keyhole with nobody home

The A-plan is a twelve-hour trolling day. A keyhole that stands the stack down at 3am is a twelve-hour opportunity to stand still. Answer: a hold-station tile is always eligible, needs no decision, needs no confidence (it is a reflex, not a choice), and holds the boat safely on the current anchor. When a keyhole is open and no human has taken the wheel for 90 s, the session switches to hold-station and marks itself parked in story.md with the reason. When a human returns, the keyhole is live and the plan resumes from the held leg. Standing still is a legitimate outcome; botching a cove alone is not.

4. Tile format

4.1 Schema

id: shoal.work-the-shoal.v1
name: work the shoal              # the intention a person holds, in their words
premise: >                        # shown to the coach verbatim
  Put the drone over the pale patch, hold her close over the bottom for ten
  seconds, and bring her back with a third still in the bank.

requires:                         # free adapter predicates; never judged
  situation_class: [shoal_work, transit]
  vehicle: boat
  drone: {aboard_or_recoverable: true, battery_min: 0.66}
  position: {anchor: shoal, within_m: 400}
  bottom_below_tide_m: 2.3        # derived in 0.2; the tile refuses, it does not fail
  max_tension: 0.45

wants:                            # what it makes true — the game's own predicates
  shoalTime: {delta_min: 10}

costs:                            # what it spends
  battery_thirds: 1
  time_s: {nominal: 40}
  ends: holding_station_near_anchor

steps:
  - launch_drone
  - transit_to: {anchor: shoal_look, depth_rule: objective_band}   # y = gnd + 1.5
  - hold: {s: 10, guard: {battery_min: 0.34, clear_of_bottom_m: 0.8}}
  - recover_drone

settle: {s: 6, measure: shoalTime_delta}     # patience window
abort: [battery_lt: 0.30, aground: true, tension_ge: 0.70, elapsed_over: 2.5x_nominal]

provenance:
  projected_from: [codex/entries/shoal-mode-v0.jsonl#12, #19]
  projects: [reset-discipline, escalation-structure]
  answers_questions: [show-003, escalation-002, over-003]
  mined_from: "segments where the drone goes down and the hands go quiet"

verify:
  harness: replays/shoalwork.seed.json
  pack: real-pack                 # canonical; demo-pack is HOST-DEFECT-01
  tides: [-1.5, 1.4, 4.0]
  asserts: [shoalTime_delta_ge_10, battery_end_ge_0.333, not_dead, drone_aboard]
  verdict: passing
  last_run: 2026-10-14T22:41Z

stats: {runs: 0, successes: 0, last_used: null, median_s: null, explained_runs: 0}
graduation: {state: candidate, tide_regimes: [], off_author_anchor_successes: 0}

requires must be free predicates. If a precondition needed a decision, every beat would cost money and the happy path would not be free. A tile whose requires is false is not a candidate at all — this is what keeps the candidate set small enough to score honestly.

[R] Thresholds inside requires are authored judgments (2.3, 0.66, 0.45). Revision 1 hid them in the "free fact" layer. They are now visibly authored constants, versioned with the tile, and every one must be justified in provenance.mined_from or derived from a formula in the tile. A magic constant in requires is a review failure.

Provenance is a gate, not a dial (answers over-007): a projected mechanic becomes a tile candidate with status: unverified and cannot be selected until its harness passes. Narration is testimony that authorises authoring; it is never evidence for deployment.

4.2 [R] Graduation — transfer, not count

Revision 1's test (3 bindings, 0 explanations, 0 edits) was gameable: the "0 explanations" metric is set by whether the UI offers a button, and "3 bindings" is satisfied by one tile swept across three anchors. It measured how many times a tile ran, not whether it transferred.

A tile graduates when, with its code never opened or edited, the coach has re-targeted it in two different tide regimes and at least one anchor its author never used, and it completed in every case with no explanation request.

Supporting rules:

The "what's it doing?" affordance is always on — a persistent button, never context-gated — so explained_runs measures the coach's curiosity, not our UI. Every press is logged with the tile id.
A coach who opens a tile to change it has not failed it; they have found a second tile. Editing forks, it never patches.
Pruning, with a real trigger [R] — revision 1 said "untouched for N sessions" without picking N, which is how you ship Voyager's unbounded library while claiming to have a rite. A tile is retired when it has not been selected in 5 consecutive sessions, or when explained_runs > 0 on its last 3 uses. Retirement is recorded in the open with the reason, per QUESTIONS-FIRST.md.

5. The first five tiles, in build order

Build order follows when each verification harness becomes possible, not importance.

5.1 T1 — make-way (the motor primitive)

Steer to an anchor at a given speed, arriving slow.

Extracted from demoBoatTo: bearing error → turn at gain 1.6, throttle = clamp(speed/6, 0.16, 0.95), arrival at hypot < 16.

[R] Arrival must be scale-relative: dist < max(16, speed × 3). The demo's fixed 16 m is a 3-second window at 5.4 m/s and a 12-second window at the 1.3 m/s cove creep — the same code behaving differently at two speeds, which is the whole subject of over-008.

Verify: both real transits × 3 tides. Assert arrival, never aground, |speed − target| < 0.6 on arrival, elapsed within 15% of distance / target. Low tide is not a formality: aground compares groundAt(bow) to tide − 0.45, so every route at tide −1.5 is a different route.

5.2 T2 — work-the-shoal (the objective tile)

Put the drone over the pale patch, hold her close over the bottom for ten seconds, bring her back with the reserve third intact.

This tile teaches the system because it is a boat tile with a drone payload — she launches at the boat's position and her 2.6 m/s is slower than the boat's 5.4. "Send the drone to look" is a lie the game does not permit, and the tile schema should say so out loud.

The standoff height is y = gnd + 1.5, derived from section 0.2, and the tile declares bottom_below_tide_m: 2.3. At tide −1.5 it is not a candidate and the overseer never judges it. The failure moves from the motor to the planner, where it is visible.

Verify: 3 tides; assert shoalTime Δ ≥ 10, battery_end ≥ 0.333, not dead, drone.aboard. And assert the honesty case: where bottom_below_tide_m is false, the tile must decline, not run and score zero. A tile that fails quietly is worse than one that refuses loudly, because the log then claims coverage it does not have.

5.3 T3 — come-about-and-stand-by (the recharge tile)

Hold station near an anchor with the drone aboard while she charges.

The battery arithmetic is the real economy: 120 s working, 600 s hovering, 20 s flat to full. She is cheap in absolute time; the expensive thing is holding station while she fills, because the boat is a parking lot. Tiles that end with the drone out are borrowing against the keyhole, which is what costs.battery_thirds prices.

Verify: battery rises monotonically to ≥ 0.99 within 25 s; boat stays within 40 m of the anchor; no aground while station-keeping in the cove — the shallow holding position is the hazard, not the transit.

5.4 T4 — circle-the-wreck (the spectacle tile)

Orbit the wreck at a standoff, hold the look, come back.

It produces no objective. It is the tile that justifies the personality layer and the first place a dial move should change behaviour rather than commentary.

[R] Revision 1's assertion here was a violation of the repo's own doctrine. "Mean bearing change > 120°" is a proxy any figure-eight satisfies, and inventing a number because a number feels more rigorous than a judgment is precisely what QUESTIONS-FIRST.md forbids. Split honestly:

Kinematic guard (cheap, catches only the degenerate): complete ≥ 3 of 4 orbit points at hDist < 5 and hold standoff within 0.5 m. This rules out fly-then-hover. It does not measure spectacle and is not claimed to.
Spectacle judgment (human, logged, N=3): one question — "name the moment you would have looked away." A tile passes if ≥ 2 of 3 name a moment during the orbit. Answers go in stats.spectacle_answers and become the evidence_needed segment the repo requires.

This is the one place V1 refuses a number, and the refusal is the design: a question that cannot gather evidence does not belong in the database, and neither should it be asserted in a harness.

5.5 T5 — feel-into-the-cove (the keyhole tile; built last)

Ease into the cove at walking pace with the keel as the only instrument, and back off when it goes.

The demo's own numbers: creep at 1.3 m/s toward (8957, 596), abort at keelBow < 1.35, grounding at keelBow < 0.45. 1.35 is a conservative line 0.9 m above death.

Built last because it is the only tile whose failure the stack cannot recover from cleanly. Grounding zeroes speed and triggers the demo's stuck > 2 s → unstick reflex — a recovery, not a plan. Per over-004 (the trust boundary, nudgeable: false) the keyhole withholds the tile rather than deprioritising it: offering a planner a 0.5-confidence tile to "try" in a keyhole is how a system with that rail ends up ignoring it. After the coach clears the cove once, it is a tile like any other.

Verify: tide 1.4 runs — arrival or clean abort, keelBow ≥ 0.45 at every sample, never aground. Tides −1.5 and 4.0 — the abort path must be taken and clean: throttle 0, backed off, keelBow rising. A tile that only ever exercises its success path is not verified, and at two of three tides this tile's correct behaviour is to refuse, which the harness scores as a pass.

5.6 [R] The pack axis, and the setup assertion

The three-tide rule is 3 points on the axis I had already found load-bearing — I chose the test cases after finding the bug, which makes it a regression test, not a suite. So: add the pack axis, and assert before anything runs.

Setup assertion, before any tile executes:

1. For every anchor the library references, groundAt resolves to a non-NaN reading.
2. For every anchor, a direct line from SPAWN exists inside mapped terrain.
3. Tide sweeps the full slider range without any anchor leaving the pack.

Assertion 1 alone catches HOST-DEFECT-01 at setup, in one line, before any tile failure is misattributed to the tile. Tiles run against real-pack (canonical) and against demo-pack once HOST-DEFECT-01 is fixed.

6. The A-plan

6.1 Representation

A plan is a splicable route, not a goal — that is the anti-beeline mechanism, and after §2 it is a mechanism with a value field and a test behind it.

{
  "id": "plan-1",
  "horizon_min": 60,
  "legs": [
    { "tile": "make-way",         "args": {"anchor":"BAYC","speed":5.4}, "value_rate": 0.6 },
    { "tile": "work-the-shoal",   "args": {"anchor":"shoal"},           "value_rate": 2.4 },
    { "tile": "circle-the-wreck", "args": {"anchor":"WRECK"},           "value_rate": 0.0 },
    { "tile": "come-about-and-stand-by", "args": {"anchor":"BAYC"},     "value_rate": 0.0 },
    { "tile": "make-way",         "args": {"anchor":"SPAWN","speed":5.4}, "value_rate": 0.0 }
  ]
}

value_rate is owned and recomputed per §2.4. A 0.0 leg is free to abandon, which makes "leave the wreck, go home" cheap and "leave the shoal mid-count" expensive — correctly, without anyone writing that rule.

The plan is a tile chain run by the ordinary tile runner. No separate planner runtime. The default path and the interrupted path are the same code with a different chain loaded, which is also what makes the coach surface honest: the plan is the next few tiles, by name.

6.2 Scoring an offer against the plan

meaning | source
U value of the target | what it is worth | harvest.json + wants (free)
P probability of arriving | corridor bottom clearance, NaN blocks, tide, battery | free — groundAt sampled per 200 m band
C cost of abandoning | value_rate of the dropped leg plus deferred legs | free — the plan
H harvest en route | corridor value from harvest.json | free — authored, tested per §2.3

Bend when (U·P − C) / minutes_to_arrive + H > value_rate(current leg)

H is a term in the arithmetic, so a beeline that samples no corridor scores H = 0 and loses. And because §2.3's test runs at load, "scores zero" cannot happen by accident: a value file whose corridors are the straight lines fails the build.

Routing through, not to. A successful bend does not produce goto(target). It produces a corridor from harvest.json — via-waypoints spliced in at the head, with dropped plan legs re-inserted after the corridor rather than discarded. The one number that tests the whole mechanism: plan_completion_after_interruption == 1.0 — a session that takes an offer still completes its A-plan objectives.

6.3 Situation classes are free

[R] Revision 1's recurrence gate ("this situation class has occurred ≥ 3 times") had no classifier, and the obvious implementation — having the judge cluster situations — spends a decision to decide whether to spend on authoring. Classes are now adapter-emitted tags from a small enum over state, a fixed list the host game defines:

shallow_transit · shoal_work · spectacle_approach · tight_cove
drone_recovery · battery_return · hold_station · parked

Emitted by the adapter at zero cost, because the adapter is host-game code reading its own state. Recurrence is a counter keyed by the tag. Note the consequence, which is now a decision rather than an accident: a situation that only ever occurs in keyholes is permanently unauthorable. That is deliberate — the first time through the cove is a coaching problem, not an authoring problem.

7. Escalation

7.1 Authorisation — five conjunctive gates

Each alone is a bug:

1. Misfit — best < MISFIT (0.30 provisional).
2. Recurrence — the situation-class counter ≥ 3 this session.
3. No keyhole — tension < 0.70.
4. Budget — ≤ 1 per 12 min, ≤ 3 per session, session token spend < 5% of cap.
5. Library short — no candidate ≥ MISFIT.

Plus the forced arm from §3.3: hold_count ≥ 3 opens gate 5 regardless.

The 12 minutes is not arbitrary — the anchorage→bay transit is 4,021 m at 5.4 m/s = 12.4 minutes, so the default V0 session is one crossing and the rule is one pulse per crossing. A competent session authors zero scripts, which is the intended outcome.

7.2 What rides in

The budget goes on the decision's reasons, not on more state — state is reconstructable, and "why the library failed" is not.

payload | ~tok | why
Reasons for the top 3 rejected tiles | 400 | the brief — the best tokens available
Situation digest + 3 s event window | 300 | what happened, in state terms
Projected question subgraph, shaded with the avatar's answers | 1200 | over-009's beam
Avatar sheet: dials + traits on this class | 250 | SHEET.md; what it should feel like
A-plan context and what the replan gave up | 200 | so the script fits the session
2–3 verified tiles, in full | 900 | shape by example; a schema is a contract, an example is a demonstration
Rails restated + mechanics to embody | 180 | hard constraints, not vibes

[R] over-009's beam is ~20–30 questions, not 271 — a graph walk from the situation's cluster (energy, escalation, risk, failure, commentary-timing, plus their tensions), shaded with the avatar's current answer values. This is the payoff of QUESTION-GRAPH.md: clusters give the prior, tensions are where character lives, and a narrow beam tuned to this situation gets the accidents without paying for all 271. What ships back in the log is which projected questions the resulting script actually used — over-009's own evidence_needed, collected for free.

Cap: 4k in / 2k out, enforced before the call. A non-conforming return is discarded at the API boundary, having cost one pulse. No retry loop.

7.3 Verification and rejection

A proposal never touches the library. It runs 3 tides × 1 pack + 1 replay of the triggering situation.

result | action
4/4 | joins as v1 verified, stats.runs = 0 — tested ≠ used
3/4 | rejected, reason logged, script kept in a graveyard with the failure state named
≤ 2/4 | rejected; the situation class is marked not authorable this session

Three things keep this honest:

Assertions are state predicates. Voyager's lesson: verification grounded in game state, not the model grading its own homework. shoalTime Δ ≥ 10 is a number. "The script looks right" is not an assertion.
The failure state is part of the test — including, for T2 and T5, that declining is a pass.
[R] Rejection feeds back. The graveyard entry and the failure state go into the question's history, per QUESTIONS-FIRST.md's standing requirement that pruning happens in the open with a recorded reason.

A verified tile enters probation on first real use: abort in live play before earning three bindings ⇒ demote to candidates/ and add that abort state to its harness. Passing a simulation is admission; surviving play is graduation.

8. M0 — the milestone

8.1 Scope

No author layer. The author is the most expensive and least load-bearing component; proving it on top of a runtime that cannot yet decide just pays the LLM to do the overseer's job. M0 exists to prove the economics of deciding so the author can stay off.

1. Extract demoBoatTo / demoDroneTo into a tiles/ module whose only sink is input. The frame loop's single-writer election is preserved verbatim.
2. Two tiles: make-way, work-the-shoal, with 3-tide × real-pack harnesses.
3. Setup assertion (§5.6) runs first and must pass.
4. Overseer: 8 Hz beat layer, three bands with the hold_count forced exits, decisions at tile boundaries only.
5. A-plan: make-way → work-the-shoal → make-way home, with one scripted offer at a fixed, human-visible moment.
6. Two logs: trace.jsonl and story.md (§1.3).
7. [R] Shadow author — when the gates would author, record the opportunity (class, top-3 reasons, budget state, hold_count) and make no call. This produces the escalation-rate distribution for zero tokens, and it is the one number revision 1's M0 could not produce at all.

Out of M0: the author, the question-graph projection, the workshop, the personality layer, proposed sheet diffs. The avatar is text on the caption pill.

8.2 [R] Four controls, not one

Revision 1's negative control was misconceived: a judge stubbed to 0.9 never enters MISFIT, so it could only ever demonstrate stumbles — the failure already designed for. It could not test the thresholds, which is what needed testing.

control | judge | must show
A — real | calibrated (or provisional) | sessions that complete objectives; low stumble rate
B — over-confident | always 0.9 | visible, nameable stumbles: grounding, wrong heading, hover-at-the-wreck
C — over-cautious | always 0.3 | correct MISFIT handling, gates refuse to author, hold-station engages
D — dead band | always 0.5 | the forced exits fire — hold_count 2 commits, 3 arms, and the session never stalls

D is the control revision 1 was missing. If a constant 0.5 judge does not terminate cleanly, the band logic is broken regardless of how good the real judge is.

8.3 How a human verifies it

Four tests, no code reading.

Takeover. Press any key mid-tile. Next frame: the human has control with the same bindings, the tile is suspended not destroyed, and it resumes from the same step. Fails if takeover needs a different key, drops the tile, or hitches.
Legibility. The coach can name which tile is running and why, and can see every dial nudge move the numbers that chose it. [R] The screen shows the reason first and the number second — work the shoal — 74% because the tide clears the shoal by 3 m — not three bare bars. Revision 1's "the confidence bars are the coach surface" showed the output of the overseer and hid its reasoning, which is the opposite of the README's "explain the actual mechanism, because understanding the mechanism IS the fun." The reasons string was already in the schema and was never put on screen.
The interruption test. Crush the bend threshold low (it beelines — visibly wrong), crush it high (it ignores a free win — equally wrong), set it right (it bends through the shoal, banks its 10 s, takes the offer, and completes the plan). Only the third passes. The number is plan_completion_after_interruption == 1.0.
The anti-tautology check. Run §2.3's load assertion. If the corridors are the straight lines, "never beeline" is decoration and the bend rule is not implemented.

Then the audit: every confidence in trace.jsonl traces to a state predicate at that timestamp; three runs from one seed are identical except for judge non-determinism; decisions_per_min stays under 12; and the shadow-author log says how many opportunities a competent session actually had.

9. The repo's ten open questions, answered

id | answer
over-001 run floor | Derived from C0, provisional 0.70. Bands widen under uncertainty. nudgeable: false — ours, not the kid's.
over-002 bend threshold | (U·P−C)/min + H > value_rate, value in units per minute.
over-003 harvest en route | H is a term in the arithmetic, and the corridors are proven non-collinear at load.
over-004 keyhole | tension ≥ 0.70 withholds tiles; closes at < 0.35 for 4 s; first-time-only per passage; hold-station if nobody's home.
over-005 tile size | Five tiles, each one human-sized intention, each a tight chain — never an input, never a campaign.
over-006 graduation | Transfer: 2 tide regimes and one off-author anchor, code never opened or edited.
over-007 projection belief | Testimony authorises authoring; only harness-passing tiles are selectable.
over-008 patience | Per-tile settle.s; arrival scale-relative to speed. Structural answer to a spectrum question.
over-009 beam width | The situation's cluster — ~20–30 shaded questions — plus the decision's reasons.
over-010 explore/prove | The tie-break inside HOLD, zero extra decisions, the cheapest place for taste to differ.

10. Open rulings before building past M0

1. C0 first. No threshold ships before calibration. If the judge cannot hit 80% top-1, the judge gets fixed, not the threshold.
2. The keyhole withholds rather than deprioritises — stricter than over-004's wording, and the only reading where the rail is not decorative. It has a product cost I cannot design away: a keyhole the avatar merely survives teaches the kid nothing but that the bot stops. Cheap fix with narrate-plan, already in SHEET.md: the avatar asks — "you take her in, I'll call the depth."
3. harvest.json is hand-authored and is a port tax. Someone must own it, and the anti-tautology rule (§2.2) has to be respected or the whole replan mechanism is circular.
4. T4's spectacle test is a human rubric, not a number. Three viewers, one question, answers logged. If that is too expensive to run routinely, say so now — it is the one place V1 declines to be quantitative, and the repo's doctrine demands the evidence be gatherable.
5. T1–T5 order puts the spectacle tile fourth. If the first thing anyone sees should be the wreck orbit rather than a 12-minute transit, reorder — but then the milestone buys a demo, not an architecture.

Deliberately not designed, because they need evidence M0 exists to produce: the question-graph cluster walk over the real 271 questions, and any threshold for personality dials affecting tile selection rather than commentary.

Appendix A — what survived the critique

Two ideas were load-bearing and are unchanged:

The single input writer election is the product. Three writers, five fields, one boolean. Every takeover, suspension and resume guarantee follows from it, and nothing above it needs to know how the game reads input.
The plan is a tile chain run by the tile runner. Collapsing the default path and the interrupted path into one code path is what makes the coach surface honest and what keeps a planner from becoming a second runtime.

Everything above those two was built faster than it was checked in revision 1. The corrections that mattered most, in order: price the layer that runs constantly; derive thresholds from a measured judge instead of asserting them; give H a real value field and a test that can fail; make bathymetry fail closed; force an exit out of the HOLD band; and refuse the one number that wanted to be an assertion.

Appendix B — host-game defect record

id | defect | impact | status
HOST-DEFECT-01 | sampleBottom returns −60 outside the pack; ?pack=demo places all 7 waypoints outside the pack and the clamp pins the boat at X=2908 | every safety signal reads "safe" in unmapped water; demo mode is unusable | adapter shadow (NaN) + pack regeneration; M0 uses real-pack
HOST-DEFECT-02 | bathymetry-confidence tiers discarded | cannot distinguish survey from interpolation | adapter exposes confidenceAt(); feeds tension.unknown

---

Pass 2 — the five strongest critiques (as returned):
1. Thresholds were slices of an uncalibrated scale; fix = calibration gate C0, thresholds as measured quantiles.
2. The overseer was never priced; at session scale the constant layer costs 1–2 orders more than the "expensive" author.
3. sampleBottom fails open (-60 = safe) on the most safety-critical quantity; demo-pack waypoints fall outside the pack and the clamp pins the boat.
4. HOLD-band livelock: no exit from re-observation; fix = hold_count forced exits.
5. Harvest-en-route (H) was a tautology; fix = authored harvest.json + load-time falsifiability test.

Session note: root agent.minimax.io and chat.minimax.io rendered blank; the working route was agent.minimax.io/mavis, signed in as Casey Digennaro (Max plan), model M3.1-Flash-Preview.
