from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    payment_method: str
    amount: Decimal
    payment_date: datetime
    transaction_reference: Optional[str] = None
    status: str = "Approved"
    sale_id: int


class PaymentCreate(PaymentBase):
    payment_method: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)


class PaymentResponse(PaymentBase):
    payment_id: int

    model_config = ConfigDict(from_attributes=True)