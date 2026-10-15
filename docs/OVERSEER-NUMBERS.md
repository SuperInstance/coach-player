# Overseer numbers — every operative value in one sheet

The overseer's numbers used to live scattered across two design
documents and a synthesis. This sheet collects them. **Extracted,
not authored**: every value below is copied from its source, and
the source is named on the row. Where the two design lanes differ,
the synthesis (`docs/DESIGN-COMPARISON.md`) wins; where the
synthesis did not rule, the row says **contested** and both values
stand — do not silently pick one.

**These are living numbers.** When one changes, change it here
*and* in its source document, and say so in the commit message
(or in `CLAIMS.md` if you are mid-lane). A value in this sheet
that disagrees with its source is a bug in this sheet.

Sources, abbreviated in the tables:

- **MM** — `docs/design-lanes/minimax-v1-design.md`
- **CL** — `docs/design-lanes/claude-v1-design.md`
- **SYN** — `docs/DESIGN-COMPARISON.md` (the synthesis rulings)
- **IMPL** — the shipped M0 runtime, sister repo
  `SuperInstance/shoalwater`, `docs/coach/` (`overseer.js`,
  `judges.js`, `tiles.js`)

Status vocabulary (from CL §12): a value is a **guess** until it is
**swept** (replayed across a grid in sim) or **shaded** (given a
`winner_lean` from evidence). **Implemented** means the value is
what the shipped code actually does today, whatever its evidence
status. No number in this sheet is swept or shaded yet.

---

## 1. Decision bands

| Value | What it governs | Status | Source |
|---|---|---|---|
| RUN_FLOOR = 0.70 | Best fit ≥ 0.70 → RUN the best tile | guess; implemented | MM §1.2; CL §12 (`run_p` 0.70); IMPL `overseer.js` |
| MISFIT = 0.30 | Best fit < 0.30 → MISFIT: none of these are good enough | guess; implemented | MM §1.2; IMPL |
| MISFIT = 0.50 | CL's beat table: best < 50% (or no candidate) → misfit, skip to next runnable leg; 50–70% runs "shaky" | guess; **contested** — SYN adopted bands + MM's M0 contents but never named the misfit value; IMPL follows MM's 0.30 | CL §6.4, §12 (`misfit_p` 0.50) |
| HOLD = 0.30 – 0.70 | Between MISFIT and RUN_FLOOR → HOLD: look once more | guess; implemented | MM §1.2, §3.3; IMPL |
| Re-look delay = 2 s | HOLD re-observes once after 2 s before hold_count forces an exit | guess; implemented | MM §3.3; IMPL (`holdUntil = time + 2`) |
| Misfit pause = 5 s | After a MISFIT verdict the overseer holds station 5 s, then skips the leg | implemented | IMPL `overseer.js` |
| Tension > 0.45 ⇒ no HOLD | Safety cap: in tight water there is no second look and no decision calls except hard-abort evaluation | guess | MM §3.2 |

**Band definitions** (MM §1.2 — the thresholds are quantiles of a
measured distribution, not tastes):

- MISFIT = the confidence below which the judge's "acceptable"
  verdict is wrong **> 50%** of the time.
- RUN_FLOOR = the confidence above which the judge's top pick is
  correct **≥ 80%** of the time.
- The provisional 0.30 / 0.70 pair stands *until the calibration
  gate runs* (§2). Uncalibrated ⇒ run less, hold more.

## 2. hold_count — the dead-band cure

| Value | What it governs | Status | Source |
|---|---|---|---|
| hold_count = 1 | One re-look, 2 s later | guess; implemented | MM §3.3; IMPL |
| hold_count ≥ 2 | FORCE: run the most-proven eligible tile; session marked **exploratory** | guess; implemented | MM §3.3; IMPL |
| hold_count ≥ 3 | FORCE + ARM: the author gate opens regardless of candidate confidence; also logged as a judge-quality signal | guess; implemented (arms the *shadow* author — no call in M0) | MM §3.3, §7.1; IMPL |

