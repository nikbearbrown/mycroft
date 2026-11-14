"""How far do the judge's verdicts agree with a human's?

Sprint 6. The judge is cheap and scales; a human is neither. The only question
that matters is whether the cheap one can stand in for the expensive one, and
the only way to answer it is to have both score the same pairs independently
and compare.

Three numbers, in increasing order of honesty:

  raw agreement -- how often they picked the same thing. Flattering and nearly
    useless on its own: two raters who always say "tie" agree 100% of the time
    while measuring nothing.
  Cohen's kappa -- agreement above what their own answer distributions would
    produce by chance. Zero means the agreement observed is exactly what
    guessing would give. UNDEFINED when expected agreement is 1.0, which is
    itself a finding.
  the decisive subset -- pairs where at least one of them picked a winner.
    This is where a judge earns its place, and where disagreement costs money.

Order bias is reported for the human too, from which answer was shown first.
The judge's was measured by swapping; the human's is measured the same way.

Usage:
    python scripts/gateway/bench/agreement.py
    python scripts/gateway/bench/agreement.py --scores <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

RESULTS_DIR = Path(__file__).with_name("results")
SCORES_DIR = Path(__file__).with_name("scores")

# A verdict is comparable only if it is a verdict. `inconsistent` means the
# judge contradicted itself on the swap; `unparsed` means it did not answer.
# Neither is a judgment about the answers, so neither is scored as a
# disagreement -- they are counted and reported separately.
VERDICTS = ("a", "b", "tie")


def latest_scores(scores_dir: Path = SCORES_DIR) -> Path | None:
    files = sorted(scores_dir.glob("*.json"))
    return files[-1] if files else None


def kappa(pairs: list[tuple[str, str]]) -> tuple[float | None, float, float, str]:
    """Cohen's kappa over (human, judge) picks. Returns (kappa, po, pe, note)."""
    n = len(pairs)
    if not n:
        return None, 0.0, 0.0, "no comparable pairs"

    po = sum(1 for h, j in pairs if h == j) / n
    human = {c: sum(1 for h, _ in pairs if h == c) / n for c in VERDICTS}
    judge = {c: sum(1 for _, j in pairs if j == c) / n for c in VERDICTS}
    pe = sum(human[c] * judge[c] for c in VERDICTS)

    if abs(1.0 - pe) < 1e-12:
        return None, po, pe, ("undefined: expected agreement is 1.0, so there is "
                              "no room above chance to measure")
    return (po - pe) / (1 - pe), po, pe, ""


def _counts(key: str, population: list[dict[str, Any]]) -> dict[str, int]:
    return {v: sum(1 for j in population if j[key] == v) for v in VERDICTS}


