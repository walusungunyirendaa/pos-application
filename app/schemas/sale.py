from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SaleBase(BaseModel):
    sale_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Optional[Decimal] = 0
    total_amount: Decimal
    status: str = "Completed"
    customer_id: Optional[int] = None
    user_id: int


class SaleCreate(SaleBase):
    pass


class SaleResponse(SaleBase):
    sale_id: int

    model_config = ConfigDict(from_attributes=True)
