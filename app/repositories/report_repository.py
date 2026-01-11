from sqlalchemy.orm import Session

from app.models import ReportSnapshot, SendHistory


def create_snapshot(db: Session, snapshot: ReportSnapshot) -> ReportSnapshot:
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def create_history(db: Session, history: SendHistory) -> SendHistory:
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def list_history(db: Session) -> list[SendHistory]:
    return db.query(SendHistory).order_by(SendHistory.sent_at.desc()).all()
