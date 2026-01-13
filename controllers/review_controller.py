from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.auth_controller import get_current_user, get_current_admin
from models.order_detail import OrderDetailModel
from models.order import OrderModel
from models.client import ClientModel
from models.review import ReviewModel
from models.user import UserModel
from repositories.user_repository import UserRepository
from schemas.auth_schema import UserPublic
from schemas.review_schema import ReviewCreate, ReviewPublic, ReviewSummary, ReviewUpdate

router = APIRouter(tags=["Reviews"])


def _user_purchased_product(db: Session, user_email: str, product_id: int) -> bool:
    stmt = (
        select(OrderDetailModel.id_key)
        .join(OrderModel, OrderDetailModel.order_id == OrderModel.id_key)
        .join(ClientModel, OrderModel.client_id == ClientModel.id_key)
        .where(
            OrderDetailModel.product_id == product_id,
            ClientModel.email == user_email,
        )
        .limit(1)
    )
    return db.execute(stmt).first() is not None


@router.get("/product/{product_id}", response_model=List[ReviewPublic])
def list_by_product(product_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(ReviewModel, UserModel)
        .join(UserModel, ReviewModel.user_id == UserModel.id_key)
        .where(ReviewModel.product_id == product_id)
    )
    rows = db.execute(stmt).all()
    result: List[ReviewPublic] = []
    for review, user in rows:
        name = (user.name or "").strip()
        lastname = (user.lastname or "").strip()
        label = " ".join([n for n in [name, lastname] if n]).strip() or user.email
        data = ReviewPublic.model_validate(review)
        data.user_name = label
        result.append(data)
    return result


@router.get("/summary", response_model=List[ReviewSummary])
def summary(db: Session = Depends(get_db)):
    stmt = (
        select(
            ReviewModel.product_id,
            func.avg(ReviewModel.rating).label("avg_rating"),
            func.count(ReviewModel.id_key).label("count"),
        )
        .group_by(ReviewModel.product_id)
    )
    rows = db.execute(stmt).all()
    return [
        ReviewSummary(
            product_id=product_id,
            avg_rating=float(avg_rating or 0),
            count=int(count or 0),
        )
        for product_id, avg_rating, count in rows
    ]


@router.post("/", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    repo = UserRepository(db)
    user = repo.get_by_id(current_user.id_key)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado.")

    if not user.is_admin and not _user_purchased_product(db, user.email, payload.product_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo podes dejar review si compraste el producto.",
        )

    existing = db.scalars(
        select(ReviewModel).where(
            ReviewModel.product_id == payload.product_id,
            ReviewModel.user_id == user.id_key,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya dejaste una review.")

    review = ReviewModel(
        rating=payload.rating,
        comment=payload.comment,
        product_id=payload.product_id,
        user_id=user.id_key,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    data = ReviewPublic.model_validate(review)
    name = (user.name or "").strip()
    lastname = (user.lastname or "").strip()
    data.user_name = " ".join([n for n in [name, lastname] if n]).strip() or user.email
    return data


@router.get("/me", response_model=List[ReviewPublic])
def my_reviews(
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    stmt = (
        select(ReviewModel, UserModel)
        .join(UserModel, ReviewModel.user_id == UserModel.id_key)
        .where(ReviewModel.user_id == current_user.id_key)
    )
    rows = db.execute(stmt).all()
    result: List[ReviewPublic] = []
    for review, user in rows:
        name = (user.name or "").strip()
        lastname = (user.lastname or "").strip()
        label = " ".join([n for n in [name, lastname] if n]).strip() or user.email
        data = ReviewPublic.model_validate(review)
        data.user_name = label
        result.append(data)
    return result


@router.put("/{review_id}", response_model=ReviewPublic)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_admin),
):
    review = db.get(ReviewModel, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review no encontrada.")

    changes = payload.model_dump(exclude_unset=True)
    if "comment" in changes and not changes["comment"]:
        changes["comment"] = None

    for key, value in changes.items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    return ReviewPublic.model_validate(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_admin),
):
    review = db.get(ReviewModel, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review no encontrada.")

    db.delete(review)
    db.commit()
    return None
@router.get("/", response_model=List[ReviewPublic])
def list_all(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_admin),
):
    stmt = (
        select(ReviewModel, UserModel)
        .join(UserModel, ReviewModel.user_id == UserModel.id_key)
        .offset(skip)
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    result: List[ReviewPublic] = []
    for review, user in rows:
        name = (user.name or "").strip()
        lastname = (user.lastname or "").strip()
        label = " ".join([n for n in [name, lastname] if n]).strip() or user.email
        data = ReviewPublic.model_validate(review)
        data.user_name = label
        result.append(data)
    return result
