# Frontier first, taste second — the loop that is not a clone and not an average

Casey's correction (2026-10-14), which governs everything in this repo:

- **Cloning one creator is out** — not ethical, and not even productive:
  the original keeps being fresh, and a copy is always behind him.
- **Averaging the field is also out.** The homogeneous average of what
  the best do is exactly what people mean by AI slop: competent,
  smooth, and nobody's. An average has no edge because every strong
  lean cancels against another strong lean.
- The question database makes both failure modes *possible* — you can
  aim it at one creator's answers and get a knock-off, and you can aim
  it at the centroid and get slop. Both are useful as floor tests and
  as proof the questions have power. Neither is the product.

## Phase 1 — the frontier loop (a GAN in an environment, not a duel)

Classic GAN thinking is one generator against one discriminator, and
Casey's standing critique of closed loops applies: the ceiling is the
sharpener. This loop is shaped differently:

1. **Profile the field.** Every roster creator gets a shading per
   question (skill: `coach_player_jev_shader`), from timestamped
   evidence. The field is an *environment*, not an opponent.
2. **Profile Our Guy** on the same questions, from his actual sessions
   (or, before he has sessions, from his current answer set).
3. **Ask the only question that matters: how are they different from
   our guy?** Per question, the gap report (tool: `tools/gap_report.py`)
   compares Our Guy against the field *frontier* for that question —
   for "higher is stronger" metrics, the relevant best-in-field
   region; for spectrum questions, distance from the professional
   band the winners occupy. Not against the mean. Never the mean.
4. **Iterate on the gaps, largest first.** Each round of play, rehearsal
   or study targets specific questions where Our Guy is below the
   professional floor, the way a player grinds a weak stat. Strengths
   are left alone. This is selective rising, not blending.
5. **The professional gate.** When Our Guy meets the floor on every
   metric we can think of — and the metric set itself keeps growing
   with the question database — we freeze that answer set and name it
   the **Professional Template**. It is deliberately tasteless:
   awesome on paper, nobody's favourite, and that is expected.

## Phase 2 — the tastemaker (the open loop that breaks the ceiling)

Only a frozen professional template earns the right to taste:

- A human tastemaker — Casey at project level, the kid coach at
  product level — now asks the identity questions: *who are we, what
  is this show, what do we love that the field does not do?*
- Taste is applied as **recorded deviations** from the template:
  each nudge that moves an answer away from the professional band is
  logged with its reason ("we go quiet twice as long as anyone
  before a sinking — that dread is our thing"). Deviations without
  reasons are drift; deviations with reasons are identity.
- Because the template underneath is professional, the deviations
  read as *edge*, not as incompetence. That is the whole sequence:
  **professional level first, choices second.** Slop is choices made
  by something that never reached the level; access-television work
  is the level with no choices ever made.

## Where this leaves the tools

- `tools/iterator.py` in average mode is a **floor-test instrument**:
  it proves the questions can mint a knock-off or a centroid.
  Its output is a starting answer set and a diagnostic, never a
  finished character.
- `tools/gap_report.py` is the Phase 1 engine: Our Guy vs the frontier,
  per question, strengths and gaps separated.
- Taste lives in the character's `taste.md` (deviations + reasons),
  applied after the template freezes, ruled on by the owner like any
  other sheet change.
