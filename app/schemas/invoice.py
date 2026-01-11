from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class InvoiceResponse(BaseModel):
    id: int
    cliente: str
    data_vencimento: date
    descricao: str
    valor_original: Decimal
    vendedor: str
    origem: str

    class Config:
        orm_mode = True


class InvoiceUploadSummary(BaseModel):
    inserted: int
    skipped_invalid: int
    skipped_duplicates: int
