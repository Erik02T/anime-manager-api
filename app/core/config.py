from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./anime.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AUTO_CREATE_TABLES: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str | None = None
    JWT_ISSUER: str = "anime-manager"
    JWT_AUDIENCE: str = "anime-manager-users"
    AUTH_RATE_LIMIT_PER_MINUTE: int = 30
    SOCIAL_RATE_LIMIT_PER_MINUTE: int = 120
    JIKAN_BASE_URL: str = "https://api.jikan.moe/v4"
    EXTERNAL_API_TIMEOUT_SECONDS: int = 20
    EXTERNAL_CACHE_TTL_SECONDS: int = 3600
    ENABLE_ANIME_SYNC_JOB: bool = False
    ANIME_SYNC_INTERVAL_MINUTES: int = 60
    EXTERNAL_API_MAX_RETRIES: int = 3
    EXTERNAL_API_BACKOFF_SECONDS: float = 0.5
    ENABLE_RUNTIME_MIGRATIONS: bool = True
    REQUIRE_ALEMBIC_IN_PRODUCTION: bool = True

    model_config = ConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_security(self):
        if self.ENVIRONMENT.lower() == "production" and self.SECRET_KEY == "change-me-in-production":
            raise ValueError("SECRET_KEY must be changed in production")
        if self.ENVIRONMENT.lower() == "production" and self.REQUIRE_ALEMBIC_IN_PRODUCTION and self.ENABLE_RUNTIME_MIGRATIONS:
            raise ValueError("Disable runtime migrations in production and use Alembic migrations")
        return self


settings = Settings()
