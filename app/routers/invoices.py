from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.invoice import InvoiceUploadSummary
from app.services import invoice_service
from app.utils.excel_parsers import ExcelParseError

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/upload/itau", response_model=InvoiceUploadSummary)
def upload_itau(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "operadora")),
):
    try:
        content = file.file.read()
        inserted, skipped_invalid, skipped_duplicates = invoice_service.upload_itau(db, content)
        return InvoiceUploadSummary(
            inserted=inserted,
            skipped_invalid=skipped_invalid,
            skipped_duplicates=skipped_duplicates,
        )
    except ExcelParseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/upload/conta-azul", response_model=InvoiceUploadSummary)
def upload_conta_azul(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "operadora")),
):
    try:
        content = file.file.read()
        inserted, skipped_invalid, skipped_duplicates = invoice_service.upload_conta_azul(
            db, content
        )
        return InvoiceUploadSummary(
            inserted=inserted,
            skipped_invalid=skipped_invalid,
            skipped_duplicates=skipped_duplicates,
        )
    except ExcelParseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
