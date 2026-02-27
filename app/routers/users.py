from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import get_current_user
from app.database import get_db
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    service = UserService()
    return service.get_user(db, user_id)
