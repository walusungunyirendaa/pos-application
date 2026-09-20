from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    category_name: str = Field(min_length=1)


class CategoryResponse(CategoryBase):
    category_id: int

    model_config = ConfigDict(from_attributes=True)