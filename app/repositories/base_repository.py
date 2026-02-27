from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, obj_id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == obj_id).first()

    def add(self, db: Session, obj: ModelType) -> ModelType:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
