from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from ..core.auth import get_current_user
from ..core.config import settings
from ..core.rate_limit import limit_requests
from ..services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register",
    response_model=schemas.UserRead,
    dependencies=[Depends(limit_requests("auth:register", settings.AUTH_RATE_LIMIT_PER_MINUTE))],
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    service = UserService()
    return service.register_user(db, user)

@router.post(
    "/login",
    response_model=schemas.Token,
    dependencies=[Depends(limit_requests("auth:login", settings.AUTH_RATE_LIMIT_PER_MINUTE))],
)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    service = UserService()
    return service.login_user(db, user)


@router.get("/me", response_model=schemas.UserRead)
def me(current_user=Depends(get_current_user)):
    return current_user
