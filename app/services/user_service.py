"""
Arquivo: backend/app/services/user_service.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    def get_user(self, db: Session, user_id: int):
        user = self.user_repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def register_user(self, db: Session, user):
        if self.user_repository.get_by_username(db, user.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        if self.user_repository.get_by_email(db, user.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = hash_password(user.password)
        try:
            return self.user_repository.create_user(
                db,
                username=user.username,
                email=user.email,
                hashed_password=hashed,
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Username or email already registered")
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=503, detail="Database unavailable")

    def login_user(self, db: Session, user):
        db_user = self.user_repository.get_by_username(db, user.username)

        if not db_user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token({"sub": db_user.username, "role": db_user.role})
        return {"access_token": token, "token_type": "bearer"}



