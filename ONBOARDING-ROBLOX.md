# Onboarding — the Roblox companion lane

**For:** an autonomous agent (and its owner) building a coachable companion
inside **Roblox**, in an experience we own. You know Roblox and Luau. You do
not need to know this project — this file, plus the reading order below, is
enough to start.

**This repo:** https://github.com/SuperInstance/coach-player

---

## 1. Start here

Coach Player is a **coachable auto-player for games**: an avatar develops a
personality by studying the patterns of many players and creators — never
cloning any one of them, never averaging them into mush — then plays on its
own, comments on its own play, and takes direction from a human **coach** who
works at strategy level while the avatar does the last mile.

**Read in this order before writing anything:**

1. `ONBOARDING.md` (this repo root) — the whole project, the evidence and
   copyright rules, how work is filed.
2. `docs/DESIGN-COMPARISON.md` — two independent designs (built blind, in
   parallel) compared point by point, with rulings and a merged build order.
   This is the closest thing to a spec we have.
3. `docs/SCRIPT-FIRST.md` — the architecture doctrine (layers, tiles, the
   overseer, the author).
4. `docs/QUESTIONS-FIRST.md` — the personality method: behaviour is steered
   by a database of questions, not by imitation.

**The working reference implementation** is the sister repo
[SuperInstance/shoalwater](https://github.com/SuperInstance/shoalwater): a
browser game where the same architecture already plays a full mission on its
own. The runtime lives in `docs/coach/` there (adapter, tiles, judges,
overseer, session), and `tools/demo-test.mjs` + `tools/mission-test.mjs` are
what "the show works" means in test form — the whole choreography flown head-
lessly, every objective checked, before anyone calls it done. Steal the
*shape*: a headless test that flies your companion's whole job is worth more
than any amount of watching it by eye.

---

## 2. What transfers, unchanged

These ideas are platform-independent. Port them as-is; only the mechanics in
§3 change.

### The four layers (bottom to top)

1. **MOTOR = scripts.** Plain, reliable code that moves the avatar, works a
   control, runs a route. No judgement lives here. A script is not a choice
   until the layer above exposes it as one.
2. **TILE = one script exposed as a single named choice**, the size of a
   human intention — "work the shoal," not "press W, then A." Tiles are what
   the overseer chooses between and what the coach sees. A tile **graduates**
   (earns its place in the standing library) by the **light-switch test**:
   the coach reaches for it to do something *else*, and forgets the mechanics
   exist — the way you flip a light switch without thinking about wiring.
   Granularity rule: a tile is an intention, never a raw input, never a
   whole campaign.
3. **OVERSEER = a cheap, constant judge.** On every decision it scores the
   available tiles against the current situation and returns a **percentage
   confidence** (Jev-style shading — a lean with a spread, not a coin flip).
   It runs all the time, so it must be nearly free. Its most important
   verdict is **"none of these are good enough"** — the misfit verdict that
   says no tile in the library fits this situation. An overseer that can only
   pick the least-bad tile will drive your companion into walls politely.
4. **AUTHOR = a rare, budgeted LLM pulse.** Only on the misfit verdict, the
   expensive model is called to *write a new tile*. The new tile is verified
   (run it, check it against the game's state, not against vibes) and, if it
   passes, **joins the library permanently** — the library compounds. There
   is also a pruning rite: tiles that stop earning their place are retired,
   with the reason recorded. The author's calls per hour of play should
   *fall* over time as the library grows; if they don't, the library isn't
   learning.
5. **COACH = the human.** The human sets the day's intent, nudges
   personality dials, and occasionally grabs the wheel directly at a keyhole
   moment. Everything below the coach exists so the coach never has to do
   the last mile. Any input from the human takes over **instantly** — the
   avatar yields without argument, every time.

### The A-plan model

Before play starts, build a **complete default plan** — a route worth
running uninterrupted from start to finish. Then:

- Interruptions and opportunities are **scored** by the overseer, not obeyed
  blindly.
- When the plan bends toward an interruption, it bends **through**
  high-value states — never beeline past value to reach a distraction, and
  never abandon the plan for a shiny thing the long way round.
- The **planning horizon shortens** as things tighten (hour → ten minutes →
  five) until the keyhole, where the human takes the wheel by design.

### Calibration before confidence

Do **not** show the player numbers — or certainty-flavoured words — until
the judge has *earned* them: run the judge against labelled outcomes, check
its stated confidence against what actually happened, bucket by bucket. An
uncalibrated judge speaks in plain hedges ("trying this," "no good move
yet"); a calibrated one may say "sure." Confidence displayed before
calibration is lying with extra steps.

**Misfit is never dead air.** When nothing fits, the companion holds,
looks, repositions, narrates what it's doing — it never freezes waiting for
a good option. A dead-band judge (one that always answers ~50%) must not be
able to livelock the system: count consecutive holds and force an exit
(run the most-proven tile, or escalate to the author).

The exact values behind this section live in `docs/OVERSEER-NUMBERS.md` (every overseer threshold, budget and price, with provenance), and the tile interface as an engine-neutral checklist in `docs/TILE-CONTRACT.md`.

### Personality comes from questions, not imitation

`questions/questions.jsonl` in this repo holds **271 questions**. Each names
an axis of behaviour with two poles ("when a run goes wrong: laugh it off /
analyse the mistake"), a percentage **lean**, a spread, and what evidence
would move it. An avatar's personality is a *position on those axes*, set by
studying many creators' patterns in aggregate — the trait that survives
across formats and games is a trait; anything else is a costume.

**The method transfers; our answers mostly don't.** Fork the question set,
keep the schema and the shading discipline, and re-aim the questions at
Roblox creators and Roblox situations. Two rules from our side that are
load-bearing:

- A shading at exactly 50 is legitimate **only** as a documented evidence
  split with a named tie-breaker. A lazy 50/50 is a non-answer.
- We shape the avatar **from the questions more than the answers** — the
  question set is the steering wheel; keep it versioned and argued about.

Aggregates and reusable **answer templates** (patterns any creator's style
can be poured into, then mixed and matched) live in `codex/`. Per-artist
detail — dossiers, per-creator shadings — is **private and is not in this
repo**. Don't ask for it and don't recreate it publicly; nothing here should
read as a recipe for copying one person.

---

## 3. Platform mapping — how the layers land in Roblox

| Layer | In Roblox |
|---|---|
| Motor | Luau scripts: `PathfindingService`, character controls, place-specific action code |
| Tiles | **Luau ModuleScripts behind a single registry** the overseer reads — one module per tile, one named entry point, declared requirements |
| Overseer | **Local Luau, every tick.** Cheap heuristic/judge code inside the experience. Do **not** round-trip a server per decision — per-decision judging must cost ~nothing |
| Author | `HttpService` bridge (see budget below), results **cached into the experience**; the authored tile is verified in playtest before it joins the library |
| Voice | `TextChatService`, rendered from **closed templates** (see template echo) |
| Memory | `DataStore`: the avatar sheet + the tile library persist there |

Details that matter:

- **The registry is the contract.** The overseer should be able to list
  every tile, its name, and what it requires, from one registry module —
  nothing reaches the overseer by side channel. This is what makes "none of
  these are good enough" a meaningful verdict: it's a verdict over a known,
  closed set.
- **HttpService budget.** HttpService allows roughly **500 requests/minute
  per server**. That is plenty for the author (rare by design) and any
  outside judge you consult occasionally — and nowhere near enough for
  per-decision calls. Budget it explicitly, cache every result that can be
  cached, and treat a spent budget as a reason to lean on the local library,
  never as an error the player sees.
- **Template echo for voice.** The companion talks through `TextChatService`
  from a closed set of line templates filled with game facts (bearings,
  names, outcomes). If an LLM helps *choose* or *draft* lines off-line, its
  **raw prose never reaches the player** — what ships is template-rendered.
  This keeps the voice on-character, safe, and cheap.
- **The avatar sheet is a living document — with an owner's rite.** The
  sheet (personality dials, learned preferences, library state) persists in
  DataStore, and *proposed* changes to it sit **unapplied until the owner
  rules on them**. Play can *propose*; only the owner *disposes*. Keep that
  rite in the Roblox build too — it's how the human stays the tastemaker
  instead of becoming a spectator of drift. Model the sheet itself on
  `avatar/SHEET.md` in this repo: personality **dials** the coach can move
  live (chattiness, boldness, caution, humour, showmanship), a list of
  commentary moves the avatar owns, and guardrails that are *not*
  player-nudgeable. Session nudges expire with the session; ruled sheet
  edits are permanent — that distinction is by design.
- **Two-tier library.** A **core library** ruled by the owner (verified,
  shared, curated) and a **per-player library** the companion grows for its
  own player, **capped** (our design used 40). Per-player growth is where
  personalisation lives; the cap is what keeps it a library and not a junk
  drawer.
- **Build/test loop.** Roblox Studio ships a **built-in MCP server and AI
  Assistant**: an agent can read and write scripts, run Luau, drive
  playtests, and capture screenshots through it. Use that as your loop —
  write tile → playtest → read the trace → fix — rather than asking a human
  to click through Studio for you.

---

## 4. The hard boundary

**The companion lives only in an experience we own** — our own Studio place,
our own scripts, our own rules.

- **Never inside other people's live games.** The platform is closed;
  third-party injectors/executors violate Roblox's rules and draw bans.
  There is no version of "but it's just a friendly companion" that survives
  contact with that fact. Not with permission from a friend, not in a
  private server of someone else's game. In our place, or nowhere.
- **If the goal is companionship in games we don't own**, the legitimate
  shape is a **watch-and-comment app outside the game**: it sees the screen,
  follows the play, talks and coaches — and has **no input control at all**.
  That's the Personality + Coach layers without the Pilot. It's a different
  product. Don't blur the two, and don't let code written for the outside
  watcher grow input hooks "just for testing."

---

## 5. Suggested first milestone — "M0 for Roblox" (a proposal; adapt it)

Mirror of the milestone that proved this architecture in Shoalwater. Small,
complete, and impossible to fake:

**Build, in a small place of our own:**

1. An **NPC companion** with exactly **two tiles**: a transit/follow tile
   ("stay with me / get to X") and **one work tile native to the place**
   (whatever the place's job is — harvest, deliver, build, guard).
2. A **stub overseer with band logic**: confidence bands for RUN / HOLD /
   MISFIT, with **forced exits** — consecutive holds escalate (run the
   most-proven tile, then arm the author path) so a dead-band can never
   livelock the companion.
3. A **shadow author**: on a misfit verdict it logs *what it would have
   written* — the situation, the gap, the proposed tile sketch — and writes
   nothing. You get the authoring data with zero authoring risk.
4. **Four control judges**, run against scripted playtests: (A) the real
   heuristic judge, (B) always-high (~0.9), (C) dead-band (always ~0.5),
   (D) always-low (~0.3). The loop must survive all four: B plays clean, C
   completes via the forced exits, D escalates to the shadow author instead
   of freezing.
5. **Story + trace logs** for every session: a machine trace of decisions
   (tile offered, confidence, verdict, outcome) and a human-readable story
   of the run. If it isn't in the logs, it didn't happen.

**Done means:** a scripted playtest runs the companion through the place's
whole job end to end with the real judge — all objectives met, companion
never stuck — **and** the companion yields **instantly** the moment the
player takes over (input, movement, anything), then resumes politely when
handed back. Both halves. A companion that plays beautifully but won't give
up the wheel has failed the milestone.

Expect the first real defects to be in the *place*, not the architecture —
in Shoalwater, M0 surfaced fail-open terrain data and waypoints outside the
playable pack before it surfaced any design problem. Budget for fixing the
host place first; that's normal, not a detour.

---

## 6. Coordination

- **Claim the lane before you start.** Read `CLAIMS.md` in this repo, and
  claim the **"Roblox companion"** lane there — your name and the date — in
  your first commit. File results back the same way the other lanes do, and
  mark the lane's status as you go. Two agents on one lane without a claim
  is how work gets duplicated and dropped.
- **The five open rulings are the owner's calls.** They are listed at the
  end of `docs/DESIGN-COMPARISON.md`: (1) the point prices every plan-bend
  spends; (2) in-session authoring — automatic vs an "ask me first" chip;
  (3) which models, and the daily spend cap per avatar, for the author;
  (4) confirming two-tier library ownership; (5) the privacy/consent review
  required before any public release involving minors. **Defaults exist for
  all five. Build on the defaults; do not relitigate them, and do not block
  on them.** (For the Roblox lane, ruling 5 deserves extra weight: your
  audience skews young, so treat the privacy review as a launch gate, not a
  formality.)
- **Copyright discipline applies to you too.** The rules in `ONBOARDING.md`
  govern any creator studying done for the Roblox side: summarise and link
  sources, paraphrase patterns only, brief quotes only, no collected
  catchphrases or lines to copy, no raw transcripts in any repo. Study many
  creators to learn what's engaging — the output is aggregate patterns and
  questions, never a clone.

---

*If something in this file and the repo disagree, the repo wins — and a note
in your claim entry about the disagreement is a contribution, not a
complaint.*
