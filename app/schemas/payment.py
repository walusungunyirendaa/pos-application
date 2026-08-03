from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    payment_method: str
    amount: Decimal
    payment_date: datetime
    transaction_reference: Optional[str] = None
    status: str = "Approved"
    sale_id: int


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    payment_id: int

    model_config = ConfigDict(from_attributes=True)
