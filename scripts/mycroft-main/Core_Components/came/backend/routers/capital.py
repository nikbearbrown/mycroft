import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Event
from models.schemas import CapitalFlowOut, SimulateRequest, SimulateOut
from agent.analytics import (
    compute_hhi, compute_entropy, classify_risk_posture,
    reconstruct_portfolio_state
)

router = APIRouter(tags=["capital"])


@router.get("/capital-flow", response_model=CapitalFlowOut)
def capital_flow(db: Session = Depends(get_db)):
    """Build Sankey node/link data from event history."""
    events = db.query(Event).order_by(Event.timestamp.asc()).all()

    # Group flows: source (event_type bucket) -> target (asset_class)
    flow_map: dict = {}
    for e in events:
        src = _event_source_label(e.event_type.value if hasattr(e.event_type, "value") else e.event_type)
        tgt = e.asset_class
        key = (src, tgt)
        flow_map[key] = flow_map.get(key, 0) + e.amount

    # Build unique node list
    node_names = []
    for src, tgt in flow_map:
        if src not in node_names:
            node_names.append(src)
        if tgt not in node_names:
            node_names.append(tgt)

    node_idx = {n: i for i, n in enumerate(node_names)}

    nodes = [
        {"id": i, "name": n, "group": "action" if i < _count_sources(flow_map) else "asset"}
        for i, n in enumerate(node_names)
    ]
    links = [
        {"source": node_idx[src], "target": node_idx[tgt], "value": round(val, 2)}
        for (src, tgt), val in flow_map.items()
        if val > 0
    ]

    return CapitalFlowOut(nodes=nodes, links=links)


def _event_source_label(etype: str) -> str:
    mapping = {
        "INVESTMENT": "New Investment",
        "DIVESTMENT": "Divestment",
        "CASH_ALLOCATION": "Cash Allocation",
        "HOLD_DECISION": "Hold",
        "INACTION_MARKER": "Inaction",
    }
    return mapping.get(etype, etype)


def _count_sources(flow_map):
    return len({src for src, _ in flow_map})


@router.post("/simulate-allocation", response_model=SimulateOut)
def simulate_allocation(payload: SimulateRequest, db: Session = Depends(get_db)):
    """Simulate the effect of proposed events on strategy profile."""
    existing = db.query(Event).order_by(Event.timestamp.asc()).all()
    existing_dicts = [
        {"event_type": e.event_type.value if hasattr(e.event_type, "value") else e.event_type,
         "asset_class": e.asset_class, "amount": e.amount,
         "timestamp": e.timestamp.isoformat()}
        for e in existing
    ]
    proposed = [
        {"event_type": e.event_type.value if hasattr(e.event_type, "value") else e.event_type,
         "asset_class": e.asset_class.lower().replace(" ", "_"),
         "amount": abs(e.amount),
         "timestamp": e.timestamp.isoformat()}
        for e in payload.proposed_events
    ]

    combined = existing_dicts + proposed
    portfolio = reconstruct_portfolio_state(combined)
    total = sum(portfolio.values()) or 1
    weights = {k: round(v / total, 4) for k, v in portfolio.items()}

    hhi = compute_hhi(portfolio)
    entropy = compute_entropy(portfolio)
    equity_w = weights.get("equities", 0) + weights.get("stocks", 0)
    crypto_w = weights.get("crypto", 0)
    risk = classify_risk_posture(hhi, equity_w, crypto_w)

    narrative = (
        f"After applying {len(proposed)} proposed event(s), the projected portfolio would be "
        + ", ".join(f"{k}: {round(v*100,1)}%" for k, v in sorted(weights.items(), key=lambda x: -x[1]))
        + f". Concentration (HHI): {round(hhi,3)}, Diversification (entropy): {round(entropy,3)}. "
        + f"Projected risk posture: {risk}."
    )

    return SimulateOut(
        projected_weights=weights,
        projected_hhi=round(hhi, 4),
        projected_entropy=round(entropy, 4),
        projected_risk_posture=risk,
        narrative=narrative,
    )
