from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import BehaviorFeature
from models.schemas import BehaviorFeatureOut

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=list[BehaviorFeatureOut])
def list_metrics(limit: int = 50, db: Session = Depends(get_db)):
    rows = (
        db.query(BehaviorFeature)
        .order_by(BehaviorFeature.window_end.desc())
        .limit(limit)
        .all()
    )
    return [
        BehaviorFeatureOut(
            id=r.id, window_start=r.window_start, window_end=r.window_end,
            hhi=r.hhi, entropy=r.entropy, turnover_rate=r.turnover_rate,
            idle_capital_ratio=r.idle_capital_ratio, dominant_action=r.dominant_action,
            asset_class_weights=r.asset_class_weights or {},
        )
        for r in rows
    ]
