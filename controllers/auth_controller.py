from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from config.database import get_db
from models.user import UserModel
from repositories.user_repository import UserRepository
from schemas.auth_schema import UserCreate, UserLogin, UserPublic, Token, UserUpdate
from utils.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(tags=["Auth"])


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> UserPublic:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido.")
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    repo = UserRepository(db)
    user = repo.get_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado.")
    return UserPublic.model_validate(user)


def get_current_admin(
    current_user: UserPublic = Depends(get_current_user),
) -> UserPublic:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso solo admin.")
    return current_user


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    existing = repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado.",
        )

    user = UserModel(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        is_active=True,
        is_admin=False,
    )
    saved = repo.save(user)
    return saved


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    token = create_access_token(subject=str(user.id_key), extra={"is_admin": bool(user.is_admin)})
    return Token(access_token=token)


@router.post("/admin/login", response_model=Token)
def admin_login(payload: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo admin.",
        )

    token = create_access_token(subject=str(user.id_key), extra={"is_admin": True})
    return Token(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current_user: UserPublic = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserPublic)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    repo = UserRepository(db)

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return current_user

    if "email" in changes:
        existing = repo.get_by_email(changes["email"])
        if existing and existing.id_key != current_user.id_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya registrado.",
            )

    updated = repo.update(current_user.id_key, changes)
    return updated
