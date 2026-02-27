from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.core.cache import cache_store
from app.repositories.stats_repository import StatsRepository


class StatsService:
    def __init__(self, repository: StatsRepository | None = None):
        self.repository = repository or StatsRepository()

    def get_user_stats(self, db: Session, user_id: int):
        cache_key = f"stats:user:{user_id}"
        cached = cache_store.get(cache_key)
        if cached is not None:
            return cached

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        average_score = self.repository.get_user_average_score(db, user_id)
        total_watched_episodes = self.repository.get_user_total_watched_episodes(db, user_id)
        total_completed = self.repository.get_user_total_completed(db, user_id)
        personal_rows = self.repository.get_user_personal_ranking(db, user_id)

        personal_ranking = [
            {
                "anime_id": row.anime_id,
                "title": row.title,
                "status": row.status,
                "score": row.score,
                "episodes_watched": row.episodes_watched,
            }
            for row in personal_rows
        ]

        result = {
            "average_score": average_score,
            "total_watched_episodes": int(total_watched_episodes or 0),
            "total_completed": int(total_completed or 0),
            "personal_ranking": personal_ranking,
        }
        cache_store.set(cache_key, result, ttl_seconds=120)
        return result

    def get_global_stats(self, db: Session):
        cache_key = "stats:global"
        cached = cache_store.get(cache_key)
        if cached is not None:
            return cached

        average_rows = self.repository.get_global_average_scores(db)
        average_scores = [
            {
                "anime_id": row.anime_id,
                "title": row.title,
                "value": float(row.value) if row.value is not None else None,
            }
            for row in average_rows
        ]

        most_watched = self.repository.get_global_most_watched(db)
        best_rated = self.repository.get_global_best_rated(db)

        result = {
            "average_scores": average_scores,
            "most_watched": (
                {
                    "anime_id": most_watched.anime_id,
                    "title": most_watched.title,
                    "value": int(most_watched.value),
                }
                if most_watched
                else None
            ),
            "best_rated": (
                {
                    "anime_id": best_rated.anime_id,
                    "title": best_rated.title,
                    "value": float(best_rated.value),
                }
                if best_rated
                else None
            ),
        }
        cache_store.set(cache_key, result, ttl_seconds=120)
        return result
