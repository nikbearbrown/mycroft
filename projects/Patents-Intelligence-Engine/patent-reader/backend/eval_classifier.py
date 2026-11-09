"""
eval_classifier.py — evaluation harness for claim_classifier.py.

Runs the scope classifier over a hand-labeled set of independent claims
and measures agreement with the human labels, so prompt changes can be
judged by numbers instead of by reading a handful of outputs.

Why this exists: across the claims we've classified so far, the readings
lean heavily toward "narrow" / "defensive". That could be true of the
patents we happened to pick, or it could be the prompt collapsing onto
one answer. A majority-class baseline and the predicted-vs-gold label
distribution separate those two explanations; raw accuracy alone can't.

Input: a CSV of labeled claims (see eval/labeled_claims.template.csv):
    publication_number, claim_number, gold_breadth, gold_posture,
    label_notes, claim_text
Rows with a blank gold_breadth or gold_posture are counted as unlabeled
and skipped. claim_text is required in the CSV so this script never
queries BigQuery — pulling claims is a separate, already-paid step.

Cost safety: without --yes the script only prints the run plan and an
upper-bound cost estimate, then exits. Nothing is sent to the API.
--mock runs the whole pipeline offline with a fake predictor.

Predictions are cached per run in eval/runs/<run>.jsonl, keyed by
(publication, claim, prompt hash), so an interrupted run resumes without
paying twice for claims it already classified.

Usage:
    python eval_classifier.py eval/labeled_claims.csv --run baseline          # estimate only
    python eval_classifier.py eval/labeled_claims.csv --run baseline --yes    # real run
    python eval_classifier.py eval/labeled_claims.csv --run v2 --prompt-file eval/prompt_v2.txt --yes
    python eval_classifier.py eval/labeled_claims.csv --run mock --mock constant
    python eval_classifier.py eval/labeled_claims.csv --compare baseline v2
"""
import argparse
import csv
import hashlib
import inspect
import json
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

import claim_classifier
from claim_classifier import ScopeClassification

BREADTH_LABELS = ["broad", "narrow"]
POSTURE_LABELS = ["defensive", "offensive", "exploratory"]

# Per-token prices in USD per 1M tokens (Anthropic first-party API,
# cached 2026-10-06). Update if claim_classifier.py switches models.
PRICING = {
    "claude-sonnet-5": {"input": 2.00, "output": 10.00},
}

# A predicted label is flagged as a collapse when it takes at least this
# share of predictions AND exceeds its share in the gold labels by at
# least COLLAPSE_GAP. Both thresholds are judgment calls, not standards.
COLLAPSE_SHARE = 0.80
COLLAPSE_GAP = 0.20

RUNS_DIR = Path(__file__).parent / "eval" / "runs"


@dataclass
class LabeledClaim:
    publication_number: str
    claim_number: int
    gold_breadth: str
    gold_posture: str
    label_notes: str
    claim_text: str

    @property
    def key(self) -> str:
        return f"{self.publication_number}#{self.claim_number}"


@dataclass
class Prediction:
    key: str
    publication_number: str
    claim_number: int
    prompt_sha: str
    breadth: str
    posture: str
    reasoning: str
    confidence_caveat: str
    error: str = ""


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_labels(path: Path) -> (List[LabeledClaim], List[str]):
    """Returns (labeled claims, problems). Problems are printed, not fatal,
    except for duplicate keys and invalid label values."""
    labeled, problems, seen = [], [], set()
    unlabeled = 0

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"publication_number", "claim_number", "gold_breadth",
                    "gold_posture", "claim_text"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"{path}: missing columns {sorted(missing)}")

        for line_no, row in enumerate(reader, start=2):
            breadth = row["gold_breadth"].strip().lower()
            posture = row["gold_posture"].strip().lower()
            if not breadth or not posture:
                unlabeled += 1
                continue

            if breadth not in BREADTH_LABELS:
                sys.exit(f"{path}:{line_no}: gold_breadth {breadth!r} not in {BREADTH_LABELS}")
            if posture not in POSTURE_LABELS:
                sys.exit(f"{path}:{line_no}: gold_posture {posture!r} not in {POSTURE_LABELS}")
            if not row["claim_text"].strip():
                sys.exit(f"{path}:{line_no}: claim_text is empty")

            claim = LabeledClaim(
                publication_number=row["publication_number"].strip(),
                claim_number=int(row["claim_number"]),
                gold_breadth=breadth,
                gold_posture=posture,
                label_notes=(row.get("label_notes") or "").strip(),
                claim_text=row["claim_text"].strip(),
            )
            if claim.key in seen:
                sys.exit(f"{path}:{line_no}: duplicate claim {claim.key}")
            seen.add(claim.key)
            labeled.append(claim)

    if unlabeled:
        problems.append(f"{unlabeled} row(s) have no gold label yet and were skipped")
    return labeled, problems


