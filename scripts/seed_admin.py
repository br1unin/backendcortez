import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from config.database import SessionLocal
from models.user import UserModel
from repositories.user_repository import UserRepository
from utils.security import hash_password


def run():
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        existing = repo.get_by_email("admin@demo.com")
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.commit()
            print("admin@demo.com ya existe.")
            return

        user = UserModel(
            email="admin@demo.com",
            name="Admin",
            password_hash=hash_password("admin123"),
            is_active=True,
            is_admin=True,
        )
        repo.save(user)
        print("Admin creado: admin@demo.com / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
