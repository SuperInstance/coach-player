# Coach Player — a coachable auto-player with a personality

Casey's concept (2026-10-14): You don't play the character. You *coach* it.

Tell it what to play and how. It plays — moment to moment, at game speed —
and it does the last mile nobody wants to script: making that play *fun to
watch*. It notices, it gets excited, it goes quiet before a hard bit, it
explains its own screw-ups, it comments while it plays. You stay up a level,
thinking strategy the way you would in an RTS, over a game that's normally
one-character-at-a-time.

## Audience — super clever middle-schoolers (Casey, 2026-10-14)

Not "for kids" in the talked-down sense. The audience is clever
middle-schoolers who are *into the technology itself* — the same
audience Sail and Sink was aimed at (younger, quirky, physics-first).

Design consequences:
- **Don't talk down.** DanTDM / MoreAliA clarity: simple words, real
  ideas. Explain the actual mechanism (dials, memory, traits) because
  understanding the mechanism IS the fun for this audience.
- **Family-friendly defaults.** No-swearing default mode (MoreAliA's
  positioning is a feature, not a limitation), humour self-directed
  or at the game, never cruel at a person.
- **The real curriculum is nudging.** A core part of the experience —
  maybe the core — is learning how to nudge an agent into being who
  you want it to be: give an order, watch what it changes, notice what
  it *didn't* change, adjust. That's directing, prompting, and
  personality-shaping learned by play, with instant visible feedback.
- **Make the nudges legible.** Every coach order should show its
  effect: which dial moved, which trait fired, what the avatar
  remembered. Hidden magic teaches nothing; a visible sheet the
  player owns teaches everything.
- **The owner rite is the learning loop.** After a session the avatar
  proposes sheet edits ("I got braver", "I talk too much during
  hard bits") — the player approves, edits, or rejects each one,
  like Casey's RPG character diffs. The avatar only becomes who
  the player *ruled* it became. Nudging is temporary; ruling is
  permanent — that distinction is the lesson.
- **Safe rails on personality.** A player can nudge style, courage,
  chattiness, humour, focus — not the guardrails (honesty about its
  memory, no impersonation, interruptibility, family-friendly mode).
  Learning where the rails are is also part of learning agents.

## Method in one paragraph — frontier first, taste second

Not a clone of any creator (unethical, and the original stays ahead
of any copy) and not an average of the field (the average is slop).
Our Guy is thrown into the mix of the best and iterated, question by
question, against the field's frontier until he meets or rises above
it on every metric we have — that frozen character is the
**Professional Template**. Then a human tastemaker gives that
competent, tasteless template its edge through recorded choices.
Professional level first, choices second. Full doctrine:
docs/FRONTIER-AND-TASTE.md and docs/QUESTIONS-FIRST.md.

## The three layers (keep them separate — module, not brain)

### 1. Pilot — plays the game
- Drives the **same input object a human player does**. No special physics,
  no cheating state. This is the Shoalwater demo rule, already proven:
  autopilot in `shoalwater/explore.html` (public `64ffb49`) drives the same
  `input`, captions its beats, and any key/tap takes over instantly.
- Interface per game: `observe(state) -> intent` / `act(input)`.
  A game adapter is small and dumb on purpose.

### 2. Personality — renders the funness
- NOT a clone of any player. A pattern library distilled from many players.
- Lives in its own folder, like the RPG zero-agents: a character sheet,
  session memory, scars/habits, and *proposed* sheet edits after a session
  that the owner approves before they stick.
- Inputs: game events + pilot intent + coach orders.
  Outputs: commentary (text first, voice later), pacing, risk flair,
  camera/showmanship choices, when to be silent.
- Social rehearsal before render (Casey's rule, 2026-10-06): let it
  rehearse / imagine / banter in text first. By the time voice/render lands,
  we should already know what it'll sound like.

### 3. Coach — your seat
- Short, high-level orders, in fragments, at any time:
  `hunt the pot`, `play it safe`, `show off`, `explore, don't rush`,
  `be aggressive for 2 minutes`, `explain what you're doing`.
- Coach orders change *priorities and personality dials*, never frame inputs.
- Interruption is the control: any order, any time, takes effect next beat.
  Takeover to manual play is always one key/tap away (Shoalwater rule).

## The YouTube Funness Codex — what we actually learn from videos

Use the installed YouTube skill (`local-youtube-full`: search + transcripts
with timestamps) to study many let's-plays across games. Extract **mechanics,
not people**:

For each timestamped segment, tag:
- `trigger` — what just happened in-game (danger, discovery, failure, win,
  near-miss, downtime, reversal)
- `move` — what the player did with it (narrate plan aloud, go quiet,
  escalate voice, laugh at self, explain failure, callback to earlier,
  set a mini-goal, invite the audience in, celebrate small, stall for drama)
- `timing` — reaction latency, how long the beat is held, when silence works
- `payoff` — does it land? (proxy signals only: segment retention cues in
  comments/titles, view counts — never treated as proof on their own)

Output is a codex entry, not a transcript hoard:
`trigger -> move -> timing -> example phrasing shape (paraphrased, not quoted lines to copy)`

Rules:
- No impersonation, no creator's catchphrases/likeness as the product.
- Patterns aggregate across >= several creators before they become a trait.
- Every trait in the avatar's sheet cites which codex patterns it came from.

## Avatar folder shape

```
avatar/
  SHEET.md        # traits, dials (aggression, chattiness, risk, humour),
                  # likes/fears, commentary moves it owns, codex citations
  memory.md       # sessions it remembers, callbacks it can legitimately use
  sessions/       # one log per coached session: orders, events, lines said
  proposed.md     # sheet diffs proposed after play — unapplied until Casey rules
```

## V0 — plain working thing first

Don't start with an external commercial game (anti-cheat, brittle input,
no state access). Start where we already have a proven pilot:

**V0 target: Shoalwater.** Add, in order:
1. A Personality layer over the existing autopilot: event -> commentary line
   on the caption pill, with 3 dials (chatty / bold / careful) live.
2. A Coach box: typed short orders that retarget the existing route/objectives
   (`find the pot`, `go home`, `work the shoal`, `show me the wreck`).
3. One avatar folder (sheet + session log + proposed diffs).
4. Codex v0: 10-15 timestamped segments from 4-5 different creators/games,
   tagged with the schema above, feeding exactly the moves V0 uses.
   **Sampling order decided 2026-10-14: Casey's younger-audience
   (Show mode) lane first** — Neotastic, GrayStillPlays, UnspeakablePlays,
   OMB Gaming, Jesse Gillett, MoreAliA — then the Coach-mode core.

Success test for V0: Casey can sit back, watch it play and talk, issue
3 coach orders mid-run and see behaviour *and* commentary change, and take
over instantly — without touching frame inputs.

Port rule: if V0 works, the second game is chosen for state access, not fame —
a small open / browser game with readable state beats a AAA title.

## Open gates (Casey's calls, nobody else's)
- First avatar's temperament seed: scrappy / deadpan / earnest-explorer?
  (Can build all three sheets in parallel and A/B them in text rehearsal.)
- Voice in V0, or text-only until the lines prove funny on paper?
  Standing lean from prior work: text first.
