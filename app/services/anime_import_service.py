from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.external.anime_client import JikanAnimeClient


class AnimeImportService:
    def __init__(self, client: JikanAnimeClient | None = None):
        self.client = client or JikanAnimeClient()

    def import_by_mal_id(self, db: Session, mal_id: int):
        if mal_id <= 0:
            raise HTTPException(status_code=400, detail="mal_id must be greater than zero")

        try:
            external = self.client.fetch_anime(mal_id)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=502, detail="External catalog unavailable")

        anime = db.query(models.Anime).filter(models.Anime.mal_id == mal_id).first()
        if not anime:
            anime = models.Anime(
                title=external["title"],
                genre=external["genre"],
                episodes=external["episodes"],
                mal_id=external["mal_id"],
                external_score=external["external_score"],
                members=external["members"],
                external_status=external["external_status"],
                image_url=external["image_url"],
                synopsis=external["synopsis"],
                last_synced_at=datetime.now(timezone.utc),
            )
            db.add(anime)
        else:
            anime.title = external["title"]
            anime.genre = external["genre"]
            anime.episodes = external["episodes"]
            anime.external_score = external["external_score"]
            anime.members = external["members"]
            anime.external_status = external["external_status"]
            anime.image_url = external["image_url"]
            anime.synopsis = external["synopsis"]
            anime.last_synced_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(anime)
        return anime

    def sync_catalog(self, db: Session, limit: int = 100) -> int:
        animes = (
            db.query(models.Anime)
            .filter(models.Anime.mal_id.is_not(None))
            .order_by(models.Anime.last_synced_at.asc().nullsfirst())
            .limit(limit)
            .all()
        )
        synced = 0
        for anime in animes:
            try:
                self.import_by_mal_id(db, anime.mal_id)
                synced += 1
            except Exception:
                db.rollback()
        return synced
