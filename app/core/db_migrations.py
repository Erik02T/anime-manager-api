"""
Arquivo: backend/app/core/db_migrations.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from logging import Logger

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def apply_runtime_migrations(engine: Engine, logger: Logger) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    with engine.begin() as connection:
        if "role" not in columns:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'user'")
            )
            logger.info("migration.applied", extra={"migration": "users.role.added"})

        connection.execute(text("UPDATE users SET role = 'user' WHERE role IS NULL"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)"))

    if inspector.has_table("animes"):
        anime_columns = {column["name"] for column in inspector.get_columns("animes")}
        anime_indexes = {index["name"] for index in inspector.get_indexes("animes")}
        with engine.begin() as connection:
            if "mal_id" not in anime_columns:
                connection.execute(text("ALTER TABLE animes ADD COLUMN mal_id INTEGER"))
                logger.info("migration.applied", extra={"migration": "animes.mal_id.added"})

            if "external_score" not in anime_columns:
                connection.execute(text("ALTER TABLE animes ADD COLUMN external_score INTEGER"))
                logger.info("migration.applied", extra={"migration": "animes.external_score.added"})

            if "members" not in anime_columns:
                connection.execute(text("ALTER TABLE animes ADD COLUMN members INTEGER"))
                logger.info("migration.applied", extra={"migration": "animes.members.added"})

            if "external_status" not in anime_columns:
                connection.execute(text("ALTER TABLE animes ADD COLUMN external_status VARCHAR"))
                logger.info("migration.applied", extra={"migration": "animes.external_status.added"})

            if "image_url" not in anime_columns:
                connection.execute(text("ALTER TABLE animes ADD COLUMN image_url VARCHAR"))
                logger.info("migration.applied", extra={"migration": "animes.image_url.added"})

            if "synopsis" not in anime_columns:
                connection.execute(text("ALTER TABLE animes ADD COLUMN synopsis TEXT"))
                logger.info("migration.applied", extra={"migration": "animes.synopsis.added"})

            if "last_synced_at" not in anime_columns:
                connection.execute(text("ALTER TABLE animes ADD COLUMN last_synced_at DATETIME"))
                logger.info("migration.applied", extra={"migration": "animes.last_synced_at.added"})

            if "ix_animes_mal_id" not in anime_indexes:
                connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_animes_mal_id ON animes (mal_id)"))
                logger.info("migration.applied", extra={"migration": "animes.ix_mal_id.added"})
            if "ix_animes_last_synced_at" not in anime_indexes:
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_animes_last_synced_at ON animes (last_synced_at)"))
                logger.info("migration.applied", extra={"migration": "animes.ix_last_synced_at.added"})



