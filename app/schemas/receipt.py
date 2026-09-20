from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReceiptBase(BaseModel):
    receipt_number: str
    issued_date: datetime
    file_url: Optional[str] = None
    sale_id: int


class ReceiptCreate(ReceiptBase):
    receipt_number: str = Field(min_length=1)


class ReceiptResponse(ReceiptBase):
    receipt_id: int

    model_config = ConfigDict(from_attributes=True)