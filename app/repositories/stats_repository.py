from sqlalchemy import case, desc, func
from sqlalchemy.orm import Session

from app import models


class StatsRepository:
    def get_user_average_score(self, db: Session, user_id: int):
        value = (
            db.query(func.avg(models.UserAnime.score))
            .filter(
                models.UserAnime.user_id == user_id,
                models.UserAnime.score.isnot(None),
            )
            .scalar()
        )
        return float(value) if value is not None else None

    def get_user_total_watched_episodes(self, db: Session, user_id: int):
        return (
            db.query(func.coalesce(func.sum(models.UserAnime.episodes_watched), 0))
            .filter(models.UserAnime.user_id == user_id)
            .scalar()
        )

    def get_user_total_completed(self, db: Session, user_id: int):
        return (
            db.query(func.count(models.UserAnime.id))
            .filter(
                models.UserAnime.user_id == user_id,
                models.UserAnime.status == "completed",
            )
            .scalar()
        )

    def get_user_personal_ranking(self, db: Session, user_id: int, limit: int = 10):
        return (
            db.query(
                models.Anime.id.label("anime_id"),
                models.Anime.title.label("title"),
                models.UserAnime.status.label("status"),
                models.UserAnime.score.label("score"),
                models.UserAnime.episodes_watched.label("episodes_watched"),
            )
            .join(models.UserAnime, models.UserAnime.anime_id == models.Anime.id)
            .filter(models.UserAnime.user_id == user_id)
            .order_by(
                case((models.UserAnime.score.is_(None), 1), else_=0),
                desc(models.UserAnime.score),
                desc(models.UserAnime.episodes_watched),
            )
            .limit(limit)
            .all()
        )

    def get_global_average_scores(self, db: Session, limit: int = 10):
        return (
            db.query(
                models.Anime.id.label("anime_id"),
                models.Anime.title.label("title"),
                func.avg(models.UserAnime.score).label("value"),
            )
            .join(models.UserAnime, models.UserAnime.anime_id == models.Anime.id)
            .filter(models.UserAnime.score.isnot(None))
            .group_by(models.Anime.id, models.Anime.title)
            .order_by(desc("value"))
            .limit(limit)
            .all()
        )

    def get_global_most_watched(self, db: Session):
        return (
            db.query(
                models.Anime.id.label("anime_id"),
                models.Anime.title.label("title"),
                func.count(models.UserAnime.id).label("value"),
            )
            .join(models.UserAnime, models.UserAnime.anime_id == models.Anime.id)
            .group_by(models.Anime.id, models.Anime.title)
            .order_by(desc("value"))
            .first()
        )

    def get_global_best_rated(self, db: Session):
        return (
            db.query(
                models.Anime.id.label("anime_id"),
                models.Anime.title.label("title"),
                func.avg(models.UserAnime.score).label("value"),
            )
            .join(models.UserAnime, models.UserAnime.anime_id == models.Anime.id)
            .filter(models.UserAnime.score.isnot(None))
            .group_by(models.Anime.id, models.Anime.title)
            .order_by(desc("value"))
            .first()
        )
