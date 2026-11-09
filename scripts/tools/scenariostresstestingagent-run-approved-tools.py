"""Purpose: Step 5 of recipes/scenariostresstestingagent.md: run the workflow's deterministic stress-test chain on the
         sample requests, stopping where a live service would be called. It ports four of the workflow's five code nodes
         in the workflow's own order (Validate Portfolio, Load_Template_Scenario, Save_Portfolio_Before_LLM and
         Stress_Test_Engine) and models the set node (Edit Fields) and the IF node (Custom Scenario?) that join them.
         Parse_LLM_Response is not ported: it only runs after the Groq call, which is never made.
Input: a folder of request files (default data/raw/scenariostresstestingagent/sample/clean/). Each is the webhook payload,
       {"body": {portfolio, scenario_type, custom_scenario, horizon_days}}. Every request first goes through the step-3
       gate; a rejected request is refused and nothing is written.
Output: data/verified/scenariostresstestingagent/<folder>/stress-results.json (one result per request) and
        logs/scenariostresstestingagent-run-approved-tools-<YYYY-MM-DD>.json, the step-5 fields (tool_name, input_path,
        output_path, action_taken, approval_id, no_write_mode) plus the handoffs the run did not make.
Side effects: writes those two files unless --no-write. No network, no credentials, no model call.
Idempotent: Yes; same inputs give the same bytes except generated_at (pin it with --now).
Errors: exit 1, nothing written, if the step-3 gate rejects any request. Exit 2 if the sample folder is missing.
Handoffs recorded, never made (approved_for_live_action: false): the Alpha Vantage HTTP request (Fetch_Data), the Groq
        chat call (Basic LLM Chain and Groq Chat Model) for a custom scenario, and the Respond to Webhook reply.
Recipe: recipes/scenariostresstestingagent.md
JavaScript note: Validate Portfolio is JavaScript. The port copies `||` defaults, `Math.abs`, division by zero (NaN and
        Infinity, not an error) and the JSON boundary (NaN becomes null between nodes). It does NOT model JavaScript's
        string arithmetic: a non-number weight raises NotModelled, which the step-3 gate refuses first.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------- the workflow's own constants (copied, not judged)
TEMPLATES = {
    "tech_crash": {"name": "Tech Sector Crash", "description": "Major tech selloff triggered by regulatory concerns",
                   "shocks": {"market": -0.15, "tech_sector": -0.30, "ai_stocks": -0.40, "semiconductor": -0.35, "volatility_spike": 2.5}},
    "rate_hike": {"name": "Aggressive Rate Hike", "description": "Fed raises rates more than expected",
                  "shocks": {"market": -0.10, "growth_stocks": -0.20, "tech_sector": -0.15, "volatility_spike": 1.8}},
    "ai_regulation": {"name": "AI Regulation Announcement", "description": "Major new AI safety regulations announced",
                      "shocks": {"market": -0.05, "ai_stocks": -0.25, "big_tech": -0.15, "volatility_spike": 2.0}},
    "chip_shortage": {"name": "Semiconductor Supply Shock", "description": "Critical chip shortage impacting AI infrastructure",
                      "shocks": {"market": -0.08, "semiconductor": -0.30, "tech_sector": -0.20, "volatility_spike": 1.5}},
    "black_swan": {"name": "Black Swan Event", "description": "Extreme tail-risk event",
                   "shocks": {"market": -0.35, "all_sectors": -0.30, "volatility_spike": 4.0}},
}
DEFAULT_TEMPLATE = "tech_crash"
SECTOR_MAP = {"NVDA": "semiconductor", "AMD": "semiconductor", "INTC": "semiconductor", "TSM": "semiconductor",
              "GOOGL": "big_tech", "MSFT": "big_tech", "META": "big_tech", "AAPL": "big_tech", "AMZN": "big_tech",
              "TSLA": "tech_sector"}
AI_STOCKS = ["NVDA", "AMD", "GOOGL", "MSFT", "META", "TSLA"]
GROWTH_STOCKS = ["NVDA", "TSLA", "META", "AMD"]
INITIAL_VALUE = 10000
RISK_LEVELS = (("CRITICAL", 30), ("HIGH", 20), ("MODERATE", 10))   # 'above' each; otherwise LOW

HANDOFFS = [
    {"node": "Fetch_Data", "action": "HTTP GET https://www.alphavantage.co/query (TIME_SERIES_DAILY, symbol NVDA)",
     "approved_for_live_action": False, "live_call_performed": False,
     "note": "not made; in sample mode the merge after it carries only the Validate Portfolio item"},
    {"node": "Basic LLM Chain / Groq Chat Model", "action": "Groq chat completion that turns a custom scenario description into shocks",
     "approved_for_live_action": False, "live_call_performed": False,
     "note": "not made; a request with a custom_scenario stops here and is recorded as a handoff, with no stress result"},
    {"node": "Respond to Webhook", "action": "reply to the caller with {success: true, data: <engine output>}",
     "approved_for_live_action": False, "live_call_performed": False, "note": "not made; the engine output is written to a local file instead"},
]


class ValidationFailed(Exception):
    """The JavaScript node's own `throw new Error(...)`; the message is the workflow's, character for character."""


class JSTypeError(Exception):
    """A JavaScript TypeError raised by the node's code (for example iterating something that is not iterable)."""


