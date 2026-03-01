"""
Arquivo: backend/app/routers/animes.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..core.auth import get_current_user
from ..core.permissions import require_roles
from ..core.cache import cache_store
from ..database import get_db

router = APIRouter(prefix="/animes", tags=["Animes"])


@router.post("/")
def create_anime(
    anime: schemas.AnimeCreate,
    _current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
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

@router.get("/")
def read_animes(
    _current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(models.Anime).all()

@router.delete("/{anime_id}")
def delete_anime(
    anime_id: int,
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    db.delete(anime)
    db.commit()
    cache_store.invalidate("stats:global")
    cache_store.invalidate_prefix("stats:user:")
    return {"detail": "Anime deleted"}



