"""
Arquivo: backend/app/routers/stats.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import get_current_user
from app.database import get_db
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/users/{user_id}", response_model=schemas.UserStatsRead, summary="Get user statistics")
def get_user_stats(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = StatsService()
    return service.get_user_stats(db, user_id)


@router.get("/global", response_model=schemas.GlobalStatsRead, summary="Get global ranking statistics")
def get_global_stats(
    _current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StatsService()
    return service.get_global_stats(db)



