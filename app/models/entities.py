from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    role = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    totp_secret = Column(String(32), nullable=True)
    is_2fa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint(
            "cliente",
            "data_vencimento",
            "valor_original",
            "descricao",
            "origem",
            name="uq_invoice_dedup",
        ),
        CheckConstraint("valor_original > 0", name="ck_invoice_value_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(150), nullable=False)
    data_vencimento = Column(Date, nullable=False, index=True)
    descricao = Column(String(255), nullable=False)
    valor_original = Column(Numeric(12, 2), nullable=False)
    vendedor = Column(String(150), nullable=False)
    origem = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReportSnapshot(Base):
    __tablename__ = "report_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50), nullable=False)
    recipient_type = Column(String(50), nullable=False)
    method = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    filters_json = Column(JSONB, nullable=True)
    data_json = Column(JSONB, nullable=False)

    histories = relationship("SendHistory", back_populates="snapshot")


class SendHistory(Base):
    __tablename__ = "send_history"

    id = Column(Integer, primary_key=True, index=True)
    recipient_type = Column(Enum("DIRETORIA", "VENDEDOR", name="recipient_type"), nullable=False)
    recipient_value = Column(String(150), nullable=True)
    report_type = Column(String(50), nullable=False)
    method = Column(Enum("EXPORT", "WHATSAPP", name="send_method"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    snapshot_id = Column(Integer, ForeignKey("report_snapshots.id"), nullable=False)

    snapshot = relationship("ReportSnapshot", back_populates="histories")
