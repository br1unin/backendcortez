from sqlalchemy.orm import Session
from sqlalchemy import select

from models.user import UserModel
from repositories.base_repository_impl import BaseRepositoryImpl
from schemas.auth_schema import UserPublic


class UserRepository(BaseRepositoryImpl):
    def __init__(self, db: Session):
        super().__init__(UserModel, UserPublic, db)

    def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        return self.session.scalars(stmt).first()

    def get_by_id(self, id_key: int) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id_key == id_key)
        return self.session.scalars(stmt).first()
