#!/usr/bin/env python3
"""Purpose: Step 4 of recipes/scenariostresstestingagent.md: quality-check the stress-test results that step 5 produced for the
         requests step 3 accepted, before any report is written. Every figure is re-derived a second way (the workflow's own template
         shocks, written out again here with exact decimals, not by calling the step-5 engine) and the totals are reconciled; duplicates
         are looked for by id and by content; advisory flags are raised for a human to read.
Input: <verified>/validated.json (step 3) and <verified>/stress-results.json (step 5), default folder
       data/verified/scenariostresstestingagent/clean/ (sample mode: invented requests). The workflow's template shocks are read from
       the step-5 script (imported as data only; its engine is never called).
Output: <verified>/quality-check.json (verified_records, record_count, duplicates, rejects, flags, quality_notes, plus the checks run)
        and <verified>/quality-notes.md, a note for human judgment. It says what was found; it does not say pass.
Side effects: writes those two files. No network, no credentials, no clock.
Idempotent: Yes; same inputs give the same bytes.
Errors: exit 1 if any request was rejected at step 3, any result fails a reconciliation check, or a duplicate is found (the files are
        still written, so the reasons are kept). Exit 2, nothing written, if validated.json is missing or unparseable.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
PORT_PATH = REPO / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py"
SCHEMA = "1"
MONEY_TOL = Decimal("0.02")          # rounded to cents in two places, so a cent either way is rounding, not an error
PCT_TOL = Decimal("0.011")
WEIGHT_TOL = Decimal("0.0105")       # the workflow rescales only when the total is more than 0.01 from 1.0
CONCENTRATION = Decimal("0.5")       # advisory: one holding is a majority (strictly more than half) of the book
DEFAULT_SECTOR_SHARE = Decimal("0.5")  # advisory: at least half the book falls back to the default sector
NEAR_BOUNDARY = Decimal("0.05")      # advisory: drawdown within 0.05 points of a risk boundary


class Refuse(Exception):
    pass


def load_port():
    spec = importlib.util.spec_from_file_location("stress_port", PORT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def D(x) -> Decimal:
    return Decimal(str(x))


def expected_shock(ticker: str, shocks: dict, port) -> Decimal:
    """The workflow's rule for one holding, written out again: market, plus the ticker's sector (default tech_sector),
    plus ai_stocks and growth_stocks when the ticker is in those lists."""
    total = D(shocks.get("market", 0))
    total += D(shocks.get(port.SECTOR_MAP.get(ticker, "tech_sector"), 0))
    if ticker in port.AI_STOCKS:
        total += D(shocks.get("ai_stocks", 0))
    if ticker in port.GROWTH_STOCKS:
        total += D(shocks.get("growth_stocks", 0))
    return total


def expected_risk(drawdown_pct: Decimal, port) -> str:
    for name, bound in port.RISK_LEVELS:
        if abs(drawdown_pct) > bound:
            return name
    return "LOW"


def content_key(request: dict) -> str:
    """Duplicate by content: the same holdings (order does not matter) under the same scenario."""
    body = request.get("body", request)
    holds = sorted((str(h.get("ticker")), str(h.get("weight"))) for h in (body.get("portfolio", {}).get("holdings") or []) if isinstance(h, dict))
    key = {"holdings": holds, "scenario_type": body.get("scenario_type"), "custom": body.get("custom_scenario")}
    return hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:16]


def check_result(rid: str, request: dict, trace: dict, port) -> tuple[list[dict], list[dict]]:
    """returns (failures, flags) for one request that step 5 ran."""
    fails: list[dict] = []
    flags: list[dict] = []
    res = trace.get("result")
    body = request.get("body", request)
    holdings = body.get("portfolio", {}).get("holdings") or []

    def fail(check: str, detail: str):
        fails.append({"id": rid, "check": check, "detail": detail})

    def flag(kind: str, detail: str):
        flags.append({"id": rid, "flag": kind, "detail": detail})

    if res is None:                                   # the custom-scenario route stops at the Groq handoff
        flag("handoff", trace.get("handoff") or "custom scenario: needs the Groq call, not made")
        return fails, flags

    scenario_type = body.get("scenario_type")
    if not scenario_type:
        flag("scenario-defaulted", f"no scenario_type in the request; the workflow runs the default, {port.DEFAULT_TEMPLATE}")
    template = port.TEMPLATES.get(scenario_type or port.DEFAULT_TEMPLATE)
    if template is None:
        fail("template-known", f"scenario_type {scenario_type!r} is not a template")
        return fails, flags
    if res["scenario_name"] != template["name"]:
        fail("scenario-name", f"result says {res['scenario_name']!r}, the template is {template['name']!r}")

    pos = res["all_positions"]
    initial = D(port.INITIAL_VALUE)
    weight_sum = sum((D(p["weight"]) for p in pos), Decimal(0))
    if abs(weight_sum - 1) > WEIGHT_TOL:
        fail("weights-sum", f"weights in the result add to {weight_sum}, expected 1.0 within 0.01")

    sum_loss = Decimal(0)
    for p in pos:
        t = p["ticker"]
        want_shock = expected_shock(t, template["shocks"], port) * 100
        if abs(D(p["shock_pct"]) - want_shock) > PCT_TOL:
            fail("position-shock", f"{t}: shock_pct {p['shock_pct']}, re-derived {want_shock}")
        if abs(D(p["initial_value"]) - initial * D(p["weight"])) > MONEY_TOL:
            fail("position-initial", f"{t}: initial_value {p['initial_value']}, weight {p['weight']} of {initial}")
        want_loss = D(p["initial_value"]) * D(p["shock_pct"]) / 100
        if abs(D(p["loss"]) - want_loss) > MONEY_TOL:
            fail("position-loss", f"{t}: loss {p['loss']}, initial_value x shock = {want_loss.quantize(Decimal('0.01'))}")
        if abs(D(p["final_value"]) - (D(p["initial_value"]) + D(p["loss"]))) > MONEY_TOL:
            fail("position-final", f"{t}: final_value {p['final_value']} is not initial_value + loss")
        sum_loss += D(p["loss"])

    if abs(sum_loss - D(res["total_loss"])) > MONEY_TOL * max(1, len(pos)):
        fail("total-loss", f"positions' losses add to {sum_loss}, total_loss says {res['total_loss']}")
    if abs(D(res["final_portfolio_value"]) - (initial + D(res["total_loss"]))) > MONEY_TOL:
        fail("final-value", f"final_portfolio_value {res['final_portfolio_value']} is not {initial} + total_loss")
    want_dd = D(res["total_loss"]) / initial * 100
    if abs(D(res["drawdown_pct"]) - want_dd) > PCT_TOL:
        fail("drawdown", f"drawdown_pct {res['drawdown_pct']}, re-derived {want_dd.quantize(Decimal('0.01'))}")
    if res["risk_level"] != expected_risk(D(res["drawdown_pct"]), port):
        fail("risk-level", f"risk_level {res['risk_level']}, re-derived {expected_risk(D(res['drawdown_pct']), port)} from drawdown {res['drawdown_pct']}")
    losses = [D(p["loss"]) for p in pos]
    if losses != sorted(losses):
        fail("positions-order", "positions are not sorted from the biggest loss up")
    if res["top_losers"] != pos[:3]:
        fail("top-losers", "top_losers is not the first three positions")

    # advisory flags, for a human to read; none of these is a failure
    raw_total = sum((D(h.get("weight") or 0) for h in holdings if isinstance(h, dict)), Decimal(0))
    if abs(raw_total - 1) > Decimal("0.01"):
        flag("rescaled", f"the request's weights add to {raw_total}; the workflow rescaled them to 1.0")
    top = max(pos, key=lambda p: D(p["weight"]))
    if D(top["weight"]) > CONCENTRATION:
        flag("majority-holding", f"{top['ticker']} is {D(top['weight']) * 100:.1f}% of the book after rescaling, more than half")
    default_share = sum((D(p["weight"]) for p in pos if p["ticker"] not in port.SECTOR_MAP), Decimal(0))
    if default_share >= DEFAULT_SECTOR_SHARE:
        flag("default-sector", f"{default_share * 100:.0f}% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock")
    dd = abs(D(res["drawdown_pct"]))
    for name, bound in port.RISK_LEVELS:
        if abs(dd - bound) <= NEAR_BOUNDARY:
            flag("on-threshold", f"drawdown {res['drawdown_pct']}% sits within 0.05 points of the {bound}% line; the rule is 'above', so the level is {res['risk_level']}")
            break
    return fails, flags


def build(verified: Path) -> dict:
    port = load_port()
    vpath = verified / "validated.json"
    try:
        validated = json.loads(vpath.read_text())
    except (OSError, ValueError) as e:
        raise Refuse(f"{vpath}: cannot read ({e})") from e
    spath = verified / "stress-results.json"
    traces = {}
    if spath.exists():
        traces = {t["id"]: t for t in json.loads(spath.read_text())["results"]}

    accepted = validated["accepted"]
    ids = [a["id"] for a in accepted]
    duplicates: list[dict] = []
    seen_id: dict[str, int] = {}
    for i in ids:
        seen_id[i] = seen_id.get(i, 0) + 1
    for i, n in seen_id.items():
        if n > 1:
            duplicates.append({"kind": "id", "ids": [i], "detail": f"id {i!r} appears {n} times among the accepted requests"})
    by_content: dict[str, list[str]] = {}
    for a in accepted:
        by_content.setdefault(content_key(a["request"]), []).append(a["id"])
    for k, group in by_content.items():
        if len(group) > 1:
            duplicates.append({"kind": "content", "ids": group, "detail": "same holdings and scenario under different ids"})

    failures: list[dict] = []
    flags: list[dict] = []
    verified_records: list[str] = []
    handed_off: list[str] = []
    for a in accepted:
        rid = a["id"]
        trace = traces.get(rid)
        if trace is None:
            failures.append({"id": rid, "check": "ran", "detail": "accepted at step 3 but step 5 has no result for it"})
            continue
        f, g = check_result(rid, a["request"], trace, port)
        failures += f
        flags += g
        if trace.get("result") is None and not f:
            handed_off.append(rid)                    # nothing to reconcile: it stops at the Groq handoff
        elif not f:
            verified_records.append(rid)
    for tid in traces:
        if tid not in ids:
            failures.append({"id": tid, "check": "was-accepted", "detail": "step 5 has a result for a request step 3 did not accept"})

    rejects = [{"id": r["id"], "stage": "step 3 (validate data shape)", "reasons": r.get("reasons") or r.get("reason") or []} for r in validated["rejected"]]
    rejects += [{"id": f["id"], "stage": f"step 4 ({f['check']})", "reasons": [f["detail"]]} for f in failures]
    checks_run = ["weights-sum", "position-shock", "position-initial", "position-loss", "position-final", "total-loss", "final-value", "drawdown",
                  "risk-level", "positions-order", "top-losers", "scenario-name", "duplicate-id", "duplicate-content"]
    notes = [
        f"{len(accepted)} request(s) came in from step 3 and {len(validated['rejected'])} were rejected there; {len(traces)} have a step-5 result "
        f"({sum(1 for t in traces.values() if t.get('result') is None)} stopped at a handoff).",
        f"{len(verified_records)} result(s) reconciled on every check and {len(handed_off)} stopped at a handoff with nothing to reconcile; "
        f"{len(failures)} failure(s); {len(duplicates)} duplicate group(s); {len(flags)} advisory flag(s).",
        "Every figure was re-derived from the workflow's own template shocks (sector map, ai_stocks, growth_stocks) with exact decimals; the step-5 engine was not called.",
        "Flags are for a human to read. They are not failures, and the checks do not judge whether the template shocks or risk thresholds are sound.",
    ]
    return {"step": "transform-quality-check", "mode": validated.get("mode", "sample"), "schema_version": SCHEMA, "source_folder": verified.name,
            "verified_records": verified_records, "handed_off": handed_off, "record_count": len(accepted), "duplicates": duplicates, "rejects": rejects, "flags": flags,
            "quality_notes": notes, "checks_run": checks_run, "failures": failures}


def notes_md(doc: dict) -> str:
    L = [f"# Transform and quality check: scenariostresstestingagent, `{doc['source_folder']}`", "",
         "Written by `scripts/gigo/scenariostresstestingagent-transform-quality-check.py`. This note says what was found; it does not say pass.", ""]
    L += [f"- {n}" for n in doc["quality_notes"]]
    L += ["", "## Verified records", ""]
    L += [f"- `{r}`" for r in doc["verified_records"]] or ["- none"]
    L += ["", "## Stopped at a handoff (no result to reconcile)", ""]
    L += [f"- `{r}`" for r in doc["handed_off"]] or ["- none"]
    L += ["", "## Failures", ""]
    L += [f"- `{f['id']}` ({f['check']}): {f['detail']}" for f in doc["failures"]] or ["- none"]
    L += ["", "## Duplicates", ""]
    L += [f"- {d['kind']}: {', '.join('`' + i + '`' for i in d['ids'])}: {d['detail']}" for d in doc["duplicates"]] or ["- none"]
    L += ["", "## Rejected before this step or at it", ""]
    for r in doc["rejects"]:
        reasons = r["reasons"] if isinstance(r["reasons"], list) else [r["reasons"]]
        L.append(f"- `{r['id']}` at {r['stage']}: " + "; ".join(str(x) for x in reasons))
    if not doc["rejects"]:
        L.append("- none")
    L += ["", "## Flags for a human", ""]
    L += [f"- `{f['id']}` **{f['flag']}**: {f['detail']}" for f in doc["flags"]] or ["- none"]
    L += ["", "## Checks run on every result", "", ", ".join(f"`{c}`" for c in doc["checks_run"]), ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verified-dir", default=str(REPO / f"data/verified/{SLUG}/clean"))
    args = ap.parse_args()
    verified = Path(args.verified_dir)
    try:
        doc = build(verified)
    except Refuse as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    (verified / "quality-check.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    (verified / "quality-notes.md").write_text(notes_md(doc))
    try:
        shown = (verified / "quality-check.json").resolve().relative_to(REPO)
    except ValueError:
        shown = verified / "quality-check.json"
    print(f"quality-check {verified.name}: {doc['record_count']} accepted, {len(doc['verified_records'])} reconciled, {len(doc['handed_off'])} handed off, "
          f"{len(doc['failures'])} failures, {len(doc['duplicates'])} duplicates, {len(doc['rejects'])} rejects, {len(doc['flags'])} flags -> {shown}")
    return 1 if (doc["failures"] or doc["duplicates"] or doc["rejects"]) else 0


if __name__ == "__main__":
    sys.exit(main())
