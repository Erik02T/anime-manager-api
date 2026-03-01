"""
Arquivo: backend/app/events/activity_handlers.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from sqlalchemy.orm import Session

from app import models
from app.events.bus import event_bus

_registered = False


def _persist_activity(payload: dict) -> None:
    db: Session = payload["db"]
    activity = models.Activity(
        user_id=payload["user_id"],
        activity_type=payload["activity_type"],
        target_type=payload["target_type"],
        target_id=payload["target_id"],
        message=payload["message"],
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)


def register_activity_handlers() -> None:
    global _registered
    if _registered:
        return
    event_bus.subscribe("activity.created", _persist_activity)
    _registered = True



