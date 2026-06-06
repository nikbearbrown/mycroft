import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Event, StrategyModel, BehaviorFeature
from models.schemas import StrategyOut, DriftOut
from agent.graph import came_graph

router = APIRouter(prefix="/strategy", tags=["strategy"])


def _events_to_dicts(events):
    return [
        {
            "id": e.id,
            "event_type": e.event_type.value if hasattr(e.event_type, "value") else e.event_type,
            "asset_class": e.asset_class,
            "ticker": e.ticker,
            "amount": e.amount,
            "timestamp": e.timestamp.isoformat(),
            "notes": e.notes,
        }
        for e in events
    ]


def _get_baseline(db: Session):
    prev = (
        db.query(StrategyModel)
        .filter(StrategyModel.is_current == 0)
        .order_by(StrategyModel.computed_at.desc())
        .first()
    )
    return prev.baseline_weights if prev else {}


@router.post("/compute", response_model=StrategyOut)
def compute_strategy(db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.timestamp.asc()).all()
    if not events:
        raise HTTPException(status_code=400, detail="No events found. Ingest events first.")

    # Mark existing current as historical
    db.query(StrategyModel).filter(StrategyModel.is_current == 1).update({"is_current": 0})

    baseline = _get_baseline(db)

    result = came_graph.invoke({
        "events": _events_to_dicts(events),
        "snapshots": [],
        "baseline_weights": baseline,
    })

    # Persist behavior features
    feat = BehaviorFeature(
        id=str(uuid.uuid4()),
        window_start=events[0].timestamp,
        window_end=events[-1].timestamp,
        hhi=result["hhi"],
        entropy=result["entropy"],
        turnover_rate=result["turnover_rate"],
        idle_capital_ratio=result["idle_capital_ratio"],
        dominant_action=result["dominant_action"],
        asset_class_weights=result["asset_class_weights"],
    )
    db.add(feat)

    # Persist strategy model
    prev_version = (
        db.query(StrategyModel).order_by(StrategyModel.version.desc()).first()
    )
    version = (prev_version.version + 1) if prev_version else 1

    model = StrategyModel(
        id=str(uuid.uuid4()),
        version=version,
        computed_at=datetime.utcnow(),
        profile_text=result["profile_text"],
        risk_posture=result["risk_posture"],
        liquidity_preference=result["liquidity_preference"],
        concentration_tendency=result["concentration_tendency"],
        baseline_weights=result["asset_class_weights"],
        metrics_snapshot={
            "hhi": result["hhi"],
            "entropy": result["entropy"],
            "turnover_rate": result["turnover_rate"],
            "idle_capital_ratio": result["idle_capital_ratio"],
            "drift_score": result.get("drift_score", 0.0),
        },
        is_current=1,
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    return StrategyOut(
        id=model.id, version=model.version, computed_at=model.computed_at,
        profile_text=model.profile_text, risk_posture=model.risk_posture,
        liquidity_preference=model.liquidity_preference,
        concentration_tendency=model.concentration_tendency,
        baseline_weights=model.baseline_weights,
        metrics_snapshot=model.metrics_snapshot,
    )


@router.get("/current", response_model=StrategyOut)
def get_current_strategy(db: Session = Depends(get_db)):
    model = (
        db.query(StrategyModel)
        .filter(StrategyModel.is_current == 1)
        .order_by(StrategyModel.computed_at.desc())
        .first()
    )
    if not model:
        raise HTTPException(status_code=404, detail="No strategy computed yet. POST /strategy/compute first.")
    return StrategyOut(
        id=model.id, version=model.version, computed_at=model.computed_at,
        profile_text=model.profile_text, risk_posture=model.risk_posture,
        liquidity_preference=model.liquidity_preference,
        concentration_tendency=model.concentration_tendency,
        baseline_weights=model.baseline_weights,
        metrics_snapshot=model.metrics_snapshot,
    )


@router.get("/history", response_model=list[StrategyOut])
def strategy_history(db: Session = Depends(get_db)):
    rows = db.query(StrategyModel).order_by(StrategyModel.computed_at.desc()).limit(20).all()
    return [
        StrategyOut(
            id=r.id, version=r.version, computed_at=r.computed_at,
            profile_text=r.profile_text, risk_posture=r.risk_posture,
            liquidity_preference=r.liquidity_preference,
            concentration_tendency=r.concentration_tendency,
            baseline_weights=r.baseline_weights,
            metrics_snapshot=r.metrics_snapshot,
        )
        for r in rows
    ]


@router.get("/drift", response_model=DriftOut)
def get_drift(db: Session = Depends(get_db)):
    current = (
        db.query(StrategyModel)
        .filter(StrategyModel.is_current == 1)
        .first()
    )
    if not current:
        raise HTTPException(status_code=404, detail="No current strategy.")

    prev = (
        db.query(StrategyModel)
        .filter(StrategyModel.is_current == 0)
        .order_by(StrategyModel.computed_at.desc())
        .first()
    )

    current_w = current.baseline_weights or {}
    baseline_w = prev.baseline_weights if prev else {}
    drift_score = current.metrics_snapshot.get("drift_score", 0.0)
    deltas = {}

    if baseline_w:
        all_classes = set(current_w) | set(baseline_w)
        c_total = sum(current_w.values()) or 1
        b_total = sum(baseline_w.values()) or 1
        c_norm = {k: current_w.get(k, 0) / c_total for k in all_classes}
        b_norm = {k: baseline_w.get(k, 0) / b_total for k in all_classes}
        deltas = {k: round(c_norm[k] - b_norm[k], 4) for k in all_classes}

    dominant_shift = max(deltas, key=lambda k: abs(deltas[k])) if deltas else None

    if drift_score < 0.1:
        narrative = "Allocation behavior is consistent with the prior strategy baseline. No significant drift detected."
    elif drift_score < 0.25:
        narrative = f"Minor drift detected (score: {drift_score:.2f}). The largest shift is in {dominant_shift or 'unknown'} allocation."
    else:
        narrative = f"Significant strategy drift detected (score: {drift_score:.2f}). Behavior has meaningfully diverged from the prior baseline, most notably in {dominant_shift or 'unknown'}."

    return DriftOut(
        has_baseline=bool(baseline_w),
        drift_score=drift_score,
        current_weights=current_w,
        baseline_weights=baseline_w,
        weight_deltas=deltas,
        dominant_shift=dominant_shift,
        drift_narrative=narrative,
    )
