import httpx
from typing import Dict, Any
from agent.state import AgentState
from agent.analytics import (
    compute_hhi, compute_entropy, compute_turnover_rate,
    compute_idle_capital_ratio, classify_risk_posture,
    classify_liquidity_preference, classify_concentration,
    reconstruct_portfolio_state, compute_drift_score
)
from config import settings


# ── Node 1: Event Normalizer ──────────────────────────────────────────────────

def event_normalizer(state: AgentState) -> AgentState:
    """Canonicalize events — lowercase asset classes, ensure required fields."""
    normalized = []
    for e in state["events"]:
        normalized.append({
            **e,
            "asset_class": e["asset_class"].lower().replace(" ", "_"),
            "ticker": (e.get("ticker") or "").upper() or None,
            "amount": abs(float(e["amount"])),
        })
    return {**state, "normalized_events": normalized}


# ── Node 2: State Builder ─────────────────────────────────────────────────────

def state_builder(state: AgentState) -> AgentState:
    """Reconstruct current portfolio state from event history."""
    portfolio = reconstruct_portfolio_state(state["normalized_events"])
    total = sum(portfolio.values())
    return {**state, "current_portfolio": portfolio, "total_value": total}


# ── Node 3: Pattern Engine ────────────────────────────────────────────────────

def pattern_engine(state: AgentState) -> AgentState:
    """Identify behavioral patterns in the event stream."""
    events = state["normalized_events"]
    type_counts: Dict[str, int] = {}
    ac_counts: Dict[str, int] = {}

    for e in events:
        etype = e["event_type"]
        ac = e["asset_class"]
        type_counts[etype] = type_counts.get(etype, 0) + 1
        ac_counts[ac] = ac_counts.get(ac, 0) + 1

    dominant_action = max(type_counts, key=type_counts.get) if type_counts else "NONE"
    dominant_asset = max(ac_counts, key=ac_counts.get) if ac_counts else "none"

    # Inaction ratio
    total = len(events)
    inaction = type_counts.get("INACTION_MARKER", 0) + type_counts.get("HOLD_DECISION", 0)
    inaction_ratio = inaction / total if total > 0 else 0.0

    patterns = {
        "type_counts": type_counts,
        "asset_class_counts": ac_counts,
        "dominant_action": dominant_action,
        "dominant_asset_class": dominant_asset,
        "inaction_ratio": round(inaction_ratio, 3),
        "total_events": total,
    }
    return {**state, "patterns": patterns, "dominant_action": dominant_action}


# ── Node 4: Behavior Modeler ──────────────────────────────────────────────────

def behavior_modeler(state: AgentState) -> AgentState:
    """Compute deterministic behavioral metrics."""
    portfolio = state["current_portfolio"]
    total = state["total_value"]
    events = state["normalized_events"]

    weights = {k: v / total for k, v in portfolio.items()} if total > 0 else {}

    hhi = compute_hhi(portfolio)
    entropy = compute_entropy(portfolio)
    turnover = compute_turnover_rate(events, total)
    idle = compute_idle_capital_ratio(portfolio)

    equity_w = weights.get("equities", 0) + weights.get("stocks", 0) + weights.get("equity", 0)
    crypto_w = weights.get("crypto", 0) + weights.get("cryptocurrency", 0)

    risk = classify_risk_posture(hhi, equity_w, crypto_w)
    liquidity = classify_liquidity_preference(idle)
    concentration = classify_concentration(hhi)

    return {
        **state,
        "hhi": round(hhi, 4),
        "entropy": round(entropy, 4),
        "turnover_rate": round(turnover, 4),
        "idle_capital_ratio": round(idle, 4),
        "asset_class_weights": {k: round(v, 4) for k, v in weights.items()},
        "risk_posture": risk,
        "liquidity_preference": liquidity,
        "concentration_tendency": concentration,
    }


# ── Node 5: Drift Detector ────────────────────────────────────────────────────

def drift_detector(state: AgentState) -> AgentState:
    """Compare current weights against baseline strategy weights."""
    baseline = state.get("baseline_weights", {})
    current = state["asset_class_weights"]
    result = compute_drift_score(current, baseline)
    return {
        **state,
        "drift_score": result["score"],
        "weight_deltas": result["deltas"],
    }


# ── Node 6: Strategy Synthesizer (Ollama) ────────────────────────────────────

def strategy_synthesizer(state: AgentState) -> AgentState:
    """Call Ollama to generate a natural-language strategy profile."""
    weights_str = ", ".join(
        f"{k}: {round(v * 100, 1)}%"
        for k, v in sorted(state["asset_class_weights"].items(), key=lambda x: -x[1])
    )

    prompt = f"""You are a financial behavior analyst. Based on the following observed data about an investor's actual capital allocation behavior, write a concise 3-4 sentence strategy profile. Be analytical and specific. Do not use filler phrases.

Observed metrics:
- Asset class weights: {weights_str}
- Risk posture: {state['risk_posture']}
- Liquidity preference: {state['liquidity_preference']}
- Concentration tendency: {state['concentration_tendency']}
- Herfindahl Index (HHI): {state['hhi']} (1.0 = fully concentrated)
- Shannon entropy: {state['entropy']}
- Capital turnover rate: {state['turnover_rate']}
- Idle capital ratio: {state['idle_capital_ratio']}
- Dominant action type: {state['dominant_action']}
- Inaction ratio: {state['patterns'].get('inaction_ratio', 'N/A')}
- Drift from baseline: {state.get('drift_score', 0.0)}

Write the strategy profile:"""

    try:
        resp = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        resp.raise_for_status()
        profile_text = resp.json().get("response", "").strip()
    except Exception as exc:
        # Fallback to deterministic summary if Ollama is unavailable
        profile_text = (
            f"The investor follows a {state['risk_posture']} strategy with "
            f"{state['concentration_tendency']} allocation across asset classes "
            f"({weights_str}). "
            f"Liquidity preference is {state['liquidity_preference']} with an idle "
            f"capital ratio of {round(state['idle_capital_ratio'] * 100, 1)}%. "
            f"Capital turnover rate of {round(state['turnover_rate'] * 100, 1)}% "
            f"indicates {'active' if state['turnover_rate'] > 0.3 else 'passive'} repositioning behavior."
        )

    return {**state, "profile_text": profile_text}
