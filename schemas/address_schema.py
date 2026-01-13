"""Address schema for request/response validation."""
from typing import Optional
from pydantic import BaseModel, Field

from schemas.base_schema import BaseSchema


class AddressSchema(BaseSchema):
    """Schema for Address entity with validations."""

    street: Optional[str] = Field(None, min_length=1, max_length=200, description="Street name")
    number: Optional[str] = Field(None, max_length=20, description="Street number")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City name")
    country: Optional[str] = Field(None, min_length=1, max_length=100, description="Country name")
    province: Optional[str] = Field(None, min_length=1, max_length=100, description="Province name")
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20, description="Postal code")
    client_id: int = Field(..., description="Client ID reference (required)")


class AddressCreate(BaseModel):
    street: str = Field(..., min_length=1, max_length=200)
    number: Optional[str] = Field(None, max_length=20)
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    province: str = Field(..., min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)


class AddressUpdate(BaseModel):
    street: Optional[str] = Field(None, min_length=1, max_length=200)
    number: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    province: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)


class AddressPublic(BaseSchema):
    street: Optional[str] = None
    number: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
