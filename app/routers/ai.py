"""Camada Router (AI).

Responsabilidade:
- Expor endpoints HTTP para funcionalidades inteligentes do produto.
- Validar autorização/acesso e delegar regras de negócio para AIService.

Dependências usadas:
- FastAPI (roteamento/deps)
- AIService (recomendação/notícias/automação)
- Auth/Permissions (escopo do usuário e regras admin)
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import get_current_user
from app.core.permissions import require_roles
from app.database import get_db
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/recommendations", response_model=list[schemas.RecommendationRead], summary="AI recommendations for user")
def get_recommendations(
    limit: int = Query(default=20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AIService()
    return service.recommend_for_user(db, current_user.id, limit=limit)


@router.get("/news", response_model=list[schemas.NewsItemRead], summary="Release news and trends")
def get_news(
    limit: int = Query(default=10, ge=1, le=50),
    _current_user=Depends(get_current_user),
):
    service = AIService()
    return service.get_news_feed(limit=limit)


@router.post("/refresh-catalog", summary="Ingest trending and seasonal titles")
def refresh_catalog(
    limit: int = Query(default=40, ge=5, le=100),
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = AIService()
    count = service.ingest_trending_catalog(db, limit=limit)
    return {"updated": count}


@router.post(
    "/import-catalog-range",
    response_model=schemas.CatalogImportRangeResult,
    summary="Import historical catalog by year range and season",
)
def import_catalog_range(
    start_year: int = Query(default=2000, ge=1960, le=2100),
    end_year: int = Query(default=datetime.now().year, ge=1960, le=2100),
    seasons: list[str] | None = Query(default=None),
    pages_per_season: int = Query(default=1, ge=1, le=10),
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = AIService()
    return service.import_catalog_range(
        db=db,
        start_year=start_year,
        end_year=end_year,
        seasons=seasons,
        pages_per_season=pages_per_season,
    )


@router.post("/auto-status", response_model=schemas.AutoStatusResult, summary="Auto-update user anime statuses")
def auto_status(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AIService()
    return service.auto_update_statuses(db, current_user.id)


@router.post("/auto-status/all", response_model=schemas.AutoStatusResult, summary="Auto-update statuses for all users")
def auto_status_all(
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    service = AIService()
    return service.auto_update_statuses_all_users(db)
