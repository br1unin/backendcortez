from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.auth_controller import get_current_user
from models.address import AddressModel
from models.client import ClientModel
from repositories.client_repository import ClientRepository
from schemas.address_schema import AddressCreate, AddressPublic, AddressUpdate
from schemas.auth_schema import UserPublic

router = APIRouter(tags=["Addresses"])


def get_or_create_client(db: Session, user: UserPublic) -> ClientModel:
    repo = ClientRepository(db)
    existing = repo.get_by_email(user.email)
    if existing:
        return existing

    client = ClientModel(
        name=user.name,
        lastname=user.lastname,
        email=user.email,
        telephone=None,
    )
    repo.session.add(client)
    repo.session.commit()
    repo.session.refresh(client)
    return client


@router.get("/me", response_model=List[AddressPublic])
def list_my_addresses(
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    client = get_or_create_client(db, current_user)
    stmt = select(AddressModel).where(AddressModel.client_id == client.id_key)
    addresses = db.scalars(stmt).all()
    return [AddressPublic.model_validate(a) for a in addresses]


@router.post("/me", response_model=AddressPublic, status_code=status.HTTP_201_CREATED)
def create_my_address(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    client = get_or_create_client(db, current_user)
    model = AddressModel(
        street=payload.street,
        number=payload.number,
        city=payload.city,
        country=payload.country,
        province=payload.province,
        postal_code=payload.postal_code,
        client_id=client.id_key,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return AddressPublic.model_validate(model)


@router.put("/me/{id_key}", response_model=AddressPublic)
def update_my_address(
    id_key: int,
    payload: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    client = get_or_create_client(db, current_user)
    stmt = select(AddressModel).where(
        AddressModel.id_key == id_key,
        AddressModel.client_id == client.id_key,
    )
    model = db.scalars(stmt).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada.")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(model, key, value)

    db.commit()
    db.refresh(model)
    return AddressPublic.model_validate(model)


@router.delete("/me/{id_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_address(
    id_key: int,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    client = get_or_create_client(db, current_user)
    stmt = select(AddressModel).where(
        AddressModel.id_key == id_key,
        AddressModel.client_id == client.id_key,
    )
    model = db.scalars(stmt).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada.")

    db.delete(model)
    db.commit()
    return None
