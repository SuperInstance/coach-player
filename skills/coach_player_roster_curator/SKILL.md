# Roster Curator

Use when a new creator is suggested for the codex or when roster facts need rechecking.

## Method

- Verify the channel before proposing it, using channel info from the YouTube skill in this repo and a web search cross check.

- Record title, handle, subscriber count and video count exactly as the source returned them, with the date of the check.

- Assign exactly one archetype and name what the avatar learns from this creator and what it must not take.

- Reject a candidate whose archetype duplicates a roster member unless the difference is stated in one sentence.

- Mark any count you could not verify as unverified instead of estimating it.

- Write the entry into codex/ROSTER-PROPOSED.md as proposed until the project owner rules on it.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Project files this skill works on

- Work inside the coach-player repo, in README.md, docs/QUESTIONS-FIRST.md, docs/FRONTIER-AND-TASTE.md, the questions folder and the codex folder.
