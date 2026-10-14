#!/usr/bin/env python3
"""Coach Player character iterator, v0 (stdlib only).

Grows a rounded avatar by answering the question database.
See docs/ITERATOR.md for the algorithm and the reasoning.

Usage:
  python3 tools/iterator.py --seed 7 --mode show --name Sparrow
  python3 tools/iterator.py --seed 7 --mode coach --nudge boldness:+15 --nudge chattiness:-10

A nudge names a dial (boldness, chattiness, caution, humour,
showmanship) or a question category, with a signed shift in points.
Nudges never move questions marked nudgeable: false (the rails).
Every answer records the forces that produced it, so the player can
see why their avatar is the way it is.
"""
import argparse
import json
import random
from pathlib import Path

SPREAD_SD = {"narrow": 6, "medium": 12, "wide": 20}
DIAL_CATEGORIES = {
    "boldness": {"risk", "spectacle"},
    "chattiness": {"commentary-timing", "downtime"},
    "caution": {"risk", "failure"},
    "humour": {"failure", "language"},
    "showmanship": {"premise", "escalation", "spectacle", "show-structure"},
}
MODE_BIAS = {
    "show": {"premise": 8, "escalation": 10, "spectacle": 12, "show-structure": 6},
    "coach": {"commentary-timing": 6, "coach-relationship": 8, "risk": -6},
    "both": {},
}


def load_questions(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(Path(__file__).parent.parent / "questions" / "questions.jsonl"))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--mode", choices=["show", "coach", "both"], default="both")
    ap.add_argument("--name", default="UNNAMED")
    ap.add_argument("--nudge", action="append", default=[], help="dial-or-category:+points")
    ap.add_argument("--out", default=None)
    ap.add_argument("--answers-out", default=None, help="write the answer set as JSON for tools/gap_report.py")
    args = ap.parse_args()

    nudges = {}
    for raw in args.nudge:
        key, _, val = raw.partition(":")
        nudges[key.strip()] = float(val)

    all_questions = load_questions(Path(args.db))
    questions = [q for q in all_questions if isinstance(q.get("winner_lean"), (int, float))]
    skipped = len(all_questions) - len(questions)
    if skipped:
        print(f"note: skipped {skipped} unshaded questions (winner_lean is null)", flush=True)
    rng = random.Random(args.seed)
    answers = []
    for q in questions:
        centre = float(q["winner_lean"])
        forces = {"base": centre}
        shift = MODE_BIAS[args.mode].get(q["category"], 0)
        if shift:
            centre += shift
            forces["mode"] = shift
        if q["nudgeable"]:
            nshift = 0.0
            for key, val in nudges.items():
                if key == q["category"] or q["category"] in DIAL_CATEGORIES.get(key, set()):
                    nshift += val
            if nshift:
                centre += nshift
                forces["nudge"] = nshift
        value = rng.gauss(centre, SPREAD_SD[q["spread"]])
        value = max(0.0, min(100.0, value))
        forces["sampled"] = round(value - centre, 1)
        answers.append({"id": q["id"], "category": q["category"], "value": round(value), "forces": forces})

    dials = {}
    for dial, cats in DIAL_CATEGORIES.items():
        vals = [a["value"] for a in answers if a["category"] in cats]
        if vals:
            dials[dial] = round(sum(vals) / len(vals) / 10, 1)

    strong = sorted(answers, key=lambda a: abs(a["value"] - 50), reverse=True)[:8]
    by_id = {q["id"]: q for q in questions}
    lines = [f"# Avatar Sheet — {args.name} (iterator v0, seed {args.seed}, mode {args.mode})", "", "## Dials (0 to 10)"]
    for dial, val in sorted(dials.items()):
        lines.append(f"- {dial}: {val}")
    lines += ["", "## Strongest leans"]
    for a in strong:
        q = by_id[a["id"]]
        pole = q["pole_high"] if a["value"] >= 50 else q["pole_low"]
        lines.append(f"- {a['value']}/100 toward: {pole} [{a['id']}]")
    lines += ["", "## Full answers (value, and the forces that produced it)"]
    for a in answers:
        lines.append(f"- {a['id']} ({a['category']}): {a['value']}  forces={a['forces']}")
    text = "\n".join(lines) + "\n"
    if args.answers_out:
        payload = {"name": args.name, "seed": args.seed, "mode": args.mode, "answers": answers}
        Path(args.answers_out).write_text(json.dumps(payload, indent=1) + "\n")
    if args.out:
        Path(args.out).write_text(text)
        print(f"wrote {args.out}")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
