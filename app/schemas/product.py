from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    sku: str
    name: str
    price: Decimal
    cost_price: Optional[Decimal] = None
    quantity_in_stock: int = 0
    reorder_level: Optional[int] = None
    is_active: bool = True
    category_id: int
    supplier_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    product_id: int

    model_config = ConfigDict(from_attributes=True)
