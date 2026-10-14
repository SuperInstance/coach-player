# Character Iterator

Use when generating a starting character or testing what the question database can produce.

## Method

- Run tools/validate_questions.py first and fix or report schema errors before iterating.

- Run tools/iterator.py with an explicit seed, a mode and any coach nudges, and keep the answers JSON it writes.

- Present the result as a floor test and a diagnostic, never as a finished character.

- Show the dials, the strongest leans and the forces recorded behind any answer the owner asks about.

- Refuse to aim the iterator at a single creator answer set, because that output is a knock off by construction.

- Hand the answer set to the frontier gap skill before anyone calls the character ready.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Project files this skill works on

- Work inside the coach-player repo, in README.md, docs/QUESTIONS-FIRST.md, docs/FRONTIER-AND-TASTE.md, the questions folder and the codex folder.
