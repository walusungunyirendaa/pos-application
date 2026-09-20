from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SaleBase(BaseModel):
    sale_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Optional[Decimal] = Decimal("0")
    total_amount: Decimal
    status: str = "Completed"
    customer_id: Optional[int] = None
    user_id: int


class SaleCreate(SaleBase):
    subtotal: Decimal = Field(ge=0)
    tax_amount: Decimal = Field(ge=0)
    discount_amount: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    total_amount: Decimal = Field(ge=0)
    status: str = Field(default="Completed", min_length=1)


class SaleResponse(SaleBase):
    sale_id: int

    model_config = ConfigDict(from_attributes=True)