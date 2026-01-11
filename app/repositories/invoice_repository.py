from datetime import date
from sqlalchemy.orm import Session

from app.models import Invoice


def find_duplicate(
    db: Session,
    cliente: str,
    data_vencimento: date,
    valor_original,
    descricao: str,
    origem: str,
) -> Invoice | None:
    return (
        db.query(Invoice)
        .filter(
            Invoice.cliente == cliente,
            Invoice.data_vencimento == data_vencimento,
            Invoice.valor_original == valor_original,
            Invoice.descricao == descricao,
            Invoice.origem == origem,
        )
        .first()
    )


def create(db: Session, invoice: Invoice) -> Invoice:
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def list_overdue(db: Session, today: date) -> list[Invoice]:
    return db.query(Invoice).filter(Invoice.data_vencimento < today).all()
