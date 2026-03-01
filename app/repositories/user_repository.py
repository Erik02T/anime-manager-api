"""
Arquivo: backend/app/repositories/user_repository.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from sqlalchemy.orm import Session

from app import models
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[models.User]):

    def __init__(self):
        super().__init__(models.User)

    def get_by_username(self, db: Session, username: str):
        return db.query(models.User).filter(models.User.username == username).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    def create_user(
        self,
        db: Session,
        username: str,
        email: str,
        hashed_password: str,
        role: str = "user",
    ):
        db_user = models.User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        return self.add(db, db_user)



