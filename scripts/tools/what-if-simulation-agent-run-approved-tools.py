"""Purpose: Step 5 of recipes/what-if-simulation-agent.md: run the approved, local, deterministic tools of the What-If
         Simulation Agent on validated requests, in sample mode. It is a Python port of six nodes of the workflow, in
         the workflow's own order: Parse & Validate Input (its defaults and rules), Sim 1 (growth vs sentiment),
         Sim 2 (risk appetite), Sim 3 (threshold break), Aggregate & Score All Simulations, and Build AI Prompt.
Input: the validator's output (data/verified/what-if-simulation-agent/clean/validated.json), or --input <path>.
       Refuses it unless every record was accepted by step 3.
Output: <output-dir>/simulation-results.json (one result per request, ending in the prompt the workflow would send)
        and logs/what-if-simulation-agent-run-approved-tools-<YYYY-MM-DD>.json with tool_name, input_path,
        output_path, action_taken, approval_id, no_write_mode (the recipe's step-5 fields) plus the live handoffs.
Side effects: writes those two files. No network, no credentials, no database. The Groq call and the PostgreSQL
              write are NOT made: each is recorded as a handoff with approved_for_live_action false.
Idempotent: Yes; same input, simulation ids and timestamp give the same bytes. The workflow draws the simulation
            id and timestamp from the clock and Math.random(); here they are derived from the request unless
            --simulation-id/--timestamp pin them (the parity check pins them to the JavaScript's own values).
Errors: exit 1 and nothing written if any record was rejected upstream or the input is not the validator's output.
JavaScript fidelity: the port copies what JavaScript does where it differs from Python: Math.round (half goes up),
        toFixed (exact binary value, ties up), Number-to-string in templates (0.85, 100, 1e-7), parseFloat's prefix
        parsing, `??` vs `||`, and the sweep loop's rounding to three decimals.
Recipe: recipes/what-if-simulation-agent.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

SLUG = "what-if-simulation-agent"
REPO = Path(__file__).resolve().parents[2]
NAN = float("nan")


# ---------------------------------------------------------------- JavaScript semantics, copied on purpose
def js_truthy(v: Any) -> bool:
    if v is None or v is False:
        return False
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return not (v == 0 or (isinstance(v, float) and math.isnan(v)))
    if isinstance(v, str):
        return v != ""
    return True


def js_num_str(x: float) -> str:
    """Number.prototype.toString for a double (what a template literal prints)."""
    if math.isnan(x):
        return "NaN"
    if math.isinf(x):
        return "Infinity" if x > 0 else "-Infinity"
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    d = Decimal(repr(abs(x))).normalize()
    digits = "".join(map(str, d.as_tuple().digits)).rstrip("0") or "0"
    k = len(digits)
    n = len(d.as_tuple().digits) + d.as_tuple().exponent
    if k <= n <= 21:
        return sign + digits + "0" * (n - k)
    if 0 < n <= 21:
        return sign + digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return sign + "0." + "0" * (-n) + digits
    e = n - 1
    mant = digits[0] + ("." + digits[1:] if k > 1 else "")
    return f"{sign}{mant}e{'+' if e >= 0 else '-'}{abs(e)}"


def js_string(v: Any) -> str:
    """String(v)."""
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return js_num_str(float(v))
    if isinstance(v, list):
        return ",".join("" if e is None else js_string(e) for e in v)
    if isinstance(v, dict):
        return "[object Object]"
    return str(v)


_PF = re.compile(r"^[+-]?(?:Infinity|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)")


def js_parse_float(v: Any) -> float:
    """parseFloat(v): String(v), then the longest numeric prefix, else NaN."""
    s = js_string(v).lstrip(" \t\n\r\v\f ﻿  ")
    m = _PF.match(s)
    if not m:
        return NAN
    t = m.group(0)
    if t.endswith("Infinity"):
        return -math.inf if t.startswith("-") else math.inf
    return float(t)


def js_parse_int(s: str) -> float:
    m = re.match(r"^\s*([+-]?\d+)", s)
    return float(int(m.group(1))) if m else NAN


def js_round(x: float) -> float:
    """Math.round: halves go toward +infinity."""
    if math.isnan(x) or math.isinf(x):
        return x
    f = math.floor(x)
    return float(f + 1) if (x - f) >= 0.5 else float(f)


def js_fixed(x: float, digits: int) -> str:
    """Number.prototype.toFixed: exact binary value, ties pick the larger n."""
    if math.isnan(x):
        return "NaN"
    if abs(x) >= 1e21:
        return js_num_str(x)
    neg = x < 0
    q = Decimal(abs(x)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    s = format(q, "f")
    return ("-" + s) if neg and q != 0 else s


def jn(x: float) -> str:
    return js_num_str(x)


def js_min(*xs: float) -> float:
    """Math.min: any NaN makes the answer NaN (Python's min() just compares and may return the other value)."""
    return NAN if any(isinstance(x, float) and math.isnan(x) for x in xs) else min(xs)


def js_max(*xs: float) -> float:
    """Math.max: any NaN makes the answer NaN."""
    return NAN if any(isinstance(x, float) and math.isnan(x) for x in xs) else max(xs)


# ---------------------------------------------------------------- Parse & Validate Input
RISK = ("low", "medium", "high")
HORIZONS = ("3month", "1year", "5year")
DEFAULTS = {"revenue_growth": 0.15, "sentiment_score": 0.50, "current_price": 100, "pe_ratio": 25,
            "debt_equity": 0.50, "market_cap_billions": 10}


class ValidationFailed(Exception):
    pass


def _nullish_default(body: dict, key: str) -> Any:
    v = body.get(key)
    return DEFAULTS[key] if v is None else v


def parse_input_collect(payload: dict) -> tuple[dict, list[str]]:
    """The node's defaults, normalisation and rules, returning (parsed input, rule errors) instead of throwing.
    `payload` is the webhook item; the node reads its `body` if truthy."""
    body = payload.get("body") if js_truthy(payload.get("body")) else payload
    inp = {
        "company": js_string(body.get("company") if js_truthy(body.get("company")) else "Unknown Company"),
        "ticker": js_string(body.get("ticker") if js_truthy(body.get("ticker")) else "N/A").upper(),
        "revenue_growth": js_parse_float(_nullish_default(body, "revenue_growth")),
        "sentiment_score": js_parse_float(_nullish_default(body, "sentiment_score")),
        "risk_appetite": js_string(body.get("risk_appetite") if js_truthy(body.get("risk_appetite")) else "medium").lower(),
        "time_horizon": js_string(body.get("time_horizon") if js_truthy(body.get("time_horizon")) else "1year").lower(),
        "current_price": js_parse_float(_nullish_default(body, "current_price")),
        "pe_ratio": js_parse_float(_nullish_default(body, "pe_ratio")),
        "debt_equity": js_parse_float(_nullish_default(body, "debt_equity")),
        "market_cap_billions": js_parse_float(_nullish_default(body, "market_cap_billions")),
    }
    errors = []
    if inp["revenue_growth"] < -1 or inp["revenue_growth"] > 20:
        errors.append("revenue_growth must be between -1.0 and 20.0")
    if inp["sentiment_score"] < 0 or inp["sentiment_score"] > 1:
        errors.append("sentiment_score must be 0–1")
    if inp["risk_appetite"] not in RISK:
        errors.append("risk_appetite must be low | medium | high")
    if inp["pe_ratio"] < 0:
        errors.append("pe_ratio must be positive")
    if inp["debt_equity"] < 0:
        errors.append("debt_equity must be positive")
    if inp["time_horizon"] not in HORIZONS:
        inp["time_horizon"] = "1year"
    return inp, errors


def parse_input(payload: dict) -> dict:
    """Parse & Validate Input as the workflow runs it: throws on any broken rule."""
    inp, errors = parse_input_collect(payload)
    if errors:
        raise ValidationFailed("Validation Failed: " + " | ".join(errors))
    return inp


# ---------------------------------------------------------------- Sim 1: growth vs sentiment
SIGNAL_MATRIX = {
    "HIGH_HIGH": ("STRONG_BUY", 0.88, "LOW", "+15 to +25%", "+60 to +120%", "Both fundamentals and market conviction are aligned — ideal setup."),
    "HIGH_MEDIUM": ("BUY", 0.72, "LOW_MEDIUM", "+8 to +15%", "+40 to +80%", "Strong fundamentals; market is starting to recognise the value."),
    "HIGH_LOW": ("FUNDAMENTAL_BUY", 0.61, "MEDIUM", "-5 to +5%", "+30 to +70%", "Market undervaluing strong fundamentals — contrarian value play."),
    "MEDIUM_HIGH": ("HOLD_WATCH", 0.55, "MEDIUM", "+5 to +12%", "+15 to +35%", "Sentiment slightly ahead of fundamentals — monitor for convergence."),
    "MEDIUM_MEDIUM": ("HOLD", 0.65, "MEDIUM", "0 to +8%", "+10 to +25%", "Balanced but lacks a strong catalyst either way."),
    "MEDIUM_LOW": ("UNDERPERFORM", 0.60, "MEDIUM_HIGH", "-5 to +5%", "+5 to +15%", "Adequate fundamentals dragged down by weak sentiment."),
    "LOW_HIGH": ("BUBBLE_RISK", 0.75, "HIGH", "+5 to +15%", "-20 to 0%", "DANGER: Sentiment massively disconnected from weak fundamentals."),
    "LOW_MEDIUM": ("SELL", 0.68, "HIGH", "-5 to -15%", "-10 to +10%", "Deteriorating fundamentals with fading sentiment support."),
    "LOW_LOW": ("STRONG_SELL", 0.82, "VERY_HIGH", "-15 to -30%", "-30 to -10%", "Both fundamentals and market sentiment fully bearish."),
}


def levels(g: float, s: float) -> tuple[str, str]:
    gl = "HIGH" if g >= 0.25 else "MEDIUM" if g >= 0.10 else "LOW"
    sl = "HIGH" if s >= 0.65 else "MEDIUM" if s >= 0.40 else "LOW"
    return gl, sl


def sim1(data: dict) -> dict:
    growth, sentiment = data["revenue_growth"], data["sentiment_score"]
    gl, sl = levels(growth, sentiment)
    sig, conf, risk, short, long_, desc = SIGNAL_MATRIX[f"{gl}_{sl}"]
    result = {"signal": sig, "confidence": conf, "risk": risk, "short_term": short, "long_term": long_, "description": desc}
    conflict = (gl == "HIGH" and sl == "LOW") or (gl == "LOW" and sl == "HIGH")
    bubble = 0.85 if (gl == "LOW" and sl == "HIGH") else 0.48 if (gl == "MEDIUM" and sl == "HIGH") else 0.35 if (gl == "LOW" and sl == "MEDIUM") else 0.12
    corr = "HIGH (>65%)" if bubble > 0.70 else "MEDIUM (30–65%)" if bubble > 0.40 else "LOW (<30%)"
    if gl == "HIGH" and sl == "LOW":
        insight = (f"⚠️ CONFLICT DETECTED: Strong {jn(js_round(growth * 100))}% revenue growth is being ignored by the market "
                   f"(sentiment {js_fixed(sentiment * 100, 0)}%). Classic value opportunity — patience required.")
    elif gl == "LOW" and sl == "HIGH":
        insight = (f"🚨 BUBBLE RISK: High sentiment ({js_fixed(sentiment * 100, 0)}%) is NOT supported by "
                   f"{jn(js_round(growth * 100))}% growth. Correction probability is {corr}.")
    else:
        insight = f"{gl} growth + {sl} sentiment → {sig}. {desc}"
    out = dict(data)
    out["sim1_growth_sentiment"] = {
        "simulation": "GROWTH_VS_SENTIMENT",
        "inputs": {"growth_rate": growth, "sentiment_score": sentiment, "growth_level": gl, "sentiment_level": sl},
        "output": result, "conflict_detected": conflict, "bubble_risk_score": bubble,
        "correction_probability": corr, "key_insight": insight,
    }
    return out


# ---------------------------------------------------------------- Sim 2: risk appetite
PROFILES = {
    "low": {"name": "Conservative", "icon": "🔵", "growth_threshold": 0.15, "sentiment_threshold": 0.60, "pe_max": 25, "de_max": 0.50,
            "max_position_pct": 5, "stop_loss_pct": 5, "take_profit_pct": 12, "preferred_horizon": "3–5 years", "max_drawdown": "10%",
            "description": "Capital preservation is paramount. Prefers stable, established companies with low volatility and dividends."},
    "medium": {"name": "Balanced", "icon": "🟢", "growth_threshold": 0.10, "sentiment_threshold": 0.45, "pe_max": 40, "de_max": 0.80,
               "max_position_pct": 10, "stop_loss_pct": 10, "take_profit_pct": 25, "preferred_horizon": "1–3 years", "max_drawdown": "20%",
               "description": "Balanced growth and protection. Accepts moderate volatility in exchange for higher long-term returns."},
    "high": {"name": "Aggressive", "icon": "🟠", "growth_threshold": 0.05, "sentiment_threshold": 0.35, "pe_max": 80, "de_max": 1.50,
             "max_position_pct": 20, "stop_loss_pct": 20, "take_profit_pct": 60, "preferred_horizon": "6–18 months", "max_drawdown": "40%",
             "description": "Maximum growth orientation. High volatility tolerance. Seeks asymmetric upside opportunities."},
}
WEIGHTS = (0.30, 0.25, 0.25, 0.20)


def _wpr(passes: list[bool]) -> float:
    total = 0.0
    for p, w in zip(passes, WEIGHTS):
        total = total + (w if p else 0)
    return total


def sim2(data: dict) -> dict:
    risk, growth, sentiment, pe, de = data["risk_appetite"], data["revenue_growth"], data["sentiment_score"], data["pe_ratio"], data["debt_equity"]
    p = PROFILES[risk]
    passes = [growth >= p["growth_threshold"], sentiment >= p["sentiment_threshold"], pe <= p["pe_max"], de <= p["de_max"]]
    criteria = [
        {"name": "Revenue Growth", "pass": passes[0], "actual": f"{jn(js_round(growth * 100))}%", "required": f"≥ {jn(js_round(p['growth_threshold'] * 100))}%", "weight": 0.30},
        {"name": "Market Sentiment", "pass": passes[1], "actual": js_fixed(sentiment, 2), "required": f"≥ {js_fixed(p['sentiment_threshold'], 2)}", "weight": 0.25},
        {"name": "P/E Ratio", "pass": passes[2], "actual": js_fixed(pe, 1), "required": f"≤ {jn(p['pe_max'])}", "weight": 0.25},
        {"name": "Debt / Equity", "pass": passes[3], "actual": js_fixed(de, 2), "required": f"≤ {jn(p['de_max'])}", "weight": 0.20},
    ]
    wpr = _wpr(passes)
    pass_count = sum(1 for x in passes if x)
    rec = "ENTER_FULL_POSITION" if wpr >= 0.80 else "ENTER_PARTIAL_POSITION" if wpr >= 0.55 else "WATCHLIST_ONLY" if wpr >= 0.30 else "AVOID"
    cross = []
    for level, q in PROFILES.items():
        w = _wpr([growth >= q["growth_threshold"], sentiment >= q["sentiment_threshold"], pe <= q["pe_max"], de <= q["de_max"]])
        r = "ENTER" if w >= 0.80 else "PARTIAL" if w >= 0.55 else "WATCH" if w >= 0.30 else "AVOID"
        cross.append({"risk_level": level, "investor_type": q["name"], "fit_score_pct": js_round(w * 100), "recommendation": r,
                      "max_position": f"{q['max_position_pct']}%", "stop_loss": f"{q['stop_loss_pct']}%", "is_selected": level == risk})
    insight = (f"{p['icon']} {p['name']} investor → {rec} | {jn(js_round(wpr * 100))}% criteria met ({pass_count}/4 passed) | "
               f"Max position: {p['max_position_pct']}% | Stop-loss: {p['stop_loss_pct']}%")
    out = dict(data)
    out["sim2_risk_appetite"] = {
        "simulation": "RISK_APPETITE",
        "inputs": {"risk_appetite": risk, "pe_ratio": pe, "debt_equity": de, "revenue_growth": growth, "sentiment_score": sentiment},
        "profile": p, "criteria_evaluation": criteria, "weighted_pass_rate": js_round(wpr * 100) / 100,
        "pass_count": f"{pass_count}/4", "recommendation": rec, "cross_profile_comparison": cross, "key_insight": insight,
    }
    return out


# ---------------------------------------------------------------- Sim 3: threshold break
SIGNAL_NAME = {"HIGH_HIGH": "STRONG_BUY", "HIGH_MEDIUM": "BUY", "HIGH_LOW": "FUNDAMENTAL_BUY", "MEDIUM_HIGH": "HOLD_WATCH",
               "MEDIUM_MEDIUM": "HOLD", "MEDIUM_LOW": "UNDERPERFORM", "LOW_HIGH": "BUBBLE_RISK", "LOW_MEDIUM": "SELL", "LOW_LOW": "STRONG_SELL"}


def classify(g: float, s: float) -> str:
    gl, sl = levels(g, s)
    return SIGNAL_NAME.get(f"{gl}_{sl}") or "HOLD"


def find_breakpoints(sweep_var: str, fixed_g: float, fixed_s: float, lo: float, hi: float, step: float) -> list[dict]:
    sweep, v = [], lo
    while v <= hi + 0.0001:
        g = v if sweep_var == "growth" else fixed_g
        s = v if sweep_var == "sentiment" else fixed_s
        sweep.append({"value": v, "recommendation": classify(g, s)})
        v = js_round((v + step) * 1000) / 1000
    breaks = []
    for i in range(1, len(sweep)):
        if sweep[i]["recommendation"] != sweep[i - 1]["recommendation"]:
            threshold = js_round(((sweep[i - 1]["value"] + sweep[i]["value"]) / 2) * 1000) / 1000
            current = fixed_g if sweep_var == "growth" else fixed_s
            dist = abs(threshold - current)
            breaks.append({"transition": f"{sweep[i - 1]['recommendation']} → {sweep[i]['recommendation']}", "threshold_approx": threshold,
                           "direction": "MUST_INCREASE_TO_TRIGGER" if sweep[i]["value"] > current else "BREAKS_IF_DECREASES",
                           "distance_from_current": js_round(dist * 1000) / 1000, "is_nearest": False})
    if breaks:
        ni = 0
        for i, b in enumerate(breaks):
            if b["distance_from_current"] < breaks[ni]["distance_from_current"]:
                ni = i
        breaks[ni]["is_nearest"] = True
    return breaks


def sim3(data: dict) -> dict:
    g0, s0 = data["revenue_growth"], data["sentiment_score"]
    base = classify(g0, s0)
    sent_b = find_breakpoints("sentiment", g0, s0, 0.00, 1.00, 0.05)
    grow_b = find_breakpoints("growth", g0, s0, -0.10, 0.60, 0.05)
    sent_near = sum(1 for b in sent_b if b["distance_from_current"] <= 0.15)
    grow_near = sum(1 for b in grow_b if b["distance_from_current"] <= 0.10)
    driver = "SENTIMENT" if sent_near >= grow_near else "GROWTH"
    min_s = js_min(*[b["distance_from_current"] for b in sent_b]) if sent_b else 0.50
    min_g = js_min(*[b["distance_from_current"] for b in grow_b]) if grow_b else 0.50
    stability = js_round(js_min(1, (min_s * 2.0 + min_g * 3.0) / 2.5) * 100) / 100
    cases = [("Sentiment −10%", g0, js_max(0, s0 - 0.10)), ("Sentiment +10%", g0, js_min(1, s0 + 0.10)), ("Growth −10pp", g0 - 0.10, s0),
             ("Growth +10pp", g0 + 0.10, s0), ("Both −10%", g0 - 0.10, js_max(0, s0 - 0.10)), ("Both +10%", g0 + 0.10, js_min(1, s0 + 0.10))]
    stress = []
    for name, g, s in cases:
        r = classify(g, s)
        stress.append({"scenario": name, "result": r, "changed": r != base, "delta": f"{base} → {r}" if r != base else "No change"})
    breach = sum(1 for t in stress if t["changed"])
    resiliency = "HIGH" if breach == 0 else "MEDIUM" if breach <= 2 else "LOW"
    near_s = next((b for b in sent_b if b["is_nearest"]), None)
    if near_s and near_s["distance_from_current"] < 0.10:
        insight = (f"🚨 HIGH SENSITIVITY: Decision is {js_fixed(near_s['distance_from_current'] * 100, 0)} sentiment-points from a change "
                   f"({near_s['transition']}). Primary driver: {driver}.")
    elif stability > 0.7:
        insight = (f"✅ STABLE: Current recommendation ({base}) is robust. Nearest trigger is {js_fixed(min_s * 100, 0)} sentiment-points away. "
                   f"Primary driver: {driver}.")
    else:
        nz = f"Sentiment threshold: {near_s['transition']} at ~{jn(near_s['threshold_approx'])}" if near_s else ""
        insight = f"⚠️ MODERATE SENSITIVITY: {driver} is the primary driver. {nz}. Stability: {jn(stability)}."
    out = dict(data)
    out["sim3_threshold_break"] = {
        "simulation": "THRESHOLD_BREAK", "current_state": {"recommendation": base, "growth": g0, "sentiment": s0},
        "sentiment_breakpoints": sent_b, "growth_breakpoints": grow_b, "stress_tests": stress,
        "sensitivity": {"sentiment_breaks_nearby": sent_near, "growth_breaks_nearby": grow_near, "primary_driver": driver,
                        "stress_resiliency": resiliency, "stress_breach_count": f"{breach}/6"},
        "stability_score": stability, "key_insight": insight,
    }
    return out


# ---------------------------------------------------------------- Aggregate & Score All Simulations
SIGNAL_SCORES = {"STRONG_BUY": 5.0, "BUY": 4.2, "FUNDAMENTAL_BUY": 3.8, "HOLD_WATCH": 3.2, "HOLD": 3.0, "UNDERPERFORM": 2.2,
                 "BUBBLE_RISK": 1.8, "SELL": 1.5, "STRONG_SELL": 1.0}
REC_SCORES = {"ENTER_FULL_POSITION": 5.0, "ENTER_PARTIAL_POSITION": 3.8, "WATCHLIST_ONLY": 2.5, "AVOID": 1.0}


def aggregate(data: dict) -> dict:
    s1, s2, s3 = data["sim1_growth_sentiment"], data["sim2_risk_appetite"], data["sim3_threshold_break"]
    s1_raw = (SIGNAL_SCORES.get(s1["output"]["signal"]) or 3.0) * s1["output"]["confidence"]
    s2_raw = REC_SCORES.get(s2["recommendation"]) or 3.0
    s3_raw = s3["stability_score"] * 5.0
    w = {"sim1": 0.45, "sim2": 0.35, "sim3": 0.20}
    raw = (s1_raw * w["sim1"]) + (s2_raw * w["sim2"]) + (s3_raw * w["sim3"])
    score = js_round(js_min(5.0, js_max(1.0, raw)) * 100) / 100
    final = "STRONG_BUY" if score >= 4.2 else "BUY" if score >= 3.6 else "HOLD" if score >= 2.8 else "SELL" if score >= 1.8 else "STRONG_SELL"
    norm = score / 5.0
    th = 3.0 if data["time_horizon"] == "5year" else 0.25 if data["time_horizon"] == "3month" else 1.0
    base_return = (score - 3.0) * 18
    best_p = js_round(js_min(65, js_max(5, norm * 60 + 5)))
    worst_p = js_round(js_min(65, js_max(5, (1 - norm) * 55 + 5)))
    exp_p = 100 - best_p - worst_p
    scenarios = {
        "best_case": {"probability": best_p, "label": "All tailwinds materialise", "return_estimate": f"+{jn(js_round((base_return + 28) * th))}%",
                      "conditions": ["Revenue growth beats estimates", "Positive sentiment momentum", "Macro conditions remain favourable", "No sector disruptions"]},
        "expected_case": {"probability": exp_p, "label": "Base case — current trajectory continues",
                          "return_estimate": f"{'+' if base_return >= 0 else ''}{jn(js_round(base_return * th))}%",
                          "conditions": ["Current growth rate maintained", "Sentiment stable", "Normal market conditions", "No major earnings surprises"]},
        "worst_case": {"probability": worst_p, "label": "Headwinds emerge", "return_estimate": f"-{jn(js_round((abs(base_return) + 22) * th))}%",
                       "conditions": ["Sentiment deteriorates sharply", "Revenue misses estimates", "Macro headwinds", "Sector rotation away"]},
    }
    flags = []
    if s1["conflict_detected"]:
        flags.append({"severity": "MEDIUM", "flag": "Growth–Sentiment conflict detected", "action": "Consider scaling in gradually"})
    if s1["bubble_risk_score"] > 0.60:
        flags.append({"severity": "HIGH", "flag": f"Bubble risk score: {jn(s1['bubble_risk_score'])}", "action": "Avoid new positions; set tight stop-loss"})
    if s3["stability_score"] < 0.40:
        flags.append({"severity": "HIGH", "flag": "Recommendation near multiple breakpoints", "action": "Monitor daily; do not hold large position"})
    if s3["sensitivity"]["sentiment_breaks_nearby"] > 2:
        flags.append({"severity": "MEDIUM", "flag": "Highly sentiment-sensitive — 3+ triggers nearby", "action": "Watch social/news sentiment closely"})
    if data["pe_ratio"] > 60 and data["revenue_growth"] < 0.20:
        flags.append({"severity": "HIGH", "flag": f"P/E {jn(data['pe_ratio'])}x not justified by {jn(js_round(data['revenue_growth'] * 100))}% growth",
                      "action": "Valuations stretched — wait for pullback"})
    if data["debt_equity"] > 1.0:
        flags.append({"severity": "MEDIUM", "flag": f"Elevated D/E ratio: {jn(data['debt_equity'])}", "action": "Monitor debt levels and cash flow"})
    if js_parse_int(s3["sensitivity"]["stress_breach_count"]) > 4:
        flags.append({"severity": "HIGH", "flag": "Low stress resiliency — 5+ scenarios trigger change", "action": "Only trade with defined risk limits"})
    conf_inputs = [s1["output"]["confidence"], s2["weighted_pass_rate"], s3["stability_score"]]
    overall = js_round(sum(conf_inputs) / 3 * 100)
    out = dict(data)
    out["aggregate"] = {
        "final_recommendation": final, "score": score, "score_label": f"{jn(score)}/5.0", "confidence_pct": overall, "simulation_weights": w,
        "component_scores": {"sim1_weighted": js_round(s1_raw * w["sim1"] * 100) / 100, "sim2_weighted": js_round(s2_raw * w["sim2"] * 100) / 100,
                             "sim3_weighted": js_round(s3_raw * w["sim3"] * 100) / 100},
        "scenarios": scenarios, "risk_flags": flags, "risk_flag_count": len(flags), "primary_risk_driver": s3["sensitivity"]["primary_driver"],
        "key_signals": [x for x in (s1["key_insight"], s2["key_insight"], s3["key_insight"]) if x],
    }
    return out


# ---------------------------------------------------------------- Build AI Prompt
def build_prompt(d: dict) -> dict:
    agg, s1, s2, s3 = d["aggregate"], d["sim1_growth_sentiment"], d["sim2_risk_appetite"], d["sim3_threshold_break"]
    L = "═══════════════════════════════════════════"
    lines = [
        "You are Mycroft, an expert AI investment analyst from the Mycroft open-source project.",
        "Analyse the following What-If simulation output and return a structured JSON investment report.",
        "", L, "COMPANY PROFILE", L,
        f"Company:         {d['company']} ({d['ticker']})",
        f"Current Price:   ${jn(d['current_price'])}",
        f"Revenue Growth:  {jn(js_round(d['revenue_growth'] * 100))}% YoY",
        f"Sentiment Score: {jn(d['sentiment_score'])}/1.0",
        f"P/E Ratio:       {jn(d['pe_ratio'])}x",
        f"Debt/Equity:     {jn(d['debt_equity'])}",
        f"Market Cap:      ${jn(d['market_cap_billions'])}B",
        f"Risk Profile:    {d['risk_appetite'].upper()}",
        f"Time Horizon:    {d['time_horizon']}",
        "", L, "SIMULATION 1 — Growth vs Sentiment Tradeoff", L,
        f"Signal:             {s1['output']['signal']}",
        f"Confidence:         {jn(js_round(s1['output']['confidence'] * 100))}%",
        "Conflict:           " + ("⚠️ YES — fundamentals and sentiment diverge" if s1["conflict_detected"] else "No conflict"),
        f"Bubble Risk Score:  {jn(s1['bubble_risk_score'])}/1.0",
        f"Short-term Return:  {s1['output']['short_term']}",
        f"Long-term Return:   {s1['output']['long_term']}",
        f"Insight:            {s1['key_insight']}",
        "", L, f"SIMULATION 2 — Risk Appetite ({s2['profile']['name']} Investor)", L,
        f"Recommendation:     {s2['recommendation']}",
        f"Criteria Passed:    {s2['pass_count']}",
        f"Weighted Pass Rate: {jn(js_round(s2['weighted_pass_rate'] * 100))}%",
        f"Max Position Size:  {s2['profile']['max_position_pct']}% of portfolio",
        f"Stop-Loss:          {s2['profile']['stop_loss_pct']}%",
        f"Take-Profit Target: {s2['profile']['take_profit_pct']}%",
        f"Insight:            {s2['key_insight']}",
        "", "Cross-Profile Summary:",
    ] + [f"  {p['investor_type']}: {p['recommendation']} ({jn(p['fit_score_pct'])}% fit)" for p in s2["cross_profile_comparison"]] + [
        "", L, "SIMULATION 3 — Threshold Break Analysis", L,
        f"Current Signal:         {s3['current_state']['recommendation']}",
        f"Stability Score:        {jn(s3['stability_score'])}/1.0",
        f"Primary Driver:         {s3['sensitivity']['primary_driver']}",
        f"Sentiment Breaks Near:  {s3['sensitivity']['sentiment_breaks_nearby']}",
        f"Stress Resiliency:      {s3['sensitivity']['stress_resiliency']}",
        f"Stress Breach Count:    {s3['sensitivity']['stress_breach_count']} scenarios triggered a change",
        f"Insight:                {s3['key_insight']}",
        "", "Stress Test Results:",
    ] + [f"  {t['scenario']}: {t['result']} (" + ("⚠️ CHANGED — " + t["delta"] if t["changed"] else "✅ unchanged") + ")" for t in s3["stress_tests"]] + [
        "", L, "AGGREGATE VERDICT", L,
        f"FINAL RECOMMENDATION:  {agg['final_recommendation']}",
        f"Score:                 {agg['score_label']}",
        f"Confidence:            {jn(agg['confidence_pct'])}%",
        f"Risk Flags ({agg['risk_flag_count']}):     " + (" | ".join(f["flag"] for f in agg["risk_flags"]) or "None"),
        "", "Scenario Probabilities:",
        f"  Best Case  ({jn(agg['scenarios']['best_case']['probability'])}%):    {agg['scenarios']['best_case']['return_estimate']}",
        f"  Expected   ({jn(agg['scenarios']['expected_case']['probability'])}%):    {agg['scenarios']['expected_case']['return_estimate']}",
        f"  Worst Case ({jn(agg['scenarios']['worst_case']['probability'])}%):    {agg['scenarios']['worst_case']['return_estimate']}",
        "", L, "YOUR TASK", L,
        "Return ONLY the following JSON — no markdown, no explanation outside the JSON:",
        "",
        "{",
        '  "executive_summary": "2–3 sentences covering the most important aspects of this investment case",',
        '  "bull_case": "The single strongest argument FOR investing in this company right now",',
        '  "bear_case": "The single most important risk that could invalidate the bullish thesis",',
        '  "key_risk_narrative": "Explain the #1 risk in 1–2 sentences, with the specific trigger to watch for",',
        '  "opportunity_narrative": "Explain the primary upside catalyst in 1–2 sentences",',
        '  "action_plan": {',
        f'    "immediate": "Exactly what a {d["risk_appetite"]} investor should do TODAY",',
        '    "monitor_weekly": "The single most important metric to track each week",',
        '    "exit_trigger": "The precise condition (with threshold) that would change the recommendation",',
        '    "position_sizing_note": "Brief note on how large this position should be and why"',
        "  },",
        f'  "mycroft_verdict": "One powerful, memorable sentence that captures the entire investment thesis for {d["company"]}",',
        f'  "confidence_rationale": "Why the confidence is {jn(agg["confidence_pct"])}% — what is certain and what is uncertain"',
        "}",
        f'IMPORTANT: Your action_plan.immediate must strictly match "{agg["final_recommendation"]}". If HOLD — say hold, do not say enter.',
        "",
    ]
    out = dict(d)
    out["ai_prompt"] = "\n".join(lines)
    return out


def jsonable(v: Any) -> Any:
    """JSON the way JSON.stringify writes numbers: 64 not 64.0, and NaN as null."""
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
        return int(v) if v.is_integer() and abs(v) < 1e15 else v
    if isinstance(v, dict):
        return {k: jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    return v


def run_chain(request: dict, simulation_id: str, timestamp: str) -> dict:
    """The six nodes in the workflow's order, on one request (the webhook item)."""
    parsed = parse_input(request)
    parsed = {**parsed, "simulation_id": simulation_id, "timestamp": timestamp}
    return build_prompt(aggregate(sim3(sim2(sim1(parsed)))))


# ---------------------------------------------------------------- the step
def derived_id(request: dict) -> tuple[str, str]:
    """Deterministic stand-in for the workflow's clock/random id: the same request always gets the same id."""
    h = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    return f"SIM-SAMPLE-{h[:6].upper()}", "1970-01-01T00:00:00.000Z"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", default=str(REPO / f"data/verified/{SLUG}/clean/validated.json"))
    ap.add_argument("--output-dir", default=None, help="default: next to the input file")
    ap.add_argument("--simulation-id", default=None, help="pin one id (single-request inputs only)")
    ap.add_argument("--timestamp", default=None)
    ap.add_argument("--now", default=None, help="YYYY-MM-DD for the log file name (default today, UTC)")
    args = ap.parse_args()
    inp = Path(args.input)
    doc = json.loads(inp.read_text())
    if doc.get("step") != "validate-data-shape" or doc.get("rejected"):
        print(f"REFUSED: {inp} is not the validator's output, or it still holds rejected requests "
              f"({len(doc.get('rejected', []))}). Nothing written.", file=sys.stderr)
        return 1
    out_dir = Path(args.output_dir) if args.output_dir else inp.parent
    results = []
    for rec in doc["accepted"]:
        sid, ts = (args.simulation_id, args.timestamp) if (args.simulation_id and len(doc["accepted"]) == 1) else derived_id(rec["request"])
        r = run_chain(rec["request"], sid, args.timestamp or ts)
        results.append({"id": rec["id"], "result": r})
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "simulation-results.json"
    out_path.write_text(json.dumps({"step": "run-approved-tools", "mode": "sample", "tool": "python port of 6 workflow nodes",
                                    "count": len(results), "results": jsonable(results)}, indent=2, ensure_ascii=False) + "\n")
    day = args.now or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log = {
        "tool_name": f"{SLUG} (Parse & Validate Input, Sim 1, Sim 2, Sim 3, Aggregate & Score, Build AI Prompt)",
        "input_path": str(inp.relative_to(REPO)) if inp.is_relative_to(REPO) else str(inp),
        "output_path": str(out_path.relative_to(REPO)) if out_path.is_relative_to(REPO) else str(out_path),
        "action_taken": f"ran {len(results)} request(s) through the six local deterministic nodes; wrote the results and the prompt the workflow would send",
        "approval_id": None, "no_write_mode": False, "mode": "sample",
        "live_handoffs": [
            {"node": "🤖 Groq — Generate Investment Insights", "kind": "http POST (chat completions)", "approved_for_live_action": False,
             "reason": "no approval record; needs a credential named groqApi; not called"},
            {"node": "💾 Save to PostgreSQL", "kind": "database write", "approved_for_live_action": False,
             "reason": "no approval record; needs a credential named postgres; not called"}],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    log_path = REPO / "logs" / f"{SLUG}-run-approved-tools-{day}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n")
    print(f"ran {len(results)} request(s); wrote {out_path} and {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