class NotModelled(Exception):
    """JavaScript behaviour this port does not copy (string arithmetic, non-object holdings). The step-3 gate refuses these."""


# ---------------------------------------------------------------- JavaScript helpers
def js_truthy(v: Any) -> bool:
    if v is None or v is False:
        return False
    if isinstance(v, bool):
        return True
    if isinstance(v, (int, float)):
        return not (v == 0 or (isinstance(v, float) and math.isnan(v)))
    if isinstance(v, str):
        return v != ""
    return True   # objects and arrays are truthy, even when empty


def js_div(a: float, b: float) -> float:
    """JavaScript's a / b: division by zero is NaN (0/0) or +-Infinity, never an error."""
    if b == 0:
        if a == 0 or (isinstance(a, float) and math.isnan(a)):
            return math.nan
        return math.inf if (a > 0) == (math.copysign(1, b) > 0) else -math.inf
    return a / b


def to_json_boundary(x: Any) -> Any:
    """What JSON.stringify does between nodes: NaN and +-Infinity become null."""
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if isinstance(x, dict):
        return {k: to_json_boundary(v) for k, v in x.items()}
    if isinstance(x, list):
        return [to_json_boundary(v) for v in x]
    return x


def _weight_or_zero(h: dict) -> float:
    """`holding.weight || 0` for a number or a missing weight; anything else is JavaScript string arithmetic."""
    w = h.get("weight")
    if isinstance(w, bool) or (w is not None and not isinstance(w, (int, float))):
        raise NotModelled(f"weight {w!r} is not a number (JavaScript would concatenate or coerce)")
    return w if js_truthy(w) else 0


# ---------------------------------------------------------------- the set node: Edit Fields
def edit_fields(request: dict) -> dict:
    """Parse Input and Edit Fields: copy body.portfolio, body.scenario_type, body.custom_scenario and body.horizon_days
    onto the item (a missing field stays missing)."""
    body = request.get("body")
    if not isinstance(body, dict):
        raise ValidationFailed("Cannot read properties of undefined (reading 'portfolio')")
    return {k: body[k] for k in ("portfolio", "scenario_type", "custom_scenario", "horizon_days") if k in body}


# ---------------------------------------------------------------- code node 1 (JavaScript): Validate Portfolio
def validate_portfolio(item: dict) -> dict:
    portfolio = item.get("portfolio")
    if not js_truthy(portfolio) or not isinstance(portfolio, dict):
        # a truthy non-object (a string, a number, an array) has no .holdings either
        raise ValidationFailed("Portfolio must have holdings array")
    holdings = portfolio.get("holdings")
    if not js_truthy(holdings):
        raise ValidationFailed("Portfolio must have holdings array")
    if isinstance(holdings, str):
        raise NotModelled("holdings is a string (JavaScript would iterate its characters)")
    if not isinstance(holdings, list):
        raise JSTypeError("portfolio.holdings is not iterable")
    for h in holdings:
        if not isinstance(h, dict):
            raise NotModelled(f"holding {h!r} is not an object")
    total = 0
    for h in holdings:
        total += _weight_or_zero(h)
    if abs(total - 1.0) > 0.01:
        for h in holdings:
            w = h.get("weight")
            if "weight" not in h:
                h["weight"] = math.nan                     # undefined / total is NaN
            else:
                h["weight"] = js_div(0 if w is None else w, total)   # null coerces to 0
    for h in holdings:
        if not js_truthy(h.get("ticker")):
            raise ValidationFailed("Each holding must have a ticker")
    out = {"portfolio": portfolio}
    for k in ("scenario_type", "custom_scenario", "horizon_days"):
        if k in item:
            out[k] = item[k]
    return to_json_boundary(out)


