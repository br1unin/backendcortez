from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.auth_controller import get_current_user
from models.client import ClientModel
from models.order import OrderModel
from models.order_detail import OrderDetailModel
from models.product import ProductModel
from schemas.auth_schema import UserPublic
from schemas.order_history_schema import OrderPublic, OrderItemPublic

router = APIRouter(tags=["Orders"])


@router.get("/me", response_model=List[OrderPublic])
def my_orders(
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    stmt = (
        select(OrderModel, OrderDetailModel, ProductModel)
        .join(ClientModel, OrderModel.client_id == ClientModel.id_key)
        .join(OrderDetailModel, OrderDetailModel.order_id == OrderModel.id_key)
        .join(ProductModel, ProductModel.id_key == OrderDetailModel.product_id)
        .where(ClientModel.email == current_user.email)
        .order_by(OrderModel.date.desc())
    )
    rows = db.execute(stmt).all()

    by_order: dict[int, OrderPublic] = {}
    for order, detail, product in rows:
        if order.id_key not in by_order:
            by_order[order.id_key] = OrderPublic(
                id_key=order.id_key,
                date=order.date,
                total=order.total,
                status=str(order.status) if order.status else None,
                items=[],
            )
        by_order[order.id_key].items.append(
            OrderItemPublic(
                product_id=detail.product_id,
                name=product.name,
                quantity=int(detail.quantity or 0),
                unit_price=float(detail.price or 0),
            )
        )

    return list(by_order.values())
