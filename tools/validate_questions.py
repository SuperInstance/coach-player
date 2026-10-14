#!/usr/bin/env python3
"""Validate the Coach Player question database.

Checks schema, unique ids, and reports flatness: a question whose
winner_lean sits near 50 is a suspected coin flip and gets flagged
for re-aiming or pruning. See docs/QUESTIONS-FIRST.md.

Usage: python3 tools/validate_questions.py [path-to-jsonl]
"""
import json
import sys
from pathlib import Path

REQUIRED = {
    "id": str, "category": str, "question": str, "pole_low": str,
    "pole_high": str, "why": str, "winner_lean": (int, float, type(None)),
    "spread": str, "nudgeable": bool, "mode": str, "status": str,
    "evidence_needed": str,
}
SPREADS = {"narrow", "medium", "wide"}
MODES = {"show", "coach", "both", "maker"}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "questions" / "questions.jsonl"
    errors, flat, ids = [], [], set()
    rows = 0
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        rows += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {lineno}: bad JSON: {exc}")
            continue
        for field, kinds in REQUIRED.items():
            if field not in row:
                errors.append(f"line {lineno}: missing {field}")
            elif not isinstance(row[field], kinds):
                errors.append(f"line {lineno}: {field} has wrong type")
        if row.get("id") in ids:
            errors.append(f"line {lineno}: duplicate id {row.get('id')}")
        ids.add(row.get("id"))
        if row.get("spread") not in SPREADS:
            errors.append(f"line {lineno}: spread must be one of {sorted(SPREADS)}")
        if row.get("mode") not in MODES:
            errors.append(f"line {lineno}: mode must be one of {sorted(MODES)}")
        lean = row.get("winner_lean")
        if isinstance(lean, (int, float)) and not 0 <= lean <= 100:
            errors.append(f"line {lineno}: winner_lean out of range")
        if isinstance(lean, (int, float)) and 45 <= lean <= 55:
            flat.append((row.get("id"), lean))
    print(f"{rows} questions checked in {path.name}")
    print("Note: winner_lean may be null for design questions that have no creator shading yet. Nulls are counted in the run output of the merge step and are skipped by the iterator.")
    if flat:
        print(f"FLAT (coin-flip smell, lean 45 to 55): {len(flat)}")
        for qid, lean in flat:
            print(f"  {qid}: lean {lean}")
    for err in errors:
        print(f"ERROR: {err}")
    print("OK" if not errors else f"{len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
