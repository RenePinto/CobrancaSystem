from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.report import SendHistoryResponse
from app.services import report_service

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=list[SendHistoryResponse])
def list_history(
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "operadora")),
):
    return report_service.list_history(db)
