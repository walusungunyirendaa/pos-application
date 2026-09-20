from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SaleItemBase(BaseModel):
    quantity: int
    unit_price: Decimal
    discount: Optional[Decimal] = Decimal("0")
    line_total: Decimal
    sale_id: int
    product_id: int


class SaleItemCreate(SaleItemBase):
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    line_total: Decimal = Field(ge=0)


class SaleItemResponse(SaleItemBase):
    sale_item_id: int

    model_config = ConfigDict(from_attributes=True)