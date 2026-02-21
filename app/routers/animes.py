import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .. import models, schemas
from ..core.config import ALGORITHM, SECRET_KEY
from ..database import get_db

router = APIRouter(prefix="/animes", tags=["Animes"])
security = HTTPBearer()


def require_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return username


@router.post("/")
def create_anime(
    anime: schemas.AnimeCreate,
    _username: str = Depends(require_token),
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
    return db_anime

@router.get("/")
def read_animes(
    _username: str = Depends(require_token),
    db: Session = Depends(get_db),
):
    return db.query(models.Anime).all()

@router.delete("/{anime_id}")
def delete_anime(
    anime_id: int,
    _username: str = Depends(require_token),
    db: Session = Depends(get_db),
):
    anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    db.delete(anime)
    db.commit()
    return {"detail": "Anime deleted"}