from typing import Optional
from pydantic import BaseModel, Field

from schemas.base_schema import BaseSchema


class PaymentMethodCreate(BaseModel):
    brand: str = Field(..., min_length=1, max_length=30)
    last4: str = Field(..., min_length=4, max_length=4)
    exp_month: int = Field(..., ge=1, le=12)
    exp_year: int = Field(..., ge=2020, le=2100)
    is_default: Optional[bool] = False


class PaymentMethodUpdate(BaseModel):
    brand: Optional[str] = Field(None, min_length=1, max_length=30)
    last4: Optional[str] = Field(None, min_length=4, max_length=4)
    exp_month: Optional[int] = Field(None, ge=1, le=12)
    exp_year: Optional[int] = Field(None, ge=2020, le=2100)
    is_default: Optional[bool] = None


class PaymentMethodPublic(BaseSchema):
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    is_default: bool
