import asyncio
import logging

from app.core.config import settings
from app.database import SessionLocal
from app.services.anime_import_service import AnimeImportService

logger = logging.getLogger(__name__)


async def anime_sync_loop() -> None:
    interval_seconds = max(1, settings.ANIME_SYNC_INTERVAL_MINUTES) * 60
    service = AnimeImportService()
    while True:
        db = SessionLocal()
        try:
            synced = service.sync_catalog(db, limit=200)
            logger.info("sync.catalog.completed", extra={"synced_count": synced})
        except Exception:
            logger.exception("sync.catalog.failed")
        finally:
            db.close()

        await asyncio.sleep(interval_seconds)
