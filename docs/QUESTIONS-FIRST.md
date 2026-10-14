# Questions first — the core doctrine of this repo

Casey's direction (2026-10-14), in substance:

> Build the system that does this, not a one-shot answer. Build the
> calculator so the human does not need the model anymore. The repo
> should find the *questions* that matter about how the best game-show
> creators do what they do — even more than it answers them. A question
> that matters is one with real shading: run a judgment on it and you
> get a genuine percentage, not a coin flip. Then an iterator that
> answers many such questions can grow a rounded character who acts
> like the best of the best — shaped by the questions more than by any
> single answer, so the character can be *ourselves*, tuned by what
> the best do.

## Why questions, not answers

- **Answers expire, questions compound.** A fact about one creator's
  show dates fast. A good question keeps paying out on every new
  creator, every new game, every new session the avatar plays.
- **Answers clone, questions shape.** Copy the answers and you get an
  impersonation. Answer the same *questions* in your own distribution
  and you get a relative — same family, different person. This is the
  structural guarantee behind the roster rule: patterns, never people.
- **Questions are the curriculum.** The product's audience is clever
  middle-schoolers learning to nudge an agent. A visible bank of good
  questions teaches them what there even *is* to nudge. The question
  list is a map of the personality space.
- **Questions are portable across agents.** Any agent (Muse, a fleet
  model, a future local model) can pick up this repo and work it:
  mine questions, shade them, iterate a character. That is the point
  of building apparatus instead of answers.

## What makes a question *matter* (the shading test)

A question earns its place in `questions/questions.jsonl` only if:

1. **It is a spectrum.** Two named poles, answers land 0 to 100.
   Not yes/no, not open prose.
2. **It discriminates.** Successful creators land at meaningfully
   different places on it. If everyone clusters at one point, the
   question describes the *medium*, not a character — move it to the
   medium notes, not the character database.
3. **It is not a coin flip.** If a Jev-style judgment on a creator (or
   on our avatar) keeps returning roughly 50/50, the question is
   either badly aimed or measuring noise. Re-aim it or kill it.
   A real question returns a lean you can act on — 65/35, 80/20.
4. **It moves behaviour.** Knowing the answer changes at least one of:
   what the avatar says, when it talks, what risks it takes, how it
   treats failure, how it treats its coach, how a run is framed.
   A question whose answer changes nothing is trivia.
5. **It can gather evidence.** At least one timestamped segment, in
   principle, could shift the estimate. Unfalsifiable questions are
   philosophy, and philosophy goes in docs, not the database.

## The three jobs in this repo

1. **Mine** — find new questions from roster creators' shows
   (skill: `coach_player_question_miner`).
2. **Shade** — estimate where each creator, and each of our avatars,
   sits on each question, with percentages and evidence, Jev-style
   (skill: `coach_player_jev_shader`). Estimates start as hypotheses.
   A shading only graduates when timestamped segments back it.
3. **Iterate** — generate and evolve rounded characters by answering
   the database: start from the winners' shading distribution, bias
   with the coach's nudges, respect the rails, and write the result
   as a character sheet a kid can read and rule on
   (skill: `coach_player_character_iterator`).

## The standing warning

The database will grow large on purpose, but size is not the metric.
The metric is *discriminating power per question*: how much of a
character is pinned down by the answer. A hundred strong questions
beat a thousand flat ones, and pruning flat questions is real work,
done in the open, with the reason recorded in the question's history.
