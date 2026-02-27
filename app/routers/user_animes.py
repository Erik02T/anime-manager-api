from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import get_current_user
from app.database import get_db
from app.services.user_anime_service import UserAnimeService

router = APIRouter(prefix="/user-animes", tags=["UserAnimes"])


@router.post("/", response_model=schemas.UserAnimeRead, summary="Create user-anime tracking entry")
def create_user_anime(
    payload: schemas.UserAnimeCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = UserAnimeService()
    return service.create_user_anime(db, payload)


@router.get("/user/{user_id}", response_model=list[schemas.UserAnimeRead], summary="List user-anime entries")
def list_user_animes(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    service = UserAnimeService()
    return service.list_user_animes(db, user_id, limit=limit, offset=offset)


@router.patch("/{entry_id}", response_model=schemas.UserAnimeRead, summary="Update progress and score")
def update_user_anime(
    entry_id: int,
    payload: schemas.UserAnimeUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserAnimeService()
    return service.update_user_anime(db, entry_id, payload, current_user.id)