def analyse(scores: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Join the human's picks to the judge's verdicts and count what happened."""
    by_pair = {r["pair_id"]: r for r in rows}

    joined, missing = [], []
    for score in scores:
        row = by_pair.get(score["pair_id"])
        if row is None:
            missing.append(score["pair_id"])
            continue
        joined.append({
            "pair_id": score["pair_id"],
            "task_type": score["task_type"],
            "human": score["pick"],
            "judge": row["result"],
            "shown_first": score.get("shown_first"),
            "picked_position": score.get("picked_position"),
            "note": score.get("note", ""),
        })

    comparable = [j for j in joined if j["judge"] in VERDICTS]
    not_a_verdict = [j for j in joined if j["judge"] not in VERDICTS]
    disagreed = [j for j in comparable if j["human"] != j["judge"]]

    k, po, pe, note = kappa([(j["human"], j["judge"]) for j in comparable])

    # Where at least one rater committed to a winner. A pair both called a tie
    # tells you nothing about either rater's discrimination.
    decisive = [j for j in comparable if j["human"] != "tie" or j["judge"] != "tie"]

    per_task = {}
    for task in sorted({j["task_type"] for j in joined}):
        subset = [j for j in comparable if j["task_type"] == task]
        tk, tpo, _, tnote = kappa([(j["human"], j["judge"]) for j in subset])
        per_task[task] = {
            "comparable": len(subset),
            "agreed": sum(1 for j in subset if j["human"] == j["judge"]),
            "raw_agreement": tpo,
            "kappa": tk,
            "kappa_note": tnote,
            "human": _counts("human", subset),
            "judge": _counts("judge", subset),
        }

    picked_first = sum(1 for j in joined
                       if j["picked_position"] == "first" and j["human"] != "tie")
    picked_second = sum(1 for j in joined
                        if j["picked_position"] == "second" and j["human"] != "tie")

    return {
        "scored": len(joined),
        "comparable": len(comparable),
        "not_a_verdict": len(not_a_verdict),
        "missing_from_results": missing,
        "agreed": len(comparable) - len(disagreed),
        "disagreed": len(disagreed),
        "raw_agreement": po,
        "kappa": k,
        "kappa_note": note,
        "expected_by_chance": pe,
        "human_picks": _counts("human", joined),
        "judge_picks": _counts("judge", joined),
        "decisive_pairs": len(decisive),
        "human_order_bias": {"picked_the_first_shown": picked_first,
                             "picked_the_second_shown": picked_second},
        "per_task": per_task,
        "disagreements": disagreed,
        "judge_non_verdicts": not_a_verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure agreement between a human's blind scores and the judge.")
    parser.add_argument("--scores", help="a scores file (default: the newest)")
    args = parser.parse_args()

    scores_file = Path(args.scores) if args.scores else latest_scores()
    if scores_file is None or not scores_file.exists():
        print("No scores file found. Run score.py first.")
        return 1

    scored = json.loads(scores_file.read_text(encoding="utf-8-sig"))
    results_file = RESULTS_DIR / scored["results_file"]
    if not results_file.exists():
        print(f"The results file this was scored against is missing: {results_file}")
        return 1
    data = json.loads(results_file.read_text(encoding="utf-8-sig"))

    report = analyse(scored["scores"], data["rows"])
    a_label, b_label = data["a_tier"], data["b_tier"]
    name = {"a": a_label, "b": b_label, "tie": "tie"}

    print(f"scores   {scores_file.name}  (by {scored['scored_by']})")
    print(f"judge    {results_file.name}  ({a_label} = A, {b_label} = B)")
    print(f"\n{report['scored']} pairs scored · {report['comparable']} comparable · "
          f"{report['not_a_verdict']} judge non-verdicts (inconsistent/unparsed)")

    print(f"\n{'':<10}{'picked ' + a_label:>16}{'picked ' + b_label:>16}{'tie':>8}")
    print(f"{'human':<10}{report['human_picks']['a']:>16}"
          f"{report['human_picks']['b']:>16}{report['human_picks']['tie']:>8}")
    print(f"{'judge':<10}{report['judge_picks']['a']:>16}"
          f"{report['judge_picks']['b']:>16}{report['judge_picks']['tie']:>8}")

    print(f"\nagreed on {report['agreed']} of {report['comparable']} "
          f"({report['raw_agreement']:.0%} raw)")
    if report["kappa"] is None:
        print(f"kappa: {report['kappa_note']}")
    else:
        print(f"kappa {report['kappa']:.2f} "
              f"(chance agreement would be {report['expected_by_chance']:.0%})")
    print(f"decisive pairs (someone picked a winner): {report['decisive_pairs']} "
          f"of {report['comparable']}")

    bias = report["human_order_bias"]
    print(f"human order bias: picked the first answer shown "
          f"{bias['picked_the_first_shown']} times, the second "
          f"{bias['picked_the_second_shown']}")

    print(f"\n{'task type':<24}{'n':>4}{'agreed':>8}{'raw':>8}{'kappa':>9}"
          f"   human {a_label}/{b_label}/tie")
    for task, row in report["per_task"].items():
        shown = "undefined" if row["kappa"] is None else f"{row['kappa']:.2f}"
        human = row["human"]
        print(f"{task:<24}{row['comparable']:>4}{row['agreed']:>8}"
              f"{row['raw_agreement']:>8.0%}{shown:>9}"
              f"   {human['a']}/{human['b']}/{human['tie']}")

    if report["disagreements"]:
        print(f"\nDISAGREEMENTS ({len(report['disagreements'])}):")
        for row in report["disagreements"]:
            print(f"  {row['pair_id']:<16} human {name[row['human']]:<7} "
                  f"judge {name[row['judge']]:<7} {row['note'][:60]}")
    else:
        print("\nNo disagreements on comparable pairs.")

    if report["judge_non_verdicts"]:
        print(f"\nJUDGE GAVE NO VERDICT ({len(report['judge_non_verdicts'])}):")
        for row in report["judge_non_verdicts"]:
            print(f"  {row['pair_id']:<16} judge {row['judge']:<13} "
                  f"human said {name[row['human']]}")

    out = RESULTS_DIR / f"{data['run_id']}-agreement.json"
    out.write_text(json.dumps({
        "run_id": data["run_id"],
        "measured_on": date.today().isoformat(),
        "scored_by": scored["scored_by"],
        "scores_file": scores_file.name,
        "results_file": results_file.name,
        "a_tier": a_label, "b_tier": b_label,
        "report": report,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nreport  {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())