from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


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
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    price: Decimal = Field(ge=0)
    cost_price: Optional[Decimal] = Field(default=None, ge=0)
    quantity_in_stock: int = Field(default=0, ge=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)


class ProductResponse(ProductBase):
    product_id: int

    model_config = ConfigDict(from_attributes=True)