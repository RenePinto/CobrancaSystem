from datetime import date

from sqlalchemy.orm import Session

from app.models import ReportSnapshot, SendHistory
from app.repositories import invoice_repository, report_repository


def create_snapshot(
    db: Session,
    report_type: str,
    recipient_type: str,
    method: str,
    recipient_value: str | None,
) -> ReportSnapshot:
    today = date.today()
    invoices = invoice_repository.list_overdue(db, today)
    data_json = [
        {
            "cliente": invoice.cliente,
            "data_vencimento": str(invoice.data_vencimento),
            "descricao": invoice.descricao,
            "valor_original": float(invoice.valor_original),
            "vendedor": invoice.vendedor,
            "origem": invoice.origem,
        }
        for invoice in invoices
    ]
    snapshot = ReportSnapshot(
        report_type=report_type,
        recipient_type=recipient_type,
        method=method,
        data_json=data_json,
        filters_json={"only_overdue": True},
    )
    snapshot = report_repository.create_snapshot(db, snapshot)

    history = SendHistory(
        recipient_type=recipient_type,
        recipient_value=recipient_value,
        report_type=report_type,
        method=method,
        snapshot_id=snapshot.id,
    )
    report_repository.create_history(db, history)
    return snapshot


def list_history(db: Session) -> list[SendHistory]:
    return report_repository.list_history(db)