# ---------------------------------------------------------------- the IF node: Custom Scenario?
def route_for(item: dict) -> str:
    """notEmpty on custom_scenario: true branch (the LLM chain) for a non-empty string, else the template branch."""
    v = item.get("custom_scenario")
    if v is None:
        return "template"
    if isinstance(v, str):
        return "custom_llm" if len(v) > 0 else "template"
    raise NotModelled(f"custom_scenario {v!r} is not a string (n8n's loose type check is not copied)")


# ---------------------------------------------------------------- code node 2 (Python): Load_Template_Scenario
def load_template_scenario(items: list[dict]) -> dict:
    cur = items[0]
    scenario_type = cur.get("scenario_type", DEFAULT_TEMPLATE)
    scenario = TEMPLATES.get(scenario_type, TEMPLATES[DEFAULT_TEMPLATE])
    portfolio = None
    for item in items:
        if "portfolio" in item:
            portfolio = item["portfolio"]
            break
        if "holdings" in item:
            portfolio = {"holdings": item["holdings"]}
            break
    return {"scenario": json.loads(json.dumps(scenario)), "scenario_source": "template", "portfolio": portfolio}


# ---------------------------------------------------------------- code node 3 (Python): Save_Portfolio_Before_LLM
def save_portfolio_before_llm(items: list[dict]) -> dict:
    portfolio = None
    custom_scenario = items[0].get("custom_scenario", "")
    for item in items:
        if "portfolio" in item:
            portfolio = item["portfolio"]
            break
    return {"custom_scenario": custom_scenario, "saved_portfolio": portfolio}


# ---------------------------------------------------------------- code node 4 (Python): Stress_Test_Engine
def stress_test_engine(items: list[dict]) -> dict:
    cur = items[0]
    scenario = cur.get("scenario")
    if not scenario:
        return {"error": "Scenario not found in input",
                "debug": {"current_item": cur, "all_items": [i for i in items]}}
    portfolio = None
    if "portfolio" in cur:
        portfolio = cur["portfolio"]
    if not portfolio:
        for item in items:
            if "portfolio" in item:
                portfolio = item["portfolio"]
                break
    if not portfolio and "portfolio" in scenario:
        portfolio = scenario["portfolio"]
    if not portfolio:
        return {"error": "Portfolio not found",
                "debug": {"available_keys_current_item": list(cur.keys()),
                          "scenario_keys": list(scenario.keys()) if isinstance(scenario, dict) else None,
                          "current_item": cur, "all_items": [i for i in items]}}
    if "holdings" not in portfolio:
        return {"error": "Portfolio found but missing holdings array", "portfolio_received": portfolio}

    shocks = scenario["shocks"]
    holdings = portfolio["holdings"]
    results = []
    total_loss = 0
    initial_value = INITIAL_VALUE
    for holding in holdings:
        ticker = holding["ticker"]
        weight = holding["weight"]
        position_value = initial_value * weight
        total_shock = shocks.get("market", 0)
        sector = SECTOR_MAP.get(ticker, "tech_sector")
        total_shock += shocks.get(sector, 0)
        if ticker in AI_STOCKS:
            total_shock += shocks.get("ai_stocks", 0)
        if ticker in GROWTH_STOCKS:
            total_shock += shocks.get("growth_stocks", 0)
        position_loss = position_value * total_shock
        total_loss += position_loss
        results.append({"ticker": ticker, "weight": weight, "initial_value": round(position_value, 2),
                        "shock_pct": round(total_shock * 100, 2), "loss": round(position_loss, 2),
                        "final_value": round(position_value + position_loss, 2)})
    results.sort(key=lambda x: x["loss"])
    top_losers = results[:3]
    final_value = initial_value + total_loss
    drawdown_pct = (total_loss / initial_value) * 100
    risk_level = "LOW"
    for name, bound in RISK_LEVELS:
        if abs(drawdown_pct) > bound:
            risk_level = name
            break
    return {"scenario_name": scenario["name"], "scenario_description": scenario["description"],
            "initial_portfolio_value": initial_value, "final_portfolio_value": round(final_value, 2),
            "total_loss": round(total_loss, 2), "drawdown_pct": round(drawdown_pct, 2),
            "top_losers": top_losers, "all_positions": results, "risk_level": risk_level}


