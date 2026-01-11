from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ReportSnapshotCreate(BaseModel):
    report_type: str = Field(..., examples=["vencidos"])
    recipient_type: str = Field(..., examples=["DIRETORIA", "VENDEDOR"])
    method: str = Field(..., examples=["EXPORT", "WHATSAPP"])
    recipient_value: str | None = Field(default=None, examples=["Equipe Sul"])


class ReportSnapshotResponse(BaseModel):
    id: int
    report_type: str
    recipient_type: str
    method: str
    created_at: datetime
    data_json: list[dict[str, Any]]

    class Config:
        orm_mode = True


class SendHistoryResponse(BaseModel):
    id: int
    recipient_type: str
    recipient_value: str | None
    report_type: str
    method: str
    sent_at: datetime
    snapshot_id: int

    class Config:
        orm_mode = True
