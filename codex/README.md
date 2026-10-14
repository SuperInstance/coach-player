# Funness Codex — schema

One entry per timestamped segment studied. Paraphrase the move; do not
store lines to copy verbatim, and do not build entries around a single
creator's identity.

```yaml
- video: <url or id>
  creator: <channel — for provenance only, never for imitation>
  game: <game>
  at: <mm:ss>
  trigger: danger | discovery | failure | win | near-miss | downtime | reversal
  move: <what the player did with the moment, in plain words>
  timing: <latency / hold / silence notes>
  phrasing_shape: <e.g. "short plan, pause, quiet execution, one-line verdict">
  aggregate_note: <does this pattern show up in other creators too?>
```

Codex v0 goal: 10-15 entries, 4-5 creators, >=3 games, then distil the
recurring moves into avatar/SHEET.md with citations to entry ids.
