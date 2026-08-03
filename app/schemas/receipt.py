from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ReceiptBase(BaseModel):
    receipt_number: str
    issued_date: datetime
    file_url: Optional[str] = None
    sale_id: int


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptResponse(ReceiptBase):
    receipt_id: int

    model_config = ConfigDict(from_attributes=True)
