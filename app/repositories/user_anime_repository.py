from sqlalchemy.orm import Session

from app import models
from app.repositories.base_repository import BaseRepository


class UserAnimeRepository(BaseRepository[models.UserAnime]):
    def __init__(self):
        super().__init__(models.UserAnime)

    def get_by_user_and_anime(self, db: Session, user_id: int, anime_id: int):
        return (
            db.query(models.UserAnime)
            .filter(
                models.UserAnime.user_id == user_id,
                models.UserAnime.anime_id == anime_id,
            )
            .first()
        )

    def create_entry(
        self,
        db: Session,
        user_id: int,
        anime_id: int,
        status: str,
        score: int | None,
        episodes_watched: int,
        start_date,
        finish_date,
    ):
        entry = models.UserAnime(
            user_id=user_id,
            anime_id=anime_id,
            status=status,
            score=score,
            episodes_watched=episodes_watched,
            start_date=start_date,
            finish_date=finish_date,
        )
        return self.add(db, entry)

    def list_by_user(self, db: Session, user_id: int, limit: int = 50, offset: int = 0):
        return (
            db.query(models.UserAnime)
            .filter(models.UserAnime.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_entry(self, db: Session, entry: models.UserAnime):
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
