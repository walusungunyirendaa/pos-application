from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SupplierBase(BaseModel):
    supplier_name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    supplier_name: str = Field(min_length=1)
    phone: str = Field(min_length=1)


class SupplierResponse(SupplierBase):
    supplier_id: int

    model_config = ConfigDict(from_attributes=True)