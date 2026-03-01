from __future__ import annotations

"""Camada Service (AI).

Responsabilidade:
- Centralizar a lógica de recomendação e automação de status.
- Fazer ingestão de tendências/lançamentos para manter catálogo vivo.
- Transformar sinais de comportamento do usuário em ranking útil.

Dependências usadas:
- models/schemas (domínio e contrato de resposta)
- JikanAnimeClient (fonte externa de dados)
- SQLAlchemy Session (persistência/transações)
"""

from datetime import datetime, timezone
from math import log10

from sqlalchemy.orm import Session

from app import models, schemas
from app.external.anime_client import JikanAnimeClient


class AIService:
    def __init__(self, client: JikanAnimeClient | None = None):
        # Injeta o client externo para facilitar testes e troca de provider.
        self.client = client or JikanAnimeClient()

    def ingest_trending_catalog(self, db: Session, limit: int = 40) -> int:
        # Ingestão incremental: top + temporada atual, criando/atualizando registros locais.
        top = self.client.fetch_top_anime(limit=limit)
        season = self.client.fetch_current_season(limit=limit)
        inserted_or_updated = 0

        for item in top + season:
            mal_id = item.get("mal_id")
            if not mal_id:
                continue

            anime = db.query(models.Anime).filter(models.Anime.mal_id == mal_id).first()
            if anime is None:
                anime = models.Anime(mal_id=mal_id)
                db.add(anime)

            anime.title = item.get("title") or "Unknown title"
            anime.genre = item.get("genre") or "Unknown"
            anime.episodes = item.get("episodes") or 0
            anime.external_score = item.get("external_score")
            anime.members = item.get("members")
            anime.external_status = item.get("external_status")
            anime.image_url = item.get("image_url")
            anime.synopsis = item.get("synopsis")
            anime.last_synced_at = datetime.now(timezone.utc)
            inserted_or_updated += 1

        db.commit()
        return inserted_or_updated

    def recommend_for_user(self, db: Session, user_id: int, limit: int = 20) -> list[schemas.RecommendationRead]:
        # Ranking híbrido por afinidade de gêneros, popularidade e score externo.
        self._ensure_catalog_seed(db)

        user_entries = (
            db.query(models.UserAnime)
            .filter(models.UserAnime.user_id == user_id)
            .all()
        )
        user_anime_ids = {entry.anime_id for entry in user_entries}
        preferred_genres = self._extract_preferred_genres(db, user_entries)

        candidates_query = db.query(models.Anime)
        if user_anime_ids:
            candidates_query = candidates_query.filter(models.Anime.id.notin_(user_anime_ids))
        candidates = candidates_query.all()

        scored: list[tuple[models.Anime, float, str]] = []
        for anime in candidates:
            score, reason = self._score_anime(anime, preferred_genres)
            scored.append((anime, score, reason))

        scored.sort(key=lambda row: row[1], reverse=True)
        top_items = scored[: max(1, min(limit, 100))]
        return [
            schemas.RecommendationRead(
                anime=anime,
                recommendation_score=round(score, 3),
                reason=reason,
            )
            for anime, score, reason in top_items
        ]

    def get_news_feed(self, limit: int = 10) -> list[schemas.NewsItemRead]:
        # Feed de novidades orientado a lançamentos futuros (upcoming).
        items = self.client.fetch_upcoming(limit=limit)
        feed: list[schemas.NewsItemRead] = []
        for item in items[: max(1, min(limit, 50))]:
            feed.append(
                schemas.NewsItemRead(
                    source="jikan",
                    title=item.get("title") or "Anime update",
                    url=item.get("url"),
                    summary=item.get("synopsis"),
                    published_at=item.get("aired_from"),
                    category="release",
                )
            )
        return feed

    def auto_update_statuses(self, db: Session, user_id: int) -> schemas.AutoStatusResult:
        # Automação por regra simples:
        # - progresso >= episódios => completed
        # - progresso > 0 e planned/on_hold => watching
        entries = (
            db.query(models.UserAnime)
            .filter(models.UserAnime.user_id == user_id)
            .all()
        )
        details: list[str] = []
        updated = 0

        for entry in entries:
            anime = db.query(models.Anime).filter(models.Anime.id == entry.anime_id).first()
            if not anime:
                continue

            target_status = self._infer_status(entry.episodes_watched, anime.episodes, entry.status)
            if target_status != entry.status:
                details.append(f"{anime.title}: {entry.status} -> {target_status}")
                entry.status = target_status
                updated += 1

        if updated:
            db.commit()

        return schemas.AutoStatusResult(updated_count=updated, details=details)

    def auto_update_statuses_all_users(self, db: Session) -> schemas.AutoStatusResult:
        users = db.query(models.User.id).all()
        total = 0
        details: list[str] = []
        for (user_id,) in users:
            result = self.auto_update_statuses(db, user_id)
            total += result.updated_count
            details.extend(result.details)
        return schemas.AutoStatusResult(updated_count=total, details=details[:200])

    def _extract_preferred_genres(self, db: Session, entries: list[models.UserAnime]) -> dict[str, float]:
        # Perfil do usuário com pesos por status + nota histórica.
        genre_weights: dict[str, float] = {}
        for entry in entries:
            anime = db.query(models.Anime).filter(models.Anime.id == entry.anime_id).first()
            if anime is None or not anime.genre:
                continue

            status_weight = 1.0
            if entry.status == "completed":
                status_weight = 1.5
            elif entry.status == "watching":
                status_weight = 1.2
            elif entry.status == "planned":
                status_weight = 0.8

            score_weight = 1.0 + ((entry.score or 0) / 20.0)
            for raw in anime.genre.split(","):
                genre = raw.strip().lower()
                if not genre:
                    continue
                genre_weights[genre] = genre_weights.get(genre, 0.0) + (status_weight * score_weight)
        return genre_weights

    def _score_anime(self, anime: models.Anime, preferred_genres: dict[str, float]) -> tuple[float, str]:
        # Score final normalizado para recomendação.
        # Componentes: popularidade, nota externa, afinidade por gênero e frescor do catálogo.
        popularity = log10(max(10, (anime.members or 0) + 10)) / 6.0
        external_score = (anime.external_score or 0) / 10.0
        freshness = 0.0
        if anime.last_synced_at:
            last_synced = anime.last_synced_at
            if last_synced.tzinfo is None:
                last_synced = last_synced.replace(tzinfo=timezone.utc)
            age_days = max(1, int((datetime.now(timezone.utc) - last_synced).total_seconds() / 86400))
            freshness = 1.0 / min(30, age_days)

        genre_boost = 0.0
        if anime.genre:
            for raw in anime.genre.split(","):
                genre = raw.strip().lower()
                genre_boost += preferred_genres.get(genre, 0.0)
        normalized_genre_boost = min(2.0, genre_boost / 5.0)

        total = (0.45 * popularity) + (0.35 * external_score) + (0.15 * normalized_genre_boost) + (0.05 * freshness)
        if normalized_genre_boost >= 0.8:
            reason = "Alta afinidade com seus generos favoritos"
        elif popularity >= 0.8:
            reason = "Em alta entre os usuarios"
        elif freshness >= 0.03:
            reason = "Lancamento com boa tendencia"
        else:
            reason = "Boa combinacao de nota e popularidade"
        return total, reason

    def _ensure_catalog_seed(self, db: Session):
        catalog_size = db.query(models.Anime).count()
        if catalog_size < 25:
            self.ingest_trending_catalog(db, limit=40)

    @staticmethod
    def _infer_status(progress: int, episodes: int, current_status: str) -> str:
        safe_progress = max(0, progress or 0)
        safe_episodes = max(0, episodes or 0)
        if safe_episodes > 0 and safe_progress >= safe_episodes:
            return "completed"
        if safe_progress > 0 and current_status in {"planned", "on_hold"}:
            return "watching"
        return current_status
