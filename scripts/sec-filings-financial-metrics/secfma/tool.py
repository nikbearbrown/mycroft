"""Agent-callable tool: verified financials for one company and fiscal year.

This is the interface other Mycroft agents use instead of asking a language
model for a financial figure. It wraps the deterministic pipeline
(resolve -> fetch -> extract -> derive -> validate) behind one function and
one JSON tool definition.

Contract a calling agent can rely on:
  * Deterministic: the same inputs and the same cached SEC data give the same
    output. There is no language model anywhere in this path.
  * Never guesses: a metric with no reliable source comes back with status
    MISSING, value null and a reason. Never 0, never interpolated.
  * Provenance on every value: the XBRL tag it came from, how the tag was
    resolved (us-gaap, custom-extension or derived), and the filing's
    accession number, form, filed date and EDGAR link.
  * Validation travels with the numbers: PASS / FAIL / UNKNOWN checks for the
    same period, so the agent can see whether the figures hang together.
  * Expected failures (unknown ticker, no data for a year, bad arguments,
    network errors) come back as {"ok": false, "error": {...}} instead of
    raising, so an agent loop can read them and decide what to do next.

Usage:
    from secfma.tool import get_verified_financials, run_tool, TOOL_SPEC
    get_verified_financials("MSFT", fiscal_year=2024, metrics=["revenue"])
    run_tool({"ticker": "MSFT", "fiscal_year": 2024})   # raw tool-call arguments

    python -m secfma.tool --ticker MSFT --year 2024
    python -m secfma.tool --sample                      # offline, bundled fixture
    python -m secfma.tool --spec                        # print the tool definition
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional

from . import config, validation
from . import metrics as metrics_mod
from .concept_map import CANONICAL_METRICS
from .edgar_client import EdgarClient
from .extractor import extract_metrics

TOOL_NAME = "get_verified_financials"
TOOL_VERSION = "0.1.0"
BASE_METRICS: tuple[str, ...] = tuple(m.name for m in CANONICAL_METRICS)

TOOL_SPEC: dict[str, Any] = {
    "name": TOOL_NAME,
    "description": (
        "Return SEC-reported financial metrics for one company and fiscal year, "
        "extracted deterministically from EDGAR XBRL filings, with provenance for "
        "every value and PASS/FAIL/UNKNOWN validation checks. Use this instead of "
        "estimating or recalling any financial figure. Metrics without a reliable "
        "source come back MISSING with a reason; they are never guessed."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "US stock ticker, e.g. MSFT.",
            },
            "fiscal_year": {
                "type": "integer",
                "description": (
                    "Fiscal year, labelled by the calendar year of the period-end "
                    "date. Omit for the latest available year."
                ),
            },
            "metrics": {
                "type": "array",
                "items": {"type": "string", "enum": list(BASE_METRICS)},
                "description": "Base metrics to return. Omit for all of them.",
            },
        },
        "required": ["ticker"],
        "additionalProperties": False,
    },
}

_CHECKS = (
    validation.check_accounting_identity,
    validation.check_margin_bounds,
    validation.check_sum_consistency,
    validation.check_current_ratio_sanity,
)


def as_openai_function() -> dict[str, Any]:
    """The same tool definition in the OpenAI function-calling shape."""
    return {
        "type": "function",
        "function": {
            "name": TOOL_SPEC["name"],
            "description": TOOL_SPEC["description"],
            "parameters": TOOL_SPEC["input_schema"],
        },
    }


def _error(kind: str, message: str, **extra: Any) -> dict[str, Any]:
    return {
        "ok": False,
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "error": {"type": kind, "message": message, **extra},
    }


def get_verified_financials(
    ticker: str,
    fiscal_year: Optional[int] = None,
    metrics: Optional[list[str]] = None,
    *,
    sample: bool = False,
    client: Optional[EdgarClient] = None,
) -> dict[str, Any]:
    """Verified base metrics, ratios and validation for one fiscal year."""
    if not isinstance(ticker, str) or not ticker.strip():
        return _error("invalid_argument", "ticker must be a non-empty string.")
    if fiscal_year is not None and (isinstance(fiscal_year, bool) or not isinstance(fiscal_year, int)):
        return _error("invalid_argument", "fiscal_year must be an integer, or omitted.")
    ticker = ticker.strip().upper()

    wanted = list(BASE_METRICS) if not metrics else list(dict.fromkeys(metrics))
    unknown = [m for m in wanted if m not in BASE_METRICS]
    if unknown:
        return _error("unknown_metric", f"Unknown metric(s): {', '.join(unknown)}.",
                      valid_metrics=list(BASE_METRICS))

    client = client or EdgarClient(sample=sample)
    mode = "sample" if getattr(client, "sample", sample) else "live"

    try:
        cik = client.ticker_to_cik(ticker)
    except ValueError as exc:
        return _error("ticker_not_found", str(exc), ticker=ticker)
    try:
        facts = client.company_facts(cik)
    except FileNotFoundError as exc:
        return _error("no_sample_fixture", str(exc), ticker=ticker, cik=cik)
    except Exception as exc:  # network / HTTP failure: report it, never swallow it
        return _error("fetch_failed", f"Could not fetch SEC company facts: {exc}",
                      ticker=ticker, cik=cik)

    records = extract_metrics(facts, cik, config.DEFAULT_FORMS)
    annual = metrics_mod.build_annual(records)
    company = {"ticker": ticker, "cik": cik, "entity": facts.get("entityName")}
    if not annual:
        return _error("no_annual_data", "No full-year (10-K) data was found for this company.",
                      **company)

    years = sorted({r["fiscal_year"] for r in annual})
    if fiscal_year is None:
        row = annual[-1]
    else:
        matches = [r for r in annual if r["fiscal_year"] == fiscal_year]
        if not matches:
            return _error("fiscal_year_not_found", f"No annual data for fiscal year {fiscal_year}.",
                          available_years=years, **company)
        row = matches[-1]

    unresolved = {r["metric"]: r["note"] for r in records if r["status"] == "MISSING"}
    out_metrics: dict[str, dict[str, Any]] = {}
    for name in wanted:
        value = row["base"].get(name)
        if value is not None:
            prov = row["provenance"].get(name, {})
            out_metrics[name] = {
                "status": "OK",
                "value": value,
                "unit": "USD",
                "source_tag": prov.get("us_gaap_tag"),
                "tag_source": prov.get("tag_source"),
                "accession": prov.get("accession"),
                "form": prov.get("form"),
                "filed": prov.get("filed"),
                "source_url": prov.get("source_url"),
            }
        else:
            out_metrics[name] = {
                "status": "MISSING",
                "value": None,
                "unit": "USD",
                "reason": unresolved.get(name) or (
                    f"No full-year value for fiscal year {row['fiscal_year']} "
                    f"(period ending {row['period_end']})."
                ),
            }

    ratios = {
        name: ({"status": "OK", "value": value} if value is not None else
               {"status": "NOT_COMPUTABLE", "value": None,
                "reason": "An input is missing or zero for this period."})
        for name, value in row["ratios"].items()
    }

    # Period checks run on exactly the values returned above.
    period = {k: float(v) for k, v in row["base"].items() if v is not None}
    checks = []
    for check in _CHECKS:
        result, detail = check(period)
        checks.append({"check": check.__name__, "result": result, "detail": detail})
    checks += [c for c in validation.check_unit_consistency(records) if c.get("metric") in wanted]
    same_period = [r for r in records
                   if r.get("period_end") == row["period_end"] and r.get("metric") in wanted]
    checks += validation.check_restatements(same_period)
    summary = {k: sum(1 for c in checks if c["result"] == k) for k in ("PASS", "FAIL", "UNKNOWN")}

    return {
        "ok": True,
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "company": company,
        "fiscal_year": row["fiscal_year"],
        "period_end": row["period_end"],
        "available_years": years,
        "metrics": out_metrics,
        "ratios": ratios,
        "validation": {"summary": summary, "checks": checks},
        "method": {
            "deterministic": True,
            "llm_in_path": False,
            "source": "SEC EDGAR XBRL company facts",
            "mode": mode,
            "forms": list(config.DEFAULT_FORMS),
            "fiscal_year_rule": "calendar year of the period-end date",
        },
    }


def run_tool(arguments: Any, *, sample: bool = False,
             client: Optional[EdgarClient] = None) -> dict[str, Any]:
    """Entry point for a raw tool call: validate the arguments, then run."""
    if not isinstance(arguments, dict):
        return _error("invalid_argument", "Tool arguments must be a JSON object.")
    allowed = set(TOOL_SPEC["input_schema"]["properties"])
    extra = sorted(set(arguments) - allowed)
    if extra:
        return _error("invalid_argument", f"Unexpected argument(s): {', '.join(extra)}.",
                      allowed_arguments=sorted(allowed))
    if "ticker" not in arguments:
        return _error("invalid_argument", "Missing required argument: ticker.")
    metrics = arguments.get("metrics")
    if metrics is not None and (not isinstance(metrics, list)
                                or not all(isinstance(m, str) for m in metrics)):
        return _error("invalid_argument", "metrics must be a list of metric names.")
    return get_verified_financials(arguments["ticker"], arguments.get("fiscal_year"), metrics,
                                   sample=sample, client=client)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=f"{TOOL_NAME}: verified SEC financials as JSON")
    parser.add_argument("--ticker", help="Stock ticker, e.g. MSFT (defaults to SMPL with --sample)")
    parser.add_argument("--year", type=int, help="Fiscal year (default: latest available)")
    parser.add_argument("--metrics", nargs="+", help="Base metrics to return (default: all)")
    parser.add_argument("--sample", action="store_true", help="Offline: use the bundled fixture")
    parser.add_argument("--spec", action="store_true", help="Print the tool definition and exit")
    parser.add_argument("--openai-spec", action="store_true",
                        help="Print the tool definition in OpenAI function format and exit")
    args = parser.parse_args(argv)

    if args.spec or args.openai_spec:
        print(json.dumps(as_openai_function() if args.openai_spec else TOOL_SPEC, indent=2))
        return 0
    ticker = args.ticker or ("SMPL" if args.sample else None)
    if not ticker:
        parser.error("--ticker is required (or use --sample for the bundled fixture)")
    result = get_verified_financials(ticker, args.year, args.metrics, sample=args.sample)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
