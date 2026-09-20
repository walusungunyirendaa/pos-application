from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str
    full_name: str
    role: str
    email: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    username: str = Field(min_length=1)
    full_name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    password: str = Field(min_length=1)
    
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserResponse(UserBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)