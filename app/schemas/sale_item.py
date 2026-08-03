from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SaleItemBase(BaseModel):
    quantity: int
    unit_price: Decimal
    discount: Optional[Decimal] = 0
    line_total: Decimal
    sale_id: int
    product_id: int


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemResponse(SaleItemBase):
    sale_item_id: int

    model_config = ConfigDict(from_attributes=True)
