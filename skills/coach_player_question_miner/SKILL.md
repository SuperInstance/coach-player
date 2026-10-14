# Question Miner

Use when the question database needs to grow in a specific direction.

## Method

- Start from a gap, either a category with few questions or a creator nobody can yet describe on the current database.

- Phrase each candidate as a spectrum with two named poles and a 0 to 100 answer range.

- Write the why line as a behaviour the answer would change, and drop the question if no behaviour changes.

- Estimate a provisional winner lean and spread and mark the entry as a hypothesis with the evidence that would settle it.

- Reject a question that every successful creator would answer the same way, and record the rejection reason in the inbox notes.

- Write survivors to questions/inbox as JSONL in the schema from docs/QUESTIONS-FIRST.md and run the validator before reporting.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Project files this skill works on

- Work inside the coach-player repo, in README.md, docs/QUESTIONS-FIRST.md, docs/FRONTIER-AND-TASTE.md, the questions folder and the codex folder.
