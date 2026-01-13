from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models.base_model import BaseModel


class PaymentMethodModel(BaseModel):
    __tablename__ = "billing_methods"

    user_id = Column(Integer, ForeignKey("users.id_key"), index=True, nullable=False)
    brand = Column(String, nullable=False)
    last4 = Column(String, nullable=False)
    exp_month = Column(Integer, nullable=False)
    exp_year = Column(Integer, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    user = relationship("UserModel", lazy="select")
