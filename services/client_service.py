from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models.client import ClientModel
from repositories.client_repository import ClientRepository
from schemas.client_schema import ClientSchema
from services.base_service_impl import BaseServiceImpl


class ClientService(BaseServiceImpl):
    def __init__(self, db: Session):
        super().__init__(
            repository_class=ClientRepository,
            model=ClientModel,
            schema=ClientSchema,
            db=db
        )

    def save(self, schema: ClientSchema) -> ClientSchema:
        email = schema.email
        if email:
            existing = self.repository.get_by_email(email)
            if existing:
                return self.schema.model_validate(existing)
        try:
            return super().save(schema)
        except IntegrityError:
            if email:
                existing = self.repository.get_by_email(email)
                if existing:
                    return self.schema.model_validate(existing)
            raise