hold_count increments on each HOLD and resets on RUN. This exists
because a constant-0.5 judge once livelocked the design: HOLD with
no exit, forever. Control judge D (§10) is the regression test.

## 3. Calibration gates — no number is trusted before these pass

Two gates, one per lane; SYN convergence #1 adopts the principle
(percentages are uncalibrated until measured; numbers hidden from
kids until a judge earns them) without merging the two procedures.

| Value | What it governs | Status | Source |
|---|---|---|---|
| 60 hand-labelled situations | MM's gate C0: situations spanning tide × anchor × vehicle × battery × hazard, each labelled best_tile / acceptable[] / none_acceptable | not yet run | MM §1.2 |
| 80% top-1 | C0 pass bar: if no confidence value achieves 80% top-1, the judge is not usable — fix the judge, not the threshold | not yet run | MM §1.2 |
| Re-run C0 | When library size doubles, or every 20 sessions, whichever comes first | rule | MM §1.2 |
| ≥ 50 live outcomes | CL's gate: a judge is *calibrated* at 50+ live outcomes… | not yet run | CL §6.2, §12 (`calibration_min` 50) |
| Buckets in fifths; buckets with ≥ 10 cases within 10 points | …and every prediction bucket (fifths) with ≥ 10 cases lands within 0.10 of its observed rate | not yet run | CL §6.2, §12 (`calibration_err` 0.10) |
| Words until calibrated | Until a judge is calibrated its numbers appear only in debug/workshop; the coach surface shows words ("sure" / "trying" / "no move yet") | settled by SYN #1 | CL §6.2, §9.2; SYN |

## 4. Fit — how a candidate's percentage is produced

SYN ruling: fit lives in CL's label store (an empirical rate), not
in a model judge; a model judge survives only as the fallback for
the "unfamiliar" state.

| Value | What it governs | Status | Source |
|---|---|---|---|
| k = 20 neighbours | kNN over label-store rows for (tile, intention) within radius of the observed features | guess | CL §6.2, §12 (`knn_k`) |
| α = 4, prior = verification rate | P(fit) = (successes + α·p0) / (n + α), p0 = the tile's overall verification success rate | guess | CL §6.2, §12 |
| < 5 neighbours = unfamiliar | Fewer than 5 labels in radius → situation is *unfamiliar*: P is mostly prior, tile treated as "shaky" however high P reads | guess | CL §6.2, §12 (`familiar_min_neighbours` 5) |
| 20 seeds | Counterfactual replays: after each session, every tile claiming a snapshot's intention runs 20 seeds from it — labels for tiles never picked | design | CL §6.2 |
| Swap margin = 10 points for 2 beats | A challenger replaces a running tile only if it beats it by 0.10 sustained 2 beats | guess | CL §6.4, §12 (`swap_margin`, `swap_beats`) |
| Rotate band = 5 points, 1 in 5 | Among candidates within 0.05 of the best, pick the less-used one 1 time in 5 (variety, over-010) | guess | CL §6.4, §12 (`rotate_band`, `rotate_rate`) |
| Progress < 30% for 2 beats → failing | Tile health: after the grace window, `J.progress` < 0.30 (`kill_p`) for 2 beats (`kill_beats`) marks the running tile failing | guess | CL §6.4, §12 |
| Grace = max(3 s, 0.25 × expected) | Tile-health checks are skipped during the grace period (over-008) | guess | CL §6.4, §12 (`grace`) |
| Beat budget < 2 ms | CL's whole overseer beat (coach → rails → health → tightness → interruptions → selection) must complete in < 2 ms | design | CL §6.4 |
| Beat = 8 Hz | MM's overseer beat layer cadence | **contested** (CL §12 sets `beat_hz` 4; IMPL sidesteps both — decisions only at tile boundaries, holds and the offer moment) | MM §3.1, §8.1 |
| Decisions < 12 / min; alarm at 15 | The architectural budget: a competent session makes under 12 decisions/min and authors 0–2 scripts; instrument `decisions_per_min`, alarm at 15 — if it alarms, the fix is fewer calls, not a cheaper model | design | MM §1.1 |

