# Codex Sampler

Use when sampling a roster creator for the funness codex.

## Method

- Pick a full run or a long segment over a highlight edit when the question is about timing or downtime.

- Fetch the transcript with timestamps through the YouTube transcript route described in the repo docs.

- Tag each useful segment with the in game trigger, the player move, the timing and a paraphrase of the phrasing shape.

- Paraphrase every phrasing shape and never store a line to copy or a catchphrase to reuse.

- Attach each entry to at least one question id from questions/questions.jsonl or flag it as a candidate for a new question.

- Stop after the segments that change an estimate and say plainly when a video yielded nothing.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Project files this skill works on

- Work inside the coach-player repo, in README.md, docs/QUESTIONS-FIRST.md, docs/FRONTIER-AND-TASTE.md, the questions folder and the codex folder.
