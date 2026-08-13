"""Score extraction accuracy and coverage against a hand-verified golden set.

The golden set (`projects/SEC-Filings-Financial-Metrics-Agent/benchmarks/golden_set.csv`)
holds values a human verified against the actual filing. This harness runs the
extractor for each ticker, matches annual base metrics by fiscal year, and reports:

  - coverage: fraction of golden rows where the metric was found at all
  - accuracy: fraction of *found* values within tolerance of the expected value

A MISSING row means the extractor produced no value for that (fiscal_year, metric)
— a coverage gap (e.g., an unmapped custom XBRL extension), never a silent zero.

Usage (from the package dir):
    python3 -m secfma.benchmark
    python3 -m secfma.benchmark --golden /path/to/golden.csv --report
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone

from . import config, metrics
from .edgar_client import EdgarClient
from .extractor import extract_metrics

DEFAULT_GOLDEN = (
    config.BASE_DIR / "projects" / "SEC-Filings-Financial-Metrics-Agent"
    / "benchmarks" / "golden_set.csv"
)
REL_TOLERANCE = 0.005  # 0.5% — tolerates rounding in recorded golden values


def _load_golden(path) -> list[dict]:
    rows = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            expected = (row.get("expected_value") or "").strip()
            if not expected:
                continue  # unfilled row — skip
            try:
                rows.append({
                    "ticker": row["ticker"].strip().upper(),
                    "fiscal_year": int(str(row["fiscal_year"]).strip()),
                    "metric": row["metric"].strip(),
                    "expected": float(expected),
                })
            except (ValueError, KeyError):
                continue
    return rows


def _annual_index(records) -> dict[int, dict[str, float]]:
    """{fiscal_year: {metric: value}} from the annual derived rows."""
    return {r["fiscal_year"]: r["base"] for r in metrics.build_annual(records)}


def score(golden_rows: list[dict]) -> list[dict]:
    client = EdgarClient()
    by_ticker: dict[str, list[dict]] = {}
    for r in golden_rows:
        by_ticker.setdefault(r["ticker"], []).append(r)

    results: list[dict] = []
    for ticker, rows in by_ticker.items():
        try:
            cik = client.ticker_to_cik(ticker)
            annual = _annual_index(extract_metrics(client.company_facts(cik), cik,
                                                   config.DEFAULT_FORMS))
        except Exception as exc:  # network / lookup failure — reported, not swallowed
            for row in rows:
                results.append({**_ref(row), "expected": row["expected"], "actual": None,
                                "rel_error": None, "status": "ERROR", "detail": str(exc)})
            continue
        for row in rows:
            actual = annual.get(row["fiscal_year"], {}).get(row["metric"])
            expected = row["expected"]
            if actual is None:
                results.append({**_ref(row), "expected": expected, "actual": None,
                                "rel_error": None, "status": "MISSING"})
            else:
                rel = abs(actual - expected) / abs(expected) if expected else None
                status = "MATCH" if (rel is not None and rel <= REL_TOLERANCE) else "MISMATCH"
                results.append({**_ref(row), "expected": expected, "actual": actual,
                                "rel_error": rel, "status": status})
    return results


def _ref(row: dict) -> dict:
    return {"ticker": row["ticker"], "fiscal_year": row["fiscal_year"], "metric": row["metric"]}


def summarize(results: list[dict]) -> dict:
    found = [r for r in results if r["status"] in ("MATCH", "MISMATCH")]
    matches = [r for r in results if r["status"] == "MATCH"]
    scorable = [r for r in results if r["status"] != "ERROR"]
    return {
        "golden_rows_scored": len(scorable),
        "coverage": (len(found) / len(scorable)) if scorable else None,
        "accuracy": (len(matches) / len(found)) if found else None,
        "match": len(matches),
        "mismatch": sum(1 for r in results if r["status"] == "MISMATCH"),
        "missing": sum(1 for r in results if r["status"] == "MISSING"),
        "errors": sum(1 for r in results if r["status"] == "ERROR"),
    }


def render_markdown(summary: dict, results: list[dict]) -> str:
    def pct(x): return "—" if x is None else f"{x * 100:.1f}%"
    def m(v): return "—" if v is None else f"{v / 1e6:,.0f}"
    def rel(v): return "—" if v is None else f"{v * 100:.3f}%"

    gen = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Extraction Accuracy Benchmark", "",
        f"**Generated:** {gen}  |  **Tolerance:** {REL_TOLERANCE:.1%} relative", "",
        f"- Rows scored: **{summary['golden_rows_scored']}**",
        f"- Coverage: **{pct(summary['coverage'])}** "
        f"({summary['match'] + summary['mismatch']} of {summary['golden_rows_scored']} found)",
        f"- Accuracy: **{pct(summary['accuracy'])}** "
        f"({summary['match']} match / {summary['mismatch']} mismatch)",
        f"- Missing: {summary['missing']}  |  Errors: {summary['errors']}", "",
        "| Ticker | FY | Metric | Expected ($M) | Actual ($M) | Rel err | Status |",
        "|---|---|---|--:|--:|--:|---|",
    ]
    for r in sorted(results, key=lambda x: (x["ticker"], x["fiscal_year"], x["metric"])):
        lines.append(
            f"| {r['ticker']} | {r['fiscal_year']} | {r['metric']} | "
            f"{m(r.get('expected'))} | {m(r.get('actual'))} | {rel(r.get('rel_error'))} | {r['status']} |"
        )
    lines += ["",
              "_Values in $ millions. Expand the golden set with independently hand-verified "
              "figures and at least one company that uses a custom XBRL extension._"]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark extraction accuracy vs a hand-verified golden set")
    parser.add_argument("--golden", default=str(DEFAULT_GOLDEN))
    parser.add_argument("--report", action="store_true", help="write a Markdown report")
    args = parser.parse_args(argv)

    golden = _load_golden(args.golden)
    if not golden:
        print(f"No filled golden rows in {args.golden} — add expected_value entries first.")
        return 0

    results = score(golden)
    summary = summarize(results)
    print("Benchmark summary:")
    print(json.dumps(summary, indent=2, default=str))

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tolerance": REL_TOLERANCE,
        "summary": summary,
        "results": results,
    }
    (config.VERIFIED_DIR / "benchmark_results.json").write_text(json.dumps(out, indent=2))
    if args.report:
        report_path = config.VERIFIED_DIR / "benchmark_report.md"
        report_path.write_text(render_markdown(summary, results))
        print(f"Wrote report to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
