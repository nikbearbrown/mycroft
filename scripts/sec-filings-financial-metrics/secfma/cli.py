"""Command-line entry point: ticker -> provenance-tagged metrics + report.

Usage (run from the package dir):
    python -m secfma.cli --ticker MSFT
    python -m secfma.cli --ticker AAPL --forms 10-K
    python -m secfma.cli --ticker MSFT --report        # also write a Markdown report
    python -m secfma.cli --ticker MSFT --validate       # also run validation checks
    python -m secfma.cli --sample --report              # offline run on the bundled fixture
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from . import config, metrics, report, validation
from .edgar_client import EdgarClient
from .extractor import extract_metrics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SEC Filings Financial Metrics Agent"
    )
    parser.add_argument("--ticker", help="Stock ticker, e.g. MSFT (defaults to SMPL in --sample mode)")
    parser.add_argument(
        "--sample", action="store_true",
        help="Offline mode: run against the bundled sample fixture, no network calls",
    )
    parser.add_argument(
        "--forms", nargs="+", default=list(config.DEFAULT_FORMS),
        help="Filing forms to include (default: 10-K 10-Q)",
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Run the rule-based validation checks",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Write a human-readable Markdown report (implies validation)",
    )
    args = parser.parse_args(argv)

    if args.ticker:
        ticker = args.ticker.upper()
    elif args.sample:
        ticker = "SMPL"  # the bundled offline fixture
    else:
        parser.error("--ticker is required (or use --sample for the bundled fixture)")

    client = EdgarClient(sample=args.sample)

    print(f"[1/4] Resolving CIK for {ticker} ...")
    cik10 = client.ticker_to_cik(ticker)
    print(f"      CIK{cik10}")

    source = "sample fixture" if args.sample else "cached in data/raw"
    print(f"[2/4] Loading companyfacts ({source}) ...")
    facts = client.company_facts(cik10)

    print("[3/4] Extracting canonical metrics with provenance ...")
    records = extract_metrics(facts, cik10, tuple(args.forms))
    ok = [r for r in records if r["status"] == "OK"]
    missing = [r for r in records if r["status"] == "MISSING"]
    custom = sorted({r["metric"] for r in ok if r.get("tag_source") == "custom-extension"})

    print("[4/4] Computing derived metrics ...")
    annual = metrics.build_annual(records)
    print(f"      {len(annual)} fiscal years of derived ratios")
    if custom:
        print(f"      resolved via custom-extension overrides: {', '.join(custom)}")

    out = {
        "ticker": ticker,
        "cik": cik10,
        "entity": facts.get("entityName"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "sample" if args.sample else "live",
        "forms": args.forms,
        "record_count": len(ok),
        "missing_metrics": [r["metric"] for r in missing],
        "custom_extension_metrics": custom,
        "derived_metrics": annual,
        "records": records,
    }

    val_report = None
    if args.validate or args.report:
        val_report = validation.run_all(records)
        out["validation"] = val_report
        fails = [r for r in val_report if r["result"] == "FAIL"]
        print(f"      validation: {len(val_report)} checks, {len(fails)} FAIL")

    out_path = config.VERIFIED_DIR / f"{ticker}_financial_metrics.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {len(ok)} metric-periods to {out_path}")

    if args.report:
        md = report.render(out, annual, val_report)
        report_path = config.VERIFIED_DIR / f"{ticker}_report.md"
        report_path.write_text(md)
        print(f"Wrote Markdown report to {report_path}")

    if missing:
        print(f"Missing metrics (no us-gaap tag or override): "
              f"{', '.join(r['metric'] for r in missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