## 5. Tension — τ = max() of correlated risks

SYN convergence #11 (settled): tension is a **max()**, never a
sum — the inputs are correlated expressions of one or two
underlying risks, and a sum double-counts. SYN also ruled MM's
bathymetry-provenance term joins CL's formula.

MM's formula (§3.4), the only full formula either lane wrote:

```
tension = max(
  keel    = clamp((1.50 - keelBow) / 1.05, 0, 1),     // 0 at 1.50 m, 1 at 0.45 m (aground)
  ahead   = clamp((30 - clearanceAhead200m) / 25, 0, 1),
  battery = drone_out ? clamp((0.45 - battery) / 0.35, 0, 1) : 0,
  unknown = isNaN(bottomAt(bow)) ? 1
          : confidenceTier(bow) == 'interpolated' ? 0.6 : 0,
  time    = clamp(1 - horizonRemaining / horizonNominal, 0, 1)
)
```

| Value | What it governs | Status | Source |
|---|---|---|---|
| Ladder < 0.25 / < 0.45 / < 0.70 / ≥ 0.70 | Planning horizon 60 min / 10 min / 5 min / KEYHOLE (planner stands down, tiles withheld, coach surface pulses) | guess; **contested** band edges | MM §3.4 |
| Keyhole closes at < 0.35 held 4 s | …or on coach clear | guess | MM §3.4 |
| τ bands 0.3 / 0.6 / 0.85 | CL's ladder: rescore every 10 s / every 1 s / every beat; at ≥ 0.85 only **graduated** tiles with P ≥ 85% may run, else keyhole hand-off | guess; **contested** band edges | CL §7.5, §12 (`tau_bands`, `keyhole_fit` 0.85) |
| 90 s with no human → hold-station | Keyhole with nobody home: a reflex hold-station tile (no decision, no confidence) takes over and the session marks itself parked | design | MM §3.5 |
| Author pulses: τ < 0.3 only | CL: in-session pulses require calm (τ < 0.3); no pulses at τ ≥ 0.3 | guess | CL §7.5, §8.2 |

## 6. The bend rule and the prices it spends

**Bend rule** (CL §7.3, adopted as the design rule; SYN
convergence #6: bends scored with hysteresis):

For option O, build plan A′ and compute gain = V(A′) − V(A).
Bend when **all** hold:

- gain ≥ **max(10 points, margin × V(A))** — margin = **15%** by
  default (CL's V1 answer to over-002), set by the coach's
  Detours dial from **40%** (dial 0) to **5%** (dial 10). The
  absolute 10-point floor stops jitter late in a session, when
  V(A) is small.
- `J.option` ≥ **60%** (the option's judged fit).
- The rule holds on **2 consecutive scans**.

| Value | What it governs | Status | Source |
|---|---|---|---|
| bend_abs 10 pts / bend_rel 0.15 / option_p 0.60 / bend_scans 2 | The bend rule above, as threshold data | guess | CL §7.3, §12 |
| Route: cell 25 m, ≤ 8 candidates, ≤ 2 via points, time ≤ 1.25 × t0 | M2 route evaluation on the computed grid (65 candidates: 0, 1 or 2 via points); route maximises harvested value − λ × extra seconds | guess | CL §7.4, §12 |
| Implemented bend (M0) | The shipped offer is a scripted moment, scored differently: `(U·P − C)/minutes + H > current leg's valueRate`, with corridor clearance P sampled every ≤ 100 m (a sample counts good when tide − bottom ≥ 1.0 m; unmapped counts 0) and H = 0.9 (authored corridor value) | implemented | IMPL `overseer.js` (`scoreOffer`) |

**Prices** — CL §7.2. **PROVISIONAL — the owner's call**
(DESIGN-COMPARISON open ruling #1; flagged again in CL §13).
Every bend spends these; they are guesses until the owner sets
them.

| Price | Points |
|---|---|
| Shoal objective | 30 |
| Pot found | 100 |
| Home with pot | 40 |
| Wreck logged | 50 |
| Home safe without the pot (**M1 only**) | 20 |
| Hull hit | −60 |
| `reserveSpent` | −25 |
| `takingWater` | −200 |

## 7. Harvest values — the authored value field

SYN ruling: MM's authored harvest map for V1 (CL's computed grid
is the M2 growth path, inheriting the falsifiability assertion).

| Value | What it governs | Status | Source |
|---|---|---|---|
| Corridor via-waypoints > 50 m lateral off the straight line; corridor value strictly > beeline value | The falsifiability test: if a corridor adds nothing over the beeline, harvest.json is decoration, the test **fails at load**, and the bend rule is not implemented | design | MM §2.3 |
| Anti-tautology rule | Every anchor's value is authored as a property of the *water*, defensible without reference to any objective — WRECK scores 0.0 despite being a listed objective; shoal scores 2.4 because the water is good | design | MM §2.2 |
| value_rate refresh: 30 s cadence + on invalidation | Recomputed by the beat layer from harvest data + live state; invalidated by tide change > 0.1 m, battery crossing 1/3 or 2/3, a tile abort, an offer taken/refused | design | MM §2.4 |
| Stale leg: rate < 0.2 × plan-time rate | A leg whose recomputed rate falls below a fifth of its plan-time value is flagged stale and must be re-scored before the plan extends through it | design | MM §2.4 |
| HARVEST (implemented) | SPAWN 0.0 · BAYC 0.6 · shoal 2.4 · pot **1.8** · WRECK 0.0 · cove 0.0 (value-units; each host game authors its own — a port tax) | implemented | IMPL `overseer.js` |
| Corridor H = 0.9 | The implemented offer's en-route harvest: BAYC → WRECK via the shoal flank | implemented | IMPL `overseer.js` |

## 8. Tile verification numbers

Full tile contract: `docs/TILE-CONTRACT.md`. The numbers:

| Value | What it governs | Status | Source |
|---|---|---|---|
| 200 seeds per fixture | Every fixture, at both ends of every style range, flair on and off | guess (the gate itself is SYN-settled: statistical, state-grounded) | CL §5.4, §12 (`verify_seeds`) |
| ≥ 181 / 200 successes per fixture | Pass bar — Wilson 95% lower bound ≥ 0.85 | guess | CL §5.4, §12 (`verify_pass`) |
| **Zero** rail violations across all runs | Rail violations: a hull hit; `takingWater`; drone dead away from the boat; `reserveSpent` (unless the manifest declares it); an undeclared write or out-of-range value; a deadline kill, exception or timeout. (Zero in 200 runs ⇒ 95% upper bound ≈ 1.5%.) | settled as a class; count is the gate | CL §5.4 |
| Static gate: parses, exports start + tick, imports nothing, ≤ 300 lines, manifest schema-valid | First verification gate, before any fixture runs | design | CL §5.4 |
| 36,000 game-seconds per fixture; ≥ 1,000× real time | Compute budget: 200 seeds × 2 dial ends × ~90 s; M0's sim must hit 1,000× realtime per Node process (≈ 36 s per fixture per process) | design | CL §5.4 |
| Proposal check: 3 tides × 1 pack + 1 replay | MM's lighter gate for authored proposals: 4/4 → joins as v1 verified; 3/4 → rejected, script kept in a graveyard with the failure state named | guess; **partially contested** — SYN convergence #3 favours the statistical regime; the implemented harnesses run tiles at 3 tides without the 200-seed gate (that gate is M1+ work) | MM §7.3 |

## 9. Authoring budgets

| Value | What it governs | Status | Source |
|---|---|---|---|
| Five conjunctive gates (MM) | An author pulse requires ALL: misfit (best < 0.30) · situation-class recurrence ≥ 3 this session · no keyhole (tension < 0.70) · budget open · library short (no candidate ≥ MISFIT). hold_count ≥ 3 forces the arm regardless | guess | MM §7.1 |
| ≤ 1 pulse / 12 min, ≤ 3 / session, token spend < 5% of cap | MM's budget gate. (The 12 min is one anchorage→bay crossing: 4,021 m at 5.4 m/s = 12.4 min — one pulse per crossing.) | guess | MM §7.1 |
| 3 / session, ≥ 120 s apart, 1 in flight | CL's in-session pulse budget | guess | CL §8.3 |
| 10 calls / avatar / day | CL: all authoring calls (in-session + offline) per avatar per day | guess | CL §8.3 |
| Repairs: 1 per in-session pulse; 3 per wishlist item offline | Each repair counts as a call; over budget → wishlist | guess | CL §8.3; SYN (offline placement) |
| Packet cap 4k in / 2k out | MM's packet discipline: reasons-first (top-3 rejected tiles' reasons ≈ 400 tok; situation digest ≈ 300; projected questions ≈ 1,200; sheet excerpt ≈ 250; A-plan context ≈ 200; 2–3 verified tiles in full ≈ 900; rails ≈ 180). Cap enforced before the call; a non-conforming return is discarded at the API boundary, no retry loop | guess; **contested** cap value | MM §7.2 |
| Tokens per call ≤ 30k in / ≤ 4k out | CL's per-call cap | guess; **contested** — SYN ruled "MM's packet discipline (reasons first, hard token cap)" without fixing the number | CL §8.3 |
| Question projection: arm A ≤ 15 shaded questions / arm B 0 | The A/B experiment (SYN ruling: CL, outright): pulses alternate arms; after **20 pulses per arm**, compare verification pass rates, keep the better arm, record the result as evidence on over-009 | settled as an experiment | CL §8.5, §12 (`packet_questions`); SYN |
| Question beam ≈ 20–30 questions | MM's assumed projection: a graph walk from the situation's cluster, not all 271 questions | superseded by the A/B ruling above | MM §7.2 |
| Health metric | Authoring calls per hour of play must **fall** as the library grows; flat or rising for 3 weeks → stop and investigate | design | CL §8.3; SYN |
| Shadow author (implemented) | M0's whole author layer: when the gates *would* open, record the opportunity (situation class, top-3 reasons, `pulsesUsed 0 / pulsesCap 3`, hold_count) and make **no call** — escalation-rate evidence for zero tokens | implemented | IMPL `overseer.js`; MM §8.1 |

## 10. The overseer is the expensive layer (pricing)

| Value | What it governs | Status | Source |
|---|---|---|---|
| Judge ≤ 1 call / 3 s (≤ 20/min), ~600 tok/call → up to 36,000 tok/session | MM's cost table: the constant layer at full rate | design | MM §1.1 |
| Author ~6,000 tok/session | One pulse per 12 min at the packet cap | design | MM §1.1 |
| Ratio 1–6× | The layer that runs constantly costs 1–6× the layer that runs once — budget decisions/minute, not tokens | design | MM §1.1 |
| Local judge: 200–400 ms/eval | MM's M0 recommendation (0 tokens, off the render thread); API judge = 20–40× the tokens | design | MM §1.1 |
| Control judges A / B / C / D | A real · B always 0.9 (must show visible, nameable stumbles) · C always 0.3 (correct MISFIT handling; gates refuse) · D always 0.5 (dead band — hold_count 2 commits, 3 arms, session never stalls). The controls test the thresholds, not any judge's wisdom. Implemented as `always-0.9 / always-0.5 / always-0.3` beside the real heuristic judge | design; implemented | MM §8.2; IMPL `judges.js` |

## 11. Order interpreter

| Value | What it governs | Status | Source |
|---|---|---|---|
| 30 per session, ≥ 5 s apart | Budget for the small LLM call that turns a kid's free-text order into a closed-vocabulary intention or dial change (phrase table first; unmatched orders only) | guess | CL §9.3 |
| ≤ 2k tokens in, ≤ 200 out | Per-call cap; the reply is schema-checked and echoed through templates — model prose never reaches the kid | guess | CL §9.3 |
| Privacy gate | The interpreter sends kid-typed text to an LLM: consent/privacy review required before any public release involving minors (open ruling #5) | owner's call pending | CL §9.3; SYN |
