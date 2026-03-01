"""
Arquivo: backend/app/services/user_anime_service.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app import models
from app.core.cache import cache_store
from app.repositories.user_anime_repository import UserAnimeRepository
from app import schemas


class UserAnimeService:
    def __init__(self, repository: UserAnimeRepository | None = None):
        self.repository = repository or UserAnimeRepository()

    def create_user_anime(self, db: Session, payload: schemas.UserAnimeCreate):
        user = db.query(models.User).filter(models.User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        anime = db.query(models.Anime).filter(models.Anime.id == payload.anime_id).first()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")

        existing = self.repository.get_by_user_and_anime(db, payload.user_id, payload.anime_id)
        if existing:
            raise HTTPException(status_code=400, detail="UserAnime entry already exists")

        try:
            created = self.repository.create_entry(
                db=db,
                user_id=payload.user_id,
                anime_id=payload.anime_id,
                status=payload.status,
                score=payload.score,
                episodes_watched=payload.episodes_watched,
                start_date=payload.start_date,
                finish_date=payload.finish_date,
            )
            self._invalidate_stats_cache(payload.user_id)
            return created
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid UserAnime data")
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=503, detail="Database unavailable")

    def list_user_animes(self, db: Session, user_id: int, limit: int = 50, offset: int = 0):
        return self.repository.list_by_user(db, user_id, limit=limit, offset=offset)

    def update_user_anime(
        self,
        db: Session,
        entry_id: int,
        payload: schemas.UserAnimeUpdate,
        current_user_id: int | None = None,
    ):
        entry = self.repository.get_by_id(db, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="UserAnime entry not found")
        if current_user_id is not None and entry.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not allowed")

        if payload.episodes_watched is not None and payload.episodes_increment is not None:
            raise HTTPException(
                status_code=400,
                detail="Use episodes_watched or episodes_increment, not both",
            )

        if payload.episodes_watched is not None or payload.episodes_increment is not None:
            anime = db.query(models.Anime).filter(models.Anime.id == entry.anime_id).first()
            if not anime:
                raise HTTPException(status_code=404, detail="Anime not found")

            if payload.episodes_watched is not None:
                new_progress = payload.episodes_watched
            else:
                new_progress = entry.episodes_watched + payload.episodes_increment

            if anime.episodes is not None and new_progress > anime.episodes:
                raise HTTPException(
                    status_code=400,
                    detail="Episodes watched cannot exceed total anime episodes",
                )
            entry.episodes_watched = new_progress

        if payload.status is not None:
            entry.status = payload.status
        if payload.score is not None:
            entry.score = payload.score
        if payload.start_date is not None:
            entry.start_date = payload.start_date
        if payload.finish_date is not None:
            entry.finish_date = payload.finish_date

        try:
            updated = self.repository.update_entry(db, entry)
            self._invalidate_stats_cache(updated.user_id)
            return updated
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=503, detail="Database unavailable")

    def _invalidate_stats_cache(self, user_id: int):
        cache_store.invalidate(f"stats:user:{user_id}")
        cache_store.invalidate("stats:global")



