from sqlalchemy import Column, String, Boolean

from models.base_model import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=True)
    lastname = Column(String, index=True, nullable=True)
    country = Column(String, nullable=True)
    province = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    street = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    extra_info = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
