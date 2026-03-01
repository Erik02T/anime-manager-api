"""
Arquivo: backend/app/jobs/anime_sync_job.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

import asyncio
import logging

from app.core.config import settings
from app.database import SessionLocal
from app.services.ai_service import AIService
from app.services.anime_import_service import AnimeImportService

logger = logging.getLogger(__name__)


async def anime_sync_loop() -> None:
    interval_seconds = max(1, settings.ANIME_SYNC_INTERVAL_MINUTES) * 60
    service = AnimeImportService()
    ai_service = AIService()
    while True:
        db = SessionLocal()
        try:
            synced = service.sync_catalog(db, limit=200)
            ai_updated = ai_service.ingest_trending_catalog(db, limit=40)
            status_updates = ai_service.auto_update_statuses_all_users(db)
            logger.info(
                "sync.catalog.completed",
                extra={
                    "synced_count": synced,
                    "ai_catalog_updated": ai_updated,
                    "auto_status_updated": status_updates.updated_count,
                },
            )
        except Exception:
            logger.exception("sync.catalog.failed")
        finally:
            db.close()

        await asyncio.sleep(interval_seconds)