def load_run(run: str) -> Dict[str, Prediction]:
    path = RUNS_DIR / f"{run}.jsonl"
    if not path.exists():
        return {}
    preds = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            p = Prediction(**json.loads(line))
            preds[p.key] = p
    return preds


# ---------------------------------------------------------------------------
# Prompt + cost
# ---------------------------------------------------------------------------

def active_prompt(prompt_file: Optional[Path]) -> str:
    if prompt_file is None:
        return claim_classifier.CLASSIFICATION_PROMPT
    text = prompt_file.read_text(encoding="utf-8")
    if "{claim_text}" not in text:
        sys.exit(f"{prompt_file}: prompt must contain the {{claim_text}} placeholder")
    return text


def classifier_settings() -> (str, int):
    """Reads model and max_tokens out of classify_claim's source so the
    cost estimate can't silently drift from what actually gets called."""
    src = inspect.getsource(claim_classifier.classify_claim)
    model = re.search(r'model="([^"]+)"', src)
    max_tokens = re.search(r"max_tokens=(\d+)", src)
    if not model or not max_tokens:
        sys.exit("Could not read model/max_tokens from classify_claim — update classifier_settings()")
    return model.group(1), int(max_tokens.group(1))


def estimate_cost(claims: List[LabeledClaim], prompt: str) -> dict:
    """Upper-bound estimate. Input tokens use ~4 chars/token (a rough
    heuristic for English; patent text may run a little higher). Output
    assumes every call uses its full max_tokens, which real calls won't."""
    model, max_tokens = classifier_settings()
    if model not in PRICING:
        sys.exit(f"No pricing for {model!r} — add it to PRICING before running")
    price = PRICING[model]

    input_tokens = sum(len(prompt.format(claim_text=c.claim_text)) // 4 + 10 for c in claims)
    output_tokens = max_tokens * len(claims)
    cost = input_tokens / 1e6 * price["input"] + output_tokens / 1e6 * price["output"]
    return {
        "model": model,
        "calls": len(claims),
        "input_tokens_est": input_tokens,
        "output_tokens_max": output_tokens,
        "cost_usd_upper_bound": round(cost, 4),
    }


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def mock_predict(claim: LabeledClaim, mode: str, rng: random.Random) -> ScopeClassification:
    if mode == "constant":
        # Reproduces the suspected failure mode, so the collapse check
        # has something to fire on in an offline test.
        breadth, posture = "narrow", "defensive"
    elif mode == "oracle":
        breadth, posture = claim.gold_breadth, claim.gold_posture
    else:  # random
        breadth, posture = rng.choice(BREADTH_LABELS), rng.choice(POSTURE_LABELS)
    return ScopeClassification(claim.claim_number, breadth, posture,
                               f"mock:{mode}", f"mock:{mode}")


def run_classifier(claims: List[LabeledClaim], run: str, prompt: str,
                   mock: Optional[str]) -> Dict[str, Prediction]:
    prompt_sha = hashlib.sha256(prompt.encode()).hexdigest()[:12]
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{run}.jsonl"

    existing = load_run(run)
    stale = [p for p in existing.values() if p.prompt_sha != prompt_sha]
    if stale:
        sys.exit(f"Run {run!r} already has predictions from a different prompt "
                 f"(sha {stale[0].prompt_sha}, now {prompt_sha}). Use a new --run name.")

    todo = [c for c in claims if c.key not in existing or existing[c.key].error]
    if existing:
        print(f"Resuming {run!r}: {len(claims) - len(todo)} cached, {len(todo)} to classify")

    claim_classifier.CLASSIFICATION_PROMPT = prompt
    rng = random.Random(0)

    with path.open("a", encoding="utf-8") as out:
        for i, claim in enumerate(todo, start=1):
            print(f"  [{i}/{len(todo)}] {claim.key}", flush=True)
            try:
                if mock:
                    result = mock_predict(claim, mock, rng)
                else:
                    result = claim_classifier.classify_claim(claim.claim_number, claim.claim_text)
                pred = Prediction(claim.key, claim.publication_number, claim.claim_number,
                                  prompt_sha, result.breadth, result.posture,
                                  result.reasoning, result.confidence_caveat)
            except Exception as e:  # keep going; errors are reported and retried on resume
                pred = Prediction(claim.key, claim.publication_number, claim.claim_number,
                                  prompt_sha, "error", "error", "", "", error=f"{type(e).__name__}: {e}")
                print(f"      error: {pred.error}")
            existing[claim.key] = pred
            out.write(json.dumps(asdict(pred)) + "\n")
            out.flush()

    return existing


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def cohens_kappa(gold: List[str], pred: List[str]) -> Optional[float]:
    n = len(gold)
    if n == 0:
        return None
    observed = sum(g == p for g, p in zip(gold, pred)) / n
    g_counts, p_counts = Counter(gold), Counter(pred)
    expected = sum(g_counts[l] * p_counts[l] for l in set(gold) | set(pred)) / (n * n)
    if expected == 1:
        return None
    return (observed - expected) / (1 - expected)


def dimension_metrics(gold: List[str], pred: List[str], labels: List[str]) -> dict:
    n = len(gold)
    pred_labels = labels + sorted(set(pred) - set(labels))  # surfaces "unclear"/"error"
    confusion = {g: {p: 0 for p in pred_labels} for g in labels}
    for g, p in zip(gold, pred):
        confusion[g][p] += 1

    per_class = {}
    for l in labels:
        tp = confusion[l][l]
        predicted = sum(confusion[g][l] for g in labels)
        actual = sum(confusion[l].values())
        per_class[l] = {
            "precision": tp / predicted if predicted else None,
            "recall": tp / actual if actual else None,
        }

    g_counts, p_counts = Counter(gold), Counter(pred)
    majority_label, majority_n = g_counts.most_common(1)[0]

    collapses = []
    for l, c in p_counts.items():
        share, gold_share = c / n, g_counts[l] / n
        if share >= COLLAPSE_SHARE and share - gold_share >= COLLAPSE_GAP:
            collapses.append(f"'{l}' is {share:.0%} of predictions but {gold_share:.0%} of gold labels")

    return {
        "accuracy": sum(g == p for g, p in zip(gold, pred)) / n,
        "kappa": cohens_kappa(gold, pred),
        "majority_baseline": {"label": majority_label, "accuracy": majority_n / n},
        "gold_distribution": {l: g_counts[l] for l in labels},
        "pred_distribution": {l: p_counts[l] for l in pred_labels},
        "confusion": confusion,
        "per_class": per_class,
        "collapses": collapses,
    }


def compute_metrics(claims: List[LabeledClaim], preds: Dict[str, Prediction]) -> dict:
    scored = [(c, preds[c.key]) for c in claims if c.key in preds and not preds[c.key].error]
    errors = [preds[c.key] for c in claims if c.key in preds and preds[c.key].error]
    missing = [c.key for c in claims if c.key not in preds]
    if not scored:
        return {"n": 0, "errors": errors, "missing": missing}

    gold_b = [c.gold_breadth for c, _ in scored]
    pred_b = [p.breadth for _, p in scored]
    gold_p = [c.gold_posture for c, _ in scored]
    pred_p = [p.posture for _, p in scored]

    pair_gold = Counter(f"{c.gold_breadth}/{c.gold_posture}" for c, _ in scored)
    pair_pred = Counter(f"{p.breadth}/{p.posture}" for _, p in scored)

    per_patent = defaultdict(lambda: {"n": 0, "breadth_ok": 0, "posture_ok": 0})
    for c, p in scored:
        row = per_patent[c.publication_number]
        row["n"] += 1
        row["breadth_ok"] += c.gold_breadth == p.breadth
        row["posture_ok"] += c.gold_posture == p.posture

    disagreements = [
        {"key": c.key, "gold": f"{c.gold_breadth}/{c.gold_posture}",
         "pred": f"{p.breadth}/{p.posture}", "reasoning": p.reasoning,
         "label_notes": c.label_notes}
        for c, p in scored
        if (c.gold_breadth, c.gold_posture) != (p.breadth, p.posture)
    ]

    return {
        "n": len(scored),
        "errors": errors,
        "missing": missing,
        "breadth": dimension_metrics(gold_b, pred_b, BREADTH_LABELS),
        "posture": dimension_metrics(gold_p, pred_p, POSTURE_LABELS),
        "joint_accuracy": sum(
            c.gold_breadth == p.breadth and c.gold_posture == p.posture for c, p in scored
        ) / len(scored),
        "pair_gold": dict(pair_gold),
        "pair_pred": dict(pair_pred),
        "per_patent": dict(per_patent),
        "disagreements": disagreements,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def fmt(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x:.2f}"


def render_report(run: str, m: dict) -> str:
    lines = [f"# Classifier eval — run `{run}`", ""]
    if m["n"] == 0:
        lines.append("No scored predictions.")
        return "\n".join(lines)

    lines += [f"Scored claims: **{m['n']}**  ·  errors: {len(m['errors'])}  ·  "
              f"not yet run: {len(m['missing'])}", ""]

    lines += ["## Headline", "",
              "| Dimension | Accuracy | Cohen's κ | Majority baseline |",
              "|---|---|---|---|"]
    for dim in ("breadth", "posture"):
        d = m[dim]
        base = d["majority_baseline"]
        lines.append(f"| {dim} | {d['accuracy']:.2f} | {fmt(d['kappa'])} | "
                     f"{base['accuracy']:.2f} (always '{base['label']}') |")
    lines += [f"| joint | {m['joint_accuracy']:.2f} | | |", ""]

    all_collapses = [f"{dim}: {c}" for dim in ("breadth", "posture") for c in m[dim]["collapses"]]
    lines += ["## Collapse check", ""]
    if all_collapses:
        lines += [f"- ⚠ {c}" for c in all_collapses]
    else:
        lines.append(f"No single label exceeds {COLLAPSE_SHARE:.0%} of predictions "
                     f"while beating its gold share by {COLLAPSE_GAP:.0%}+.")
    lines += ["", "| Breadth/posture pair | Gold | Predicted |", "|---|---|---|"]
    for pair in sorted(set(m["pair_gold"]) | set(m["pair_pred"])):
        lines.append(f"| {pair} | {m['pair_gold'].get(pair, 0)} | {m['pair_pred'].get(pair, 0)} |")
    lines.append("")

    for dim, labels in (("breadth", BREADTH_LABELS), ("posture", POSTURE_LABELS)):
        d = m[dim]
        cols = list(next(iter(d["confusion"].values())).keys())
        lines += [f"## {dim.capitalize()} confusion (rows = gold, cols = predicted)", "",
                  "| gold \\ pred | " + " | ".join(cols) + " | recall |",
                  "|---|" + "---|" * (len(cols) + 1)]
        for g in labels:
            row = d["confusion"][g]
            lines.append(f"| {g} | " + " | ".join(str(row[c]) for c in cols) +
                         f" | {fmt(d['per_class'][g]['recall'])} |")
        lines.append("| precision | " + " | ".join(
            fmt(d["per_class"][c]["precision"]) if c in labels else "" for c in cols) + " | |")
        lines.append("")

    lines += ["## Per patent", "", "| Patent | n | breadth acc | posture acc |", "|---|---|---|---|"]
    for pub, r in sorted(m["per_patent"].items()):
        lines.append(f"| {pub} | {r['n']} | {r['breadth_ok'] / r['n']:.2f} | {r['posture_ok'] / r['n']:.2f} |")
    lines.append("")

    lines += [f"## Disagreements ({len(m['disagreements'])})", ""]
    for d in m["disagreements"]:
        lines.append(f"- **{d['key']}** — gold `{d['gold']}`, predicted `{d['pred']}`")
        if d["reasoning"]:
            lines.append(f"  - model: {d['reasoning']}")
        if d["label_notes"]:
            lines.append(f"  - labeler: {d['label_notes']}")
    lines.append("")

    if m["errors"]:
        lines += ["## Errors (retried automatically on the next run)", ""]
        lines += [f"- {e.key}: {e.error}" for e in m["errors"]]
        lines.append("")

    return "\n".join(lines)


def render_compare(a: str, b: str, claims: List[LabeledClaim]) -> str:
    pa, pb = load_run(a), load_run(b)
    if not pa or not pb:
        sys.exit(f"Both runs must exist in {RUNS_DIR} (found {a}: {len(pa)}, {b}: {len(pb)})")
    shared = [c for c in claims if c.key in pa and c.key in pb
              and not pa[c.key].error and not pb[c.key].error]
    ma = compute_metrics(shared, pa)
    mb = compute_metrics(shared, pb)

    lines = [f"# Compare `{a}` → `{b}` on {len(shared)} shared claims", "",
             "| Metric | " + a + " | " + b + " | Δ |", "|---|---|---|---|"]
    for dim in ("breadth", "posture"):
        for key in ("accuracy", "kappa"):
            va, vb = ma[dim][key], mb[dim][key]
            delta = "n/a" if va is None or vb is None else f"{vb - va:+.2f}"
            lines.append(f"| {dim} {key} | {fmt(va)} | {fmt(vb)} | {delta} |")
    lines.append(f"| joint accuracy | {ma['joint_accuracy']:.2f} | {mb['joint_accuracy']:.2f} | "
                 f"{mb['joint_accuracy'] - ma['joint_accuracy']:+.2f} |")
    lines.append("")

    fixed, broke = [], []
    for c in shared:
        gold = (c.gold_breadth, c.gold_posture)
        ok_a = (pa[c.key].breadth, pa[c.key].posture) == gold
        ok_b = (pb[c.key].breadth, pb[c.key].posture) == gold
        if ok_b and not ok_a:
            fixed.append(c.key)
        elif ok_a and not ok_b:
            broke.append(c.key)
    lines += [f"Fixed by `{b}` ({len(fixed)}): {', '.join(fixed) or '—'}", "",
              f"Broken by `{b}` ({len(broke)}): {', '.join(broke) or '—'}", ""]
    if len(shared) < 30:
        lines.append(f"Note: with {len(shared)} claims, one claim moves accuracy by "
                     f"{1 / len(shared):.0%}. Treat small deltas as noise.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("labels", type=Path, help="CSV of hand-labeled claims")
    ap.add_argument("--run", help="name for this run's cached predictions")
    ap.add_argument("--prompt-file", type=Path, help="override CLASSIFICATION_PROMPT (must contain {claim_text})")
    ap.add_argument("--yes", action="store_true", help="actually call the Claude API (costs money)")
    ap.add_argument("--mock", choices=["constant", "oracle", "random"], help="offline fake predictor, no API calls")
    ap.add_argument("--limit", type=int, help="only use the first N labeled claims")
    ap.add_argument("--compare", nargs=2, metavar=("RUN_A", "RUN_B"), help="compare two existing runs")
    args = ap.parse_args()

    claims, problems = load_labels(args.labels)
    for p in problems:
        print(f"note: {p}")
    if args.limit:
        claims = claims[:args.limit]
    print(f"{len(claims)} labeled claim(s) across "
          f"{len({c.publication_number for c in claims})} patent(s)\n")

    if args.compare:
        print(render_compare(*args.compare, claims))
        return

    if not args.run:
        ap.error("--run is required unless using --compare")

    prompt = active_prompt(args.prompt_file)

    if not args.mock:
        cached = load_run(args.run)
        todo = [c for c in claims if c.key not in cached or cached[c.key].error]
        est = estimate_cost(todo, prompt)
        print("Run plan (nothing has been sent yet):")
        for k, v in est.items():
            print(f"  {k}: {v}")
        if not args.yes:
            print("\nEstimate only. Re-run with --yes to call the API.")
            return
        if todo:
            from dotenv import load_dotenv
            load_dotenv()
        print()

    preds = run_classifier(claims, args.run, prompt, args.mock)
    metrics = compute_metrics(claims, preds)
    report = render_report(args.run, metrics)

    report_path = RUNS_DIR / f"{args.run}_report.md"
    report_path.write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
