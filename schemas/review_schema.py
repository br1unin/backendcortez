from typing import Optional
from pydantic import BaseModel, Field

from schemas.base_schema import BaseSchema


class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, min_length=10, max_length=1000)
    product_id: int = Field(..., description="Product ID reference (required)")


class ReviewPublic(BaseSchema):
    rating: float
    comment: Optional[str] = None
    product_id: int
    user_id: int
    user_name: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewSummary(BaseModel):
    product_id: int
    avg_rating: float
    count: int
