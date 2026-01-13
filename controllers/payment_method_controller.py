from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.auth_controller import get_current_user
from models.payment_method import PaymentMethodModel
from schemas.auth_schema import UserPublic
from schemas.payment_method_schema import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodPublic,
)

router = APIRouter(tags=["BillingMethods"])


def _validate_exp(exp_month: int, exp_year: int):
    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month
    if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tarjeta esta vencida.",
        )


@router.get("/", response_model=List[PaymentMethodPublic])
def list_methods(
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    stmt = select(PaymentMethodModel).where(PaymentMethodModel.user_id == current_user.id_key)
    methods = db.scalars(stmt).all()
    return [PaymentMethodPublic.model_validate(m) for m in methods]


@router.post("/", response_model=PaymentMethodPublic, status_code=status.HTTP_201_CREATED)
def create_method(
    payload: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    if not payload.last4.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Last4 invalido.")
    _validate_exp(payload.exp_month, payload.exp_year)

    if payload.is_default:
        db.execute(
            update(PaymentMethodModel)
            .where(PaymentMethodModel.user_id == current_user.id_key)
            .values(is_default=False)
        )

    model = PaymentMethodModel(
        user_id=current_user.id_key,
        brand=payload.brand.strip(),
        last4=payload.last4,
        exp_month=payload.exp_month,
        exp_year=payload.exp_year,
        is_default=bool(payload.is_default),
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return PaymentMethodPublic.model_validate(model)


@router.put("/{id_key}", response_model=PaymentMethodPublic)
def update_method(
    id_key: int,
    payload: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    stmt = select(PaymentMethodModel).where(
        PaymentMethodModel.id_key == id_key,
        PaymentMethodModel.user_id == current_user.id_key,
    )
    method = db.scalars(stmt).first()
    if not method:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metodo no encontrado.")

    data = payload.model_dump(exclude_unset=True)
    if "last4" in data and data["last4"] and not data["last4"].isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Last4 invalido.")

    exp_month = data.get("exp_month", method.exp_month)
    exp_year = data.get("exp_year", method.exp_year)
    _validate_exp(exp_month, exp_year)

    if data.get("is_default"):
        db.execute(
            update(PaymentMethodModel)
            .where(PaymentMethodModel.user_id == current_user.id_key)
            .values(is_default=False)
        )

    for key, value in data.items():
        setattr(method, key, value)

    db.commit()
    db.refresh(method)
    return PaymentMethodPublic.model_validate(method)


@router.delete("/{id_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_method(
    id_key: int,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    stmt = select(PaymentMethodModel).where(
        PaymentMethodModel.id_key == id_key,
        PaymentMethodModel.user_id == current_user.id_key,
    )
    method = db.scalars(stmt).first()
    if not method:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metodo no encontrado.")

    db.delete(method)
    db.commit()
    return None
