import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Event
from models.schemas import EventCreate, EventOut

router = APIRouter(prefix="/event", tags=["events"])


@router.post("", response_model=EventOut)
def ingest_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(
        id=str(uuid.uuid4()),
        event_type=payload.event_type,
        asset_class=payload.asset_class.lower().replace(" ", "_"),
        ticker=payload.ticker,
        amount=abs(payload.amount),
        timestamp=payload.timestamp,
        notes=payload.notes,
        metadata_=payload.metadata or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventOut(
        id=event.id,
        event_type=event.event_type,
        asset_class=event.asset_class,
        ticker=event.ticker,
        amount=event.amount,
        timestamp=event.timestamp,
        notes=event.notes,
        metadata=event.metadata_,
        created_at=event.created_at,
    )


@router.get("", response_model=list[EventOut])
def list_events(limit: int = 200, db: Session = Depends(get_db)):
    rows = db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()
    return [
        EventOut(
            id=r.id, event_type=r.event_type, asset_class=r.asset_class,
            ticker=r.ticker, amount=r.amount, timestamp=r.timestamp,
            notes=r.notes, metadata=r.metadata_ or {}, created_at=r.created_at,
        )
        for r in rows
    ]


@router.delete("/{event_id}")
def delete_event(event_id: str, db: Session = Depends(get_db)):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(ev)
    db.commit()
    return {"deleted": event_id}
