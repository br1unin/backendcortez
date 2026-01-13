from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from schemas.base_schema import BaseSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)


class UserPublic(BaseSchema):
    email: EmailStr
    name: Optional[str] = None
    lastname: Optional[str] = None
    country: Optional[str] = None
    province: Optional[str] = None
    locality: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    extra_info: Optional[str] = None
    is_active: bool
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    country: Optional[str] = Field(None, min_length=1, max_length=120)
    province: Optional[str] = Field(None, min_length=1, max_length=120)
    locality: Optional[str] = Field(None, min_length=1, max_length=120)
    street: Optional[str] = Field(None, min_length=1, max_length=200)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    extra_info: Optional[str] = Field(None, max_length=500)
