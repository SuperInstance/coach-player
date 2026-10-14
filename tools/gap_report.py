#!/usr/bin/env python3
"""Frontier gap report, Phase 1 of docs/FRONTIER-AND-TASTE.md.

Compares one character answer set (from tools/iterator.py
--answers-out) against a field profile file, question by question.
The field profile gives, per question, the professional band the
winners occupy: [band_low, band_high]. Our Guy is:

  below floor  -> value under band_low (gap = band_low - value)
  in the band  -> professional on this question
  above band   -> value over band_high (a lean stronger than the
                  field norm: a strength, or a taste candidate)

The report never averages. Strengths and gaps stay separated, gaps
sorted largest first, because the loop iterates on gaps only.

Field profile format (JSON):
{"questions": {"<question-id>": [band_low, band_high], ...}}
Real profiles will be built by the jev_shader skill from timestamped
evidence into profiles/. Until then, any profile is a hypothesis and
must be named like one.

Usage:
  python3 tools/gap_report.py --guy characters/guy.json --field profiles/field.json
"""
import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--guy", required=True)
    ap.add_argument("--field", required=True)
    args = ap.parse_args()

    guy = json.loads(Path(args.guy).read_text())
    field = json.loads(Path(args.field).read_text())["questions"]
    values = {a["id"]: a["value"] for a in guy["answers"]}

    gaps, in_band, above, missing = [], [], [], []
    for qid, (low, high) in sorted(field.items()):
        if qid not in values:
            missing.append(qid)
        elif values[qid] < low:
            gaps.append((low - values[qid], qid, values[qid], low, high))
        elif values[qid] > high:
            above.append((qid, values[qid], low, high))
        else:
            in_band.append(qid)

    gaps.sort(reverse=True)
    print(f"Gap report for {guy.get('name', 'Our Guy')} against {args.field}")
    print(f"questions compared: {len(field)} | in band: {len(in_band)} | above band: {len(above)} | below floor: {len(gaps)} | missing: {len(missing)}")
    print("\nGAPS, largest first (iterate on these):")
    for size, qid, val, low, high in gaps:
        print(f"  -{size:>3}  {qid}: ours {val}, professional band {low} to {high}")
    print("\nABOVE THE FIELD BAND (strengths / taste candidates):")
    for qid, val, low, high in above:
        print(f"  {qid}: ours {val}, band {low} to {high}")
    if missing:
        print("\nMISSING from Our Guy's answer set:", ", ".join(missing))
    verdict = "PROFESSIONAL GATE PASSED on this profile" if not gaps and not missing else "below the professional gate, gaps listed above"
    print(f"\nVerdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