# ---------------------------------------------------------------- the chain, in the workflow's order
def run_chain(request: dict) -> dict:
    """Edit Fields -> Validate Portfolio -> (Merge, sample mode: just that item) -> Custom Scenario? ->
    template: Load_Template_Scenario -> Stress_Test_Engine; custom: Save_Portfolio_Before_LLM -> HANDOFF (Groq).
    Raises ValidationFailed / JSTypeError / NotModelled / the engine's own Python errors, like the workflow's nodes."""
    item = edit_fields(request)
    validated = validate_portfolio(json.loads(json.dumps(item)))      # the node mutates its input; work on a copy
    trace = {"edit_fields": item, "validate_portfolio": validated}
    route = route_for(validated)
    trace["route"] = route
    if route == "template":
        loaded = to_json_boundary(load_template_scenario([validated]))
        trace["load_template_scenario"] = loaded
        trace["stress_test_engine"] = to_json_boundary(stress_test_engine([loaded]))
    else:
        trace["save_portfolio_before_llm"] = to_json_boundary(save_portfolio_before_llm([validated]))
        trace["stress_test_engine"] = None
        trace["handoff"] = "Groq chat call needed for a custom scenario: not approved, not made"
    return trace


def load_validator():
    p = REPO / "scripts" / "gigo" / f"{SLUG}-validate-data-shape.py"
    spec = importlib.util.spec_from_file_location("stress_validator", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sample-dir", default=str(REPO / f"data/raw/{SLUG}/sample/clean"))
    ap.add_argument("--now", default=None, help="pin generated_at (ISO) and the log file's date")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    sample_dir = Path(args.sample_dir).resolve()
    if not sample_dir.is_dir():
        print(f"sample folder missing: {sample_dir}", file=sys.stderr)
        return 2
    validator = load_validator()
    files = sorted(p for p in sample_dir.iterdir() if p.is_file() and p.suffix == ".json")
    judged = [validator.judge(p, sys.modules[__name__]) for p in files]
    rejected = [j for j in judged if not j["accepted"]]
    if rejected:
        print(f"REFUSED: the step-3 gate rejects {len(rejected)} of {len(judged)} request(s); nothing was run or written:", file=sys.stderr)
        for j in rejected:
            print(f"  - {j['id']}: {'; '.join(j['reasons'])}", file=sys.stderr)
        return 1
    results = []
    for j in judged:
        trace = run_chain(j["request"])
        results.append({"id": j["id"], "route": trace["route"], "scenario_source": (trace.get("load_template_scenario") or {}).get("scenario_source", "custom_llm (not run)"),
                        "result": trace["stress_test_engine"], "handoff": trace.get("handoff")})
    now = args.now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    day = now[:10]
    out_dir = REPO / "data" / "verified" / SLUG / sample_dir.name
    out_path = out_dir / "stress-results.json"
    log_path = REPO / "logs" / f"{SLUG}-run-approved-tools-{day}.json"
    ran = [r for r in results if r["result"] is not None]
    log = {"tool_name": f"{SLUG}-run-approved-tools", "input_path": str(sample_dir.relative_to(REPO)) if sample_dir.is_relative_to(REPO) else str(sample_dir),
           "output_path": str(out_path.relative_to(REPO)), "action_taken": f"ran the stress-test chain on {len(ran)} request(s); {len(results) - len(ran)} stopped at the Groq handoff",
           "approval_id": None, "no_write_mode": bool(args.no_write), "mode": "sample", "requests": len(results),
           "risk_levels": {k: sum(1 for r in ran if r["result"]["risk_level"] == k) for k in ("CRITICAL", "HIGH", "MODERATE", "LOW")},
           "handoffs_not_made": HANDOFFS, "generated_at": now}
    if not args.no_write:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({"step": "run-approved-tools", "mode": "sample", "results": results}, indent=2, ensure_ascii=False) + "\n")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n")
    print(f"{sample_dir.name}: {len(results)} request(s), {len(ran)} stress-tested, {len(results) - len(ran)} stopped at the Groq handoff; "
          f"risk levels {log['risk_levels']}" + ("" if args.no_write else f" -> {out_path.relative_to(REPO)}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
