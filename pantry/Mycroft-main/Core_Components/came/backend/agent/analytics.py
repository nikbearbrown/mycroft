import math
from typing import Dict, List, Any


def compute_hhi(weights: Dict[str, float]) -> float:
    """Herfindahl-Hirschman Index. 1.0 = fully concentrated, ~0 = fully diversified."""
    if not weights:
        return 0.0
    total = sum(weights.values())
    if total == 0:
        return 0.0
    shares = [v / total for v in weights.values()]
    return sum(s ** 2 for s in shares)


def compute_entropy(weights: Dict[str, float]) -> float:
    """Shannon entropy. Higher = more diversified."""
    if not weights:
        return 0.0
    total = sum(weights.values())
    if total == 0:
        return 0.0
    shares = [v / total for v in weights.values() if v > 0]
    return -sum(s * math.log2(s) for s in shares)


def compute_turnover_rate(events: List[Dict[str, Any]], total_value: float) -> float:
    """Sum of buy+sell volumes / total AUM. Higher = more active repositioning."""
    if total_value == 0:
        return 0.0
    active_volume = sum(
        abs(e["amount"])
        for e in events
        if e["event_type"] in ("INVESTMENT", "DIVESTMENT")
    )
    return active_volume / total_value if total_value > 0 else 0.0


def compute_idle_capital_ratio(weights: Dict[str, float]) -> float:
    """Cash + cash equivalents / total. Proxy for deployment hesitancy."""
    total = sum(weights.values())
    if total == 0:
        return 0.0
    cash = weights.get("cash", 0.0) + weights.get("money_market", 0.0)
    return cash / total


def classify_risk_posture(hhi: float, equity_weight: float, crypto_weight: float) -> str:
    high_risk_exposure = equity_weight + crypto_weight
    if high_risk_exposure > 0.75 and hhi < 0.4:
        return "aggressive"
    elif high_risk_exposure > 0.5:
        return "moderate-aggressive"
    elif high_risk_exposure > 0.3:
        return "moderate"
    else:
        return "conservative"


def classify_liquidity_preference(idle_ratio: float) -> str:
    if idle_ratio > 0.3:
        return "high"
    elif idle_ratio > 0.1:
        return "medium"
    else:
        return "low"


def classify_concentration(hhi: float) -> str:
    if hhi > 0.6:
        return "highly concentrated"
    elif hhi > 0.35:
        return "moderately concentrated"
    else:
        return "well diversified"


def compute_drift_score(current: Dict[str, float], baseline: Dict[str, float]) -> Dict:
    """L1 distance between normalized weight vectors."""
    if not baseline:
        return {"score": 0.0, "deltas": {}}

    all_classes = set(current) | set(baseline)
    c_total = sum(current.values()) or 1
    b_total = sum(baseline.values()) or 1

    c_norm = {k: current.get(k, 0) / c_total for k in all_classes}
    b_norm = {k: baseline.get(k, 0) / b_total for k in all_classes}

    deltas = {k: c_norm[k] - b_norm[k] for k in all_classes}
    l1 = sum(abs(v) for v in deltas.values()) / 2  # normalize to [0,1]

    return {"score": round(l1, 4), "deltas": {k: round(v, 4) for k, v in deltas.items()}}


def reconstruct_portfolio_state(events: List[Dict[str, Any]]) -> Dict[str, float]:
    """Replay events to get current allocation by asset class."""
    state: Dict[str, float] = {}
    for e in sorted(events, key=lambda x: x["timestamp"]):
        ac = e["asset_class"]
        amount = e["amount"]
        etype = e["event_type"]
        if etype in ("INVESTMENT", "CASH_ALLOCATION"):
            state[ac] = state.get(ac, 0.0) + amount
        elif etype == "DIVESTMENT":
            state[ac] = max(0.0, state.get(ac, 0.0) - amount)
        # HOLD_DECISION and INACTION_MARKER don't change state
    return {k: v for k, v in state.items() if v > 0}
