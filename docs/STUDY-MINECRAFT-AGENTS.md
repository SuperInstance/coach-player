# Study — the Minecraft agent lineage

Researched 2026-10-14 at Casey's direction: the scripted bot era
and the AI agents that grew out of it. Findings paraphrased from
the projects' own papers and repos (linked); what each one proves
and what it lacks, measured against the Coach Player stack.

## Mineflayer and Baritone — the scripted motor layer (2013– )

[Mineflayer](https://github.com/PrismarineJS/mineflayer/) (PrismarineJS)
is a JavaScript API that lets a program be a Minecraft player:
spawn, chat, dig, craft, fight, plus a module ecosystem
(prismarine-physics, chunk, world, recipe...). On top of it,
[mineflayer-pathfinder](https://github.com/PrismarineJS/mineflayer-pathfinder)
and Baritone provide A* navigation with goals, movement costs,
and the ability to break/place blocks en route.

What it proves: a well-built scripted layer makes whole classes
of problems *disappear*. Nobody re-solves walking. Bots written
a decade ago still run. This is the layer Casey calls the motor:
mechanical, reliable, and — when it works — invisible.

What it lacks: everything above the waist. A Mineflayer bot does
exactly what its script says and nothing else; the choosing is
all in the human who wrote the script.

## Voyager — the LLM as script author (NVIDIA, 2023)

[Voyager](https://arxiv.org/abs/2305.16291)
([code](https://github.com/MineDojo/Voyager), Wang et al.) is the
first LLM-powered lifelong-learning Minecraft agent. Three parts:
an **automatic curriculum** that proposes ever-harder tasks, an
**ever-growing skill library of executable code**, and an
**iterative prompting loop** — GPT-4 writes a Mineflayer program
for the task, the program runs, environment feedback and errors
come back, a second model checks completion, and only verified
skills enter the library. Result headlines: 3.3x more unique
items, tech-tree milestones up to 15.3x faster than prior agents,
and skills that transfer to fresh worlds.

What it proves: Casey's core loop works. The LLM's job is to
*write scripts*; verified scripts accumulate into a library;
runtime is mostly the library running. Verification is grounded
in the game state, not in the model grading its own homework.

What it lacks (the gaps Coach Player fills):
- **The selector is the expensive model.** Retrieval is by
  embedding similarity and the decider throughout is GPT-4.
  There is no cheap overseer asking "does a script fit, and how
  sure am I" at a tiny price.
- **No human in the direction loop.** Voyager's direction is a
  self-generated exploration curriculum. Nobody coaches it,
  nobody grabs the wheel, nobody's taste is being learned.
- **The library grows unbounded**, with known retrieval strain
  as it accumulates — no pruning rite, no professional gate.

## STEVE-1 — the learned reflex (Toronto, 2023)

[STEVE-1](https://arxiv.org/abs/2306.00937) (Lifshitz et al.) goes
the opposite way: an instruction-tuned video-pretraining model
that takes short text commands ("chop a tree") and raw pixels and
emits mouse/keyboard directly, trained by hindsight relabeling
for roughly $60 of compute. It robustly completes 12 of 13
early-game tasks.

What it proves: a frozen small policy can be the muscle — cheap,
fast, reactive. This is the ancestor of the tile idea: a short
command in, a whole behaviour out.

What it lacks: it is a black box. You cannot read it, diff it,
let a kid nudge it, or ask why it chose that. No library, no
scripts, no coach surface. Coach Player wants STEVE-1's
*interface* (command in, behaviour out) with Mineflayer's
*inspectability* (the behaviour is code you can read).

## Mindcraft — the LLM in the loop, and the tiles it invented

[Mindcraft](https://github.com/mindcraft-bots/mindcraft)
(Kolby Nottingham et al., paper: *Collaborating Action by
Action*, 2025) puts LLM agents inside Minecraft over Mineflayer:
each bot reasons in chat, collaborates with other bots, and can
write and run sandboxed code. The telling detail is its
evolution: raw code generation proved unreliable for common
skills, so the project grew **parameterized commands** — instead
of generating the code to find, walk to and collect a log, the
model emits one command, `!collectBlocks("oak_log", 1)`.

That is Casey's tile, invented independently under pressure:
**the decider should choose among finished moves, not compose
mechanics.** The commands are the buttons; pressing one should
feel like the act itself.

What it lacks: the LLM still makes every decision, every few
seconds, at full price — the overseer layer is missing, so cost
and latency scale with playtime forever.

## Field evidence: the bot-army pattern (2026)

A public project running 50 Mineflayer bots as one survival
"army" states its doctrine plainly in its README: all bots run
ONE script program and take jobs from ONE board; a dispatcher
staffs jobs; **LLMs are used sparingly — event-driven operator
and help-desk roles only; everything repetitive is a script**;
outcome audits compare the world against the plan. That is
Casey's economics running in the wild, arrived at independently:
scripts carry the hours, models carry the exceptions.
