from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.report import ReportSnapshotCreate, ReportSnapshotResponse
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/snapshot", response_model=ReportSnapshotResponse)
def create_snapshot(
    payload: ReportSnapshotCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "operadora")),
):
    snapshot = report_service.create_snapshot(
        db,
        report_type=payload.report_type,
        recipient_type=payload.recipient_type,
        method=payload.method,
        recipient_value=payload.recipient_value,
    )
    return snapshot
