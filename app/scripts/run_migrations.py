"""
Arquivo: backend/app/scripts/run_migrations.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

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



