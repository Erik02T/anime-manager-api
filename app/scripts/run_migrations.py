import logging

from app.core.db_migrations import apply_runtime_migrations
from app.database import engine


def run() -> None:
    logger = logging.getLogger("migrations")
    logging.basicConfig(level=logging.INFO)
    apply_runtime_migrations(engine, logger)
    print("Runtime migrations executed.")


if __name__ == "__main__":
    run()
