"""
Arquivo: backend/app/routers/social.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import get_current_user
from app.core.config import settings
from app.core.rate_limit import limit_requests
from app.database import get_db
from app.services.social_service import SocialService

router = APIRouter(prefix="/social", tags=["Social"])
social_rate_limit = Depends(limit_requests("social", settings.SOCIAL_RATE_LIMIT_PER_MINUTE))


@router.post(
    "/reviews",
    response_model=schemas.ReviewRead,
    summary="Publish review",
    dependencies=[social_rate_limit],
)
def create_review(
    payload: schemas.ReviewCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = SocialService()
    return service.create_review(db, payload)


@router.post(
    "/reviews/{review_id}/comments",
    response_model=schemas.CommentRead,
    summary="Comment on review",
    dependencies=[social_rate_limit],
)
def create_comment(
    review_id: int,
    payload: schemas.CommentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = SocialService()
    return service.create_comment(db, review_id, payload)


@router.post(
    "/follow",
    response_model=schemas.FollowRead,
    summary="Follow another user",
    dependencies=[social_rate_limit],
)
def follow_user(
    payload: schemas.FollowCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.follower_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = SocialService()
    return service.follow_user(db, payload.follower_id, payload.following_id)


@router.get(
    "/feed/{user_id}",
    response_model=list[schemas.ActivityRead],
    summary="Get social feed",
    dependencies=[social_rate_limit],
)
def get_feed(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = SocialService()
    return service.get_feed(db, user_id, limit=limit, offset=offset)


@router.get(
    "/dashboard/{user_id}",
    response_model=schemas.DashboardRead,
    summary="Get consolidated dashboard",
    dependencies=[social_rate_limit],
)
def get_dashboard(
    user_id: int,
    activity_limit: int = Query(default=10, ge=1, le=100),
    activity_offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = SocialService()
    return service.get_dashboard(
        db,
        user_id,
        activity_limit=activity_limit,
        activity_offset=activity_offset,
    )



