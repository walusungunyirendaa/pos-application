from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    loyalty_points: Optional[int] = 0


class CustomerCreate(CustomerBase):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    loyalty_points: Optional[int] = Field(default=0, ge=0)


class CustomerResponse(CustomerBase):
    customer_id: int

    model_config = ConfigDict(from_attributes=True)