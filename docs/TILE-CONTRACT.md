# The tile contract — a checklist for tile authors in any engine

A **tile** is a verified script exposed upward as ONE named choice
the size of a human intention ("work the shoal", "hunt the pot") —
never an input, never a campaign. The overseer picks tiles; the
coach presses tiles; the tile drives the vehicle through the same
input object a human uses. If a coach can use the tile for
something else and forget how it works inside, it has passed the
light-switch test; if they have to think about its mechanics, it
isn't a tile yet.

This contract is extracted from the reference implementation —
sister repo `SuperInstance/shoalwater`, `docs/coach/tiles.js`
(+ `judges.js`, `overseer.js`, `adapter.js`) — and the two V1
designs (`docs/design-lanes/`). It is engine-neutral: the JS shape
below maps directly onto Luau ModuleScripts or any other host.
Numbers cited here live, with provenance, in
`docs/OVERSEER-NUMBERS.md`.

**Reference shape** (from `tiles.js`):

```
tile = {
  id: 'work-the-shoal',          // stable id
  name: 'work the shoal',        // the intention, in a person's words
  claims: 'work-shoal',          // the intention it claims
  precondition(ctx) -> { ok: true, ...evidence }
                     | { ok: false, reason: '…' },
  start(ctx),                    // price the run: ETA, timeout, guards
  tick(ctx, dt) -> 'running' | 'done' | 'failed',
}
```

`ctx` carries only what the adapter exposes: game state a player
could see, plus adapter instruments (bottom, confidence, pinger).
The tile's only sink is the game's input object — the same object
the keyboard, the touch stick and the demo write. Single writer,
always.

---

## The checklist

### Declare

- [ ] **id + name.** A stable id, and a name that is the intention
  a person holds, in their words. Granularity test: an intention,
  never an input ("steer 10° port" is not a tile), never a
  campaign ("do the whole mission" is a plan, not a tile).
- [ ] **claims.** The single intention this tile answers. The
  overseer's registry check is structural: an intention with no
  claimant is a misfit before any percentage is computed.
- [ ] **premise.** One sentence a coach can read verbatim —
  what it will do, in outcome language ("Put the drone over the
  pale patch, hold her close over the bottom for ten seconds,
  and bring her back with a third still in the bank").
- [ ] **costs, priced in advance.** What the run spends, declared
  before it runs: battery thirds, nominal time, what state it
  ends in. The overseer and the coach decide with the price tag
  visible, not after.
- [ ] **provenance.** Where the tile came from (hand / demo port /
  codex-projected / authored pulse / adopted) and the questions
  it answers. A codex-projected tile enters as *draft* only —
  narration authorises authoring; it is never evidence for
  deployment.

### Require — free predicates over observable state only

- [ ] **requires are free.** `precondition` is evaluated from
  adapter predicates that cost nothing — no judgement, no model
  call. If a precondition needed a decision, every beat would
  cost money and the happy path would not be free.
- [ ] **Observable inputs only — the chart-precision rule.** The
  tile sees what a player can see, at the precision a player
  gets it: charted positions at chart precision, instrument
  readouts as the HUD prints them — never exact hidden state.
  - *The pinger contract is the canonical example*
    (`adapter.js`): the pot's coordinates live only inside the
    instrument. A tile receives `{ hasReturn, rangeM (integer
    metres), bars (1–8) }`, a return only inside **150 m** —
    exactly what the game's HUD shows a human. `hunt-the-pot`
    never imports the pot's position; its fix comes from
    trilaterating three pinger range samples.
- [ ] **Fail closed.** Unmapped or unknown state makes requires
  *false*, never optimistic: the adapter returns NaN for
  unmapped bottom, NaN fails every depth test, and a corridor
  may not route through it. (The host defect this kills: the
  game once returned −60 m — "deep and safe" — outside the
  mapped pack.)
- [ ] **Authored constants are visible.** A threshold inside
  requires (the shoal's 2.3 m, the drone's 0.66 battery floor)
  is an authored judgement: versioned with the tile, justified
  in provenance or derived from a formula in the tile. A magic
  constant in requires is a review failure (MM §4.1).

### Run — bounded phases, an exit for every phase

- [ ] **Named phases.** The body is a small phase machine
  (position → go → hold → back), each phase legible in the log.
- [ ] **Every phase has an arrival exit.** Arrival is
  **scale-relative**: `dist < max(16 m, |speed| × 3)` — a fixed
  window is 3 s at transit speed and 12 s at a creep, which is
  two different tiles wearing one number.
- [ ] **Every phase has a timeout exit.** Priced at `start` from
  the shaped ETA (make-way: 2.5 × ETA + 120 s slack) and
  **hard-capped** — make-way caps at 2,700 s, because at creep
  speed the raw formula prices a 3 km leg at ~179 minutes and a
  leg that can never arrive must fail, not hold the plan open.
  Tile-level caps in the reference library: work-the-shoal
  600 s, hunt-the-pot 1,500 s, wreck-look 1,800 s.
- [ ] **Every phase has a resource-guard exit.** Battery (or the
  host's equivalent) crossing its guard abandons the objective
  phase and goes to the return phase — work-the-shoal at
  battery < 0.36, hunt-the-pot at < 0.50 (its return is longer),
  wreck-look at < 0.36. The reserve third is sacred: a tile
  that spends it silently has failed even if it "succeeded".
- [ ] **Abort conditions are declared, not discovered.** The
  schema carries an abort list (MM §4.1: `[battery_lt: 0.30,
  aground: true, tension_ge: 0.70, elapsed_over: 2.5×nominal]`)
  and the run honours it from any phase.
- [ ] **Failure flies home first.** Every abort path returns the
  vehicle to safety *before* the tile reports failure —
  hunt-the-pot's `back` phase is reached on success, on abort
  and on any failure, is itself bounded (240 s), and only then
  does the tile settle its result. A failed tile never strands
  the vehicle.
- [ ] **Recovery uses the game's own rule.** Don't invent a
  stricter arrival test than the host's recovery rule (the game
  recovers the drone within 15 m at any height; the tile
  switches at < 12 m) — a stricter test can be unreachable in
  thin water and the phase spins while the battery dies.

### Decline — a first-class outcome

- [ ] **Declining is not failing.** When the world doesn't
  support the run, `precondition` returns `{ ok: false,
  reason }` — a sentence a human can read ("the shoal carries
  only 1.4 m of water at this tide (needs > 2.3 m)"). The tile
  does not run and score zero.
- [ ] **The refusal is visible at the planner.** The overseer
  logs `tile-declined` with the reason, marks the leg declined,
  and arms a shadow-author opportunity. A tile that fails
  quietly is worse than one that refuses loudly: the log would
  claim coverage the library does not have.

### Return — outcome plus evidence

- [ ] **tick returns** `'running' | 'done' | 'failed'` — nothing
  else. Done/failed are the tile's verdict on its own run,
  including the compromised flag (work-the-shoal that came home
  on the battery guard reports `failed` even though the drone
  is safe: the objective wasn't met).
- [ ] **Evidence rides along.** The precondition returns its
  measurements (depth, battery) and the judge returns
  `{ fit, reasons[] }` — the reasons are what the coach strip
  shows and what an author packet is built from. A number
  without its reason is not evidence.

### Be judged

- [ ] **A fit heuristic exists for the tile** in the judge
  (`judges.js`): a deterministic read of adapter-visible state
  whose reasons name the governing facts. Reference examples:
  make-way scores 0.25 if the direct route leaves mapped water,
  else ~0.9 less a distance term; work-the-shoal fits from the
  depth margin over its 2.3 m floor plus battery; wreck-look
  from the cove mouth's margin over the 1.35 m keel guard.
- [ ] **The tile survives the control judges.** The band logic
  around it is tested by constant judges (always-0.9 / 0.5 /
  0.3); a tile is not done when it works under a wise judge, but
  when the *machinery* behaves under foolish ones.
- [ ] **Safety rails outrank the tile.** Possession (a human
  driving stands the whole stack down — not a failure), the
  taking-water rail (plan collapses to the home leg), and the
  keel look-ahead (water 10 m ahead under 2.0 m of clearance —
  or unmapped — caps any boat phase at creep, 1.5 m/s) apply
  inside and above every tile. Where the water isn't there, a
  tile slows and fails loudly on timeout instead of striking.

### Verify, then graduate

- [ ] **Verification before the library.** Static gate (parses;
  exports start + tick; imports nothing; ≤ 300 lines; manifest
  valid), then fixtures: 200 seeds per fixture, ≥ 181/200
  successes (Wilson 95% lower bound ≥ 0.85), **zero rail
  violations** — and declining correctly where the world doesn't
  support the run is a pass, asserted like any other
  (work-the-shoal's harness asserts the refusal at low tide).
  Numbers: `docs/OVERSEER-NUMBERS.md` §8.
- [ ] **Probation.** A verified tile runs marked "new": MM —
  an abort in live play before it earns three bindings demotes
  it back to candidates and adds that abort state to its
  harness; CL — 5 live uses with ≥ 4 successes and 0 takeovers
  earns the library proper.
- [ ] **Graduation = transfer + invisibility, ruled by the
  owner** (synthesis-converged; both lanes' bars):
  - *MM:* with its code never opened or edited, the coach has
    re-targeted it in **two different tide regimes** and at
    least **one anchor its author never used**, and it
    completed in every case with **no explanation request**.
  - *CL (measured on coach presses):* ≥ **18 of the last 20**
    pressed runs succeed; **0 takeovers** in the last 10; at
    most 1 surprise flag; pressed in ≥ **2 different plans**
    or situation signatures; code unopened during those 10 —
    plus a **teach-back**: the coach captions the tile in their
    own words, and a caption naming the outcome ("gets us into
    the cove") over the mechanics is the human evidence the
    wiring disappeared.
- [ ] **Pruning is proposed, never silent.** Triggers: MM — not
  selected in **5 consecutive sessions**, or explanation
  requests on its last 3 uses; CL — unused for 10 sessions,
  live success below 70% over 20 uses, or superseded on the
  same fixtures. Retirement is recorded in the open with the
  reason, and the owner rules. The library never grows
  unbounded (Voyager's lesson).
- [ ] **Authored tiles run boxed.** LLM-written code runs in a
  QuickJS-wasm isolate — no DOM, network, timers or host
  objects — with a **2 ms per-tick interrupt deadline**;
  exceeding it twice in a row kills the tile and the overseer
  treats it as failed (synthesis-adopted, CL §5.3).

---

## Worked examples (reference implementation, `tiles.js`)

**hunt-the-pot — pinger-only by contract.** Claims `hunt-pot`.
Precondition: the charted drainage east of the shoal carries
> 2.0 m of water, else it declines with the depth named. It never
reads the pot's position — the pot is not imported in the file.
Phases: `charge` (drone tops up aboard to ≥ 0.97 first; refuses
fast if the boat herself lies in < 1.3 m — too thin to launch) →
`listen-read` (a pinger read at the boat) → `carry` (the boat
hops 45 m east along the drainage and listens again; ≤ 5 carries,
with a 60 s watchdog if the boat can't move) → `probe` (two more
range samples on a 16 m triangle; trilaterate) → `fix` (fly the
fix; the range there must check out ≤ 12 m, one refinement round
allowed) → `hold` (descend to bottom + 1.2 m and hold the game's
find condition — within 10 m, within 3 m of the bottom, 3 s —
slow-circling after 15 s; abort at 60 s) → `back` (every outcome
flies home first; bounded 240 s). Battery guard < 0.50 aborts to
`back` from any drone phase; whole-tile cap 1,500 s.

**wreck-look — keel-guarded creep, declines a dry cove.**
Claims `wreck-look`. Precondition: the cove mouth must carry
> 1.35 m at this tide and the drone's altitude band must exist
at the wreck — otherwise it declines and the wreck "stays
unlogged rather than struck for". Phases: `creep` (boat at
1.3 m/s toward the approach point, ~25 m short of the wreck; the
keel guard — bow clearance < 1.35 m, checked 3.4 m ahead of the
bow — stops the creep where she lies, and the drone looks from
there if it can reach; too far ⇒ settle failed) → `dive` (two
orbit points at bottom + 1.4 m) → `look` (a held 3 s gaze; the
game's latch is the drone within 18 m of the wreck, near its
bottom) → `back` (recovery by proximity, bounded 240 s). Battery
guard < 0.36 returns early; whole-tile cap 1,800 s.

**make-way / work-the-shoal** — the transit primitive
(scale-relative arrival; keel-capped speed; 2.5×ETA timeout,
hard-capped 2,700 s; an unstick reflex — hung > 2 s under way,
back off 1.2 s) and the objective tile (declines under 2.3 m of
water over the shoal; boat carries the drone to the work — a
drone tile is a positioning tile with a payload; 10 s hold in
the objective band; battery guard 0.36; cap 600 s).
