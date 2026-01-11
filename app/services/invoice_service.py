from datetime import date
from decimal import Decimal
from typing import Iterable

from sqlalchemy.orm import Session

from app.models import Invoice
from app.repositories import invoice_repository
from app.utils.excel_parsers import ExcelParseError, parse_conta_azul, parse_itau


class InvoiceValidationError(Exception):
    pass


def _is_valid(row: dict, today: date) -> bool:
    if not row.get("cliente") or not row.get("descricao") or not row.get("vendedor"):
        return False
    if not row.get("data_vencimento") or row["data_vencimento"] >= today:
        return False
    if Decimal(row.get("valor_original", 0)) <= 0:
        return False
    return True


def _save_invoices(db: Session, rows: Iterable[dict]) -> tuple[int, int, int]:
    inserted = 0
    skipped_invalid = 0
    skipped_duplicates = 0
    today = date.today()

    for row in rows:
        if not _is_valid(row, today):
            skipped_invalid += 1
            continue
        duplicate = invoice_repository.find_duplicate(
            db,
            cliente=row["cliente"],
            data_vencimento=row["data_vencimento"],
            valor_original=row["valor_original"],
            descricao=row["descricao"],
            origem=row["origem"],
        )
        if duplicate:
            skipped_duplicates += 1
            continue
        invoice = Invoice(**row)
        invoice_repository.create(db, invoice)
        inserted += 1

    return inserted, skipped_invalid, skipped_duplicates


def upload_itau(db: Session, content: bytes) -> tuple[int, int, int]:
    rows = parse_itau(content)
    return _save_invoices(db, rows)


def upload_conta_azul(db: Session, content: bytes) -> tuple[int, int, int]:
    rows = parse_conta_azul(content)
    return _save_invoices(db, rows)
