# Script-First — the runtime stack

Casey's architecture, stated 2026-10-14 and studied against the
Minecraft agent lineage (docs/STUDY-MINECRAFT-AGENTS.md). The
LLM is the creative one. The Jev is the deciding one. The motor
knows how to put the shirt on, so the deciders have fewer and
smaller decisions to make.

## The stack, bottom to top

**1. Motor — scripts and tiles.** Finished, tested behaviours
that drive the same input object a human player drives. A
script is code. A **tile** is a script (or tight script chain)
exposed upward as ONE choice with a name a person would use:
the way a fighting-game button means *punch* — the player never
thinks about sprite frames or collision boxes, the press and
the act are the same thing.

**2. Overseer — Jev judges.** Cheap judges running constantly,
scoring the questions that matter: does an existing tile fit
this situation, and how confident are we? Which tile? Is the
current tile failing? Is this interruption worth more than the
plan? Most ticks of the game, only this layer thinks, and it
thinks in percentages at a tiny price.

**3. Author — the LLM, in pulses.** When the overseer's honest
answer is *none of these are good enough*, the system calls the
LLM to write a new script — rarely, on a budget. The call is
not cold: the question graph projects into it. Hundreds of
shaded questions about this situation, this game, this avatar
ride along, so the author starts from a vast array of what
matters instead of a blank prompt. A new script that verifies
joins the library permanently; the LLM has worked itself a
little further out of a job.

**4. Coach — the human.** Sets the day's intent, nudges the
avatar's dials, and grabs the wheel in the keyholes — the tight
first-time passages where no overseer should be trusted to react
in time. The coach never composes mechanics either; the coach
coaches.

## Tiles: projected from watching, finished when invisible

Where do tiles come from? From the Codex work. Listening to
hundreds of hours of expert play and asking enough questions,
we **project the lower mechanics the players are actually
executing** underneath their narration — the reset discipline,
the forensic pause, the escalation structure — and those
projected mechanics crystallise into the tile vocabulary. The
questions find the mechanics; the mechanics become buttons.

A tile is finished when it meets the **light-switch test**:
you flip a switch to use the light for something else, and you
forget the wiring entirely — switch and light are one. If the
coach has to think about what a tile *does mechanically*, the
tile is not done. The code has to be so good it goes invisible,
so the player stops thinking about the code and feels only the
act: I punched him, his energy went down, that *felt* right.

Granularity rule that follows: a tile is the size of an
intention a person can hold ("work the shoal", "sell the fake",
"mop up the disaster"), never the size of an input
("press W for 0.4 s") and never the size of a campaign.

## The A-plan: a route you hope gets interrupted

The session structure is Casey's trolling day in Sitka Sound.
Before the day begins there is an **A-plan**: the route the boat
would troll for twelve hours if nothing happened — thirty miles
of decent water, chosen from fifteen years of knowing the
bottom, the tide, and where the water moves. The A-plan is a
script: complete, sensible, running by default.

The hope is to be *interrupted*. A strike. A text from a boat
nearby sitting on fish. Then the plan bends toward the
interruption — but never beelines: the bottom still matters,
the gear's depth still matters, and the re-route is chosen to
pass the highest-probability water on the way, because every
hour counts and a king salmon is a hundred-dollar bill. The
overseer does exactly this in game terms:

- run the A-plan tile chain by default;
- score every interruption against the plan (Jev percentages,
  not vibes);
- bend toward the better option *through* the good water —
  the route to the new target should harvest value en route;
- as the situation tightens, shorten the planning horizon:
  an hour at a time, ten minutes, five — until the keyhole,
  where the coach grabs the wheel and the stack honestly
  stands down.

One fish an hour feels good; five an hour feels super good;
zero is fine too, because the A-plan was worth trolling anyway.
A session designed this way never has dead air: either the
plan is good, or something better interrupted it.

## What this changes in the build order

1. The Pilot ships as a **tile runner**, not a behaviour tree:
   tiles in, input-object frames out.
2. Every tile carries the questions it answers (its projection
   provenance) and the Jev confidences that gate it.
3. The overseer is a separate small component with a hard
   budget: it may escalate to the Author, it may never *become*
   the Author by calling the LLM every tick.
4. Authoring events are logged like Voyager's verifications:
   script proposed → run → game state checked → library or
   rejected, with the question set that primed the call saved
   alongside, so the library's growth is auditable.
5. The coach surface presents tiles and dials, never code.
   Code appears only in the workshop (debrief), where scripts
   are reviewed, pruned, and graduated — the pruning rite is
   what keeps the library from Voyager's unbounded growth.
