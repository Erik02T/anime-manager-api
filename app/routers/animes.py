# Arquivo: backend/backend\app\routers\animes.py
# Camada: Module
# Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
# Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session
from .. import models, schemas
from ..core.auth import get_current_user
from ..core.permissions import require_roles
from ..core.cache import cache_store
from ..database import get_db

router = APIRouter(prefix="/animes", tags=["Animes"])


def _normalize_legacy_anime_row(row) -> dict:
    mapping = row._mapping if hasattr(row, "_mapping") else row
    return {
        "id": mapping.get("id"),
        "title": mapping.get("title"),
        "genre": mapping.get("genre"),
        "episodes": mapping.get("episodes"),
        "mal_id": mapping.get("mal_id"),
        "external_score": mapping.get("external_score"),
        "members": mapping.get("members"),
        "external_status": mapping.get("external_status"),
        "image_url": mapping.get("image_url"),
        "synopsis": mapping.get("synopsis"),
        "last_synced_at": mapping.get("last_synced_at"),
    }


def _legacy_read_animes(db: Session):
    queries = [
        text(
            """
            SELECT id, title, genre, episodes, mal_id, external_score, members, external_status, image_url, synopsis, last_synced_at
            FROM animes
            ORDER BY id DESC
            """
        ),
        text(
            """
            SELECT id, title, genre, episodes, NULL AS mal_id, NULL AS external_score, NULL AS members,
                   NULL AS external_status, NULL AS image_url, NULL AS synopsis, NULL AS last_synced_at
            FROM animes
            ORDER BY id DESC
            """
        ),
        text(
            """
            SELECT id, title, genre, episodes, NULL AS mal_id, NULL AS external_score, NULL AS members,
                   NULL AS external_status, NULL AS image_url, NULL AS synopsis, NULL AS last_synced_at
            FROM anime
            ORDER BY id DESC
            """
        ),
    ]
    last_exc: Exception | None = None
    for query in queries:
        try:
            rows = db.execute(query).fetchall()
            return [_normalize_legacy_anime_row(row) for row in rows]
        except Exception as exc:
            db.rollback()
            last_exc = exc
    raise HTTPException(status_code=503, detail="Database schema is not compatible") from last_exc


def _legacy_create_anime(db: Session, anime: schemas.AnimeCreate):
    statements = [
        (
            text("INSERT INTO animes (title, genre, episodes) VALUES (:title, :genre, :episodes) RETURNING id"),
            "animes",
        ),
        (
            text("INSERT INTO anime (title, genre, episodes) VALUES (:title, :genre, :episodes) RETURNING id"),
            "anime",
        ),
    ]
    for statement, table_name in statements:
        try:
            result = db.execute(statement, {"title": anime.title, "genre": anime.genre, "episodes": anime.episodes})
            inserted_id = result.scalar_one()
            db.commit()
            return {
                "id": inserted_id,
                "title": anime.title,
                "genre": anime.genre,
                "episodes": anime.episodes,
                "mal_id": None,
                "external_score": None,
                "members": None,
                "external_status": None,
                "image_url": None,
                "synopsis": None,
                "last_synced_at": None,
            }
        except Exception:
            db.rollback()
            if table_name == "anime":
                break
    raise HTTPException(status_code=503, detail="Database schema is not compatible")


@router.post("/")
def create_anime(
    anime: schemas.AnimeCreate,
    _current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        db_anime = models.Anime(
            title=anime.title,
            genre=anime.genre,
            episodes=anime.episodes,
        )
        db.add(db_anime)
        db.commit()
        db.refresh(db_anime)
        cache_store.invalidate("stats:global")
        return db_anime
    except (OperationalError, ProgrammingError):
        db.rollback()
        created = _legacy_create_anime(db, anime)
        cache_store.invalidate("stats:global")
        return created

@router.get("/")
def read_animes(
    _current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return db.query(models.Anime).all()
    except (OperationalError, ProgrammingError):
        db.rollback()
        return _legacy_read_animes(db)

@router.delete("/{anime_id}")
def delete_anime(
    anime_id: int,
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    try:
        anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        db.delete(anime)
        db.commit()
        cache_store.invalidate("stats:global")
        cache_store.invalidate_prefix("stats:user:")
        return {"detail": "Anime deleted"}
    except (OperationalError, ProgrammingError):
        db.rollback()
        for table_name in ("animes", "anime"):
            try:
                result = db.execute(text(f"DELETE FROM {table_name} WHERE id = :anime_id"), {"anime_id": anime_id})
                if result.rowcount and result.rowcount > 0:
                    db.commit()
                    cache_store.invalidate("stats:global")
                    cache_store.invalidate_prefix("stats:user:")
                    return {"detail": "Anime deleted"}
                db.rollback()
            except Exception:
                db.rollback()
        raise HTTPException(status_code=404, detail="Anime not found")




