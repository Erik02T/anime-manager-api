"""
Arquivo: backend/app/routers/admin.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.permissions import require_roles
from app.database import get_db
from app.services.anime_import_service import AnimeImportService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[schemas.UserRead], summary="Admin user audit list")
def list_users_for_audit(
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return db.query(models.User).all()


@router.get("/schema-status", response_model=schemas.SchemaStatusRead, summary="Admin schema/migration status")
def schema_status(
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    inspector = inspect(db.bind)
    users_exists = inspector.has_table("users")
    role_exists = False
    role_index_exists = False
    pending: list[str] = []

    if users_exists:
        columns = {column["name"] for column in inspector.get_columns("users")}
        role_exists = "role" in columns
        index_names = {index["name"] for index in inspector.get_indexes("users")}
        role_index_exists = "ix_users_role" in index_names

        if not role_exists:
            pending.append("users.role column")
        if not role_index_exists:
            pending.append("ix_users_role index")
    else:
        pending.append("users table")

    return {
        "users_table_exists": users_exists,
        "users_role_column_exists": role_exists,
        "users_role_index_exists": role_index_exists,
        "pending_runtime_migrations": pending,
    }


@router.post("/import-anime", response_model=schemas.ImportAnimeResult, summary="Import anime from external catalog")
def import_anime(
    mal_id: int = Query(..., ge=1),
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = AnimeImportService()
    anime = service.import_by_mal_id(db, mal_id)
    return {"anime": anime, "source": "jikan"}


@router.post("/sync-animes", summary="Manual trigger for external sync")
def sync_animes(
    limit: int = Query(default=100, ge=1, le=500),
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = AnimeImportService()
    synced_count = service.sync_catalog(db, limit=limit)
    return {"synced_count": synced_count}



