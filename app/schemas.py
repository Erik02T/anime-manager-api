from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Camada Schema:
# Define contratos de entrada/saída da API (validação Pydantic + shape de resposta).
# Arquivo usado por todas as camadas HTTP (routers/services/tests/frontend).


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: Literal["admin", "user"]

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class AnimeCreate(BaseModel):
    title: str
    genre: str
    episodes: int

class ReadAnime(BaseModel):
    id: int
    title: str
    genre: str
    episodes: int
    mal_id: int | None = None
    external_score: int | None = None
    members: int | None = None
    external_status: str | None = None
    image_url: str | None = None
    synopsis: str | None = None
    last_synced_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


UserAnimeStatus = Literal["watching", "completed", "dropped", "on_hold", "planned"]
UserRole = Literal["admin", "user"]


class UserAnimeCreate(BaseModel):
    user_id: int
    anime_id: int
    status: UserAnimeStatus
    score: int | None = Field(default=None, ge=0, le=10)
    episodes_watched: int = Field(default=0, ge=0)
    start_date: date | None = None
    finish_date: date | None = None


class UserAnimeRead(BaseModel):
    id: int
    user_id: int
    anime_id: int
    status: UserAnimeStatus
    score: int | None
    episodes_watched: int
    start_date: date | None
    finish_date: date | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAnimeUpdate(BaseModel):
    status: UserAnimeStatus | None = None
    score: int | None = Field(default=None, ge=0, le=10)
    episodes_watched: int | None = Field(default=None, ge=0)
    episodes_increment: int | None = Field(default=None, ge=1)
    start_date: date | None = None
    finish_date: date | None = None


class PersonalRankingItem(BaseModel):
    anime_id: int
    title: str
    status: UserAnimeStatus
    score: int | None
    episodes_watched: int


class UserStatsRead(BaseModel):
    average_score: float | None
    total_watched_episodes: int
    total_completed: int
    personal_ranking: list[PersonalRankingItem]


class GlobalAnimeMetric(BaseModel):
    anime_id: int
    title: str
    value: float | int | None


class GlobalStatsRead(BaseModel):
    average_scores: list[GlobalAnimeMetric]
    most_watched: GlobalAnimeMetric | None
    best_rated: GlobalAnimeMetric | None


class ReviewCreate(BaseModel):
    user_id: int
    anime_id: int
    score: int = Field(ge=0, le=10)
    content: str


class ReviewRead(BaseModel):
    id: int
    user_id: int
    anime_id: int
    score: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    user_id: int
    content: str


class CommentRead(BaseModel):
    id: int
    review_id: int
    user_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityRead(BaseModel):
    id: int
    user_id: int
    activity_type: str
    target_type: str
    target_id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FollowCreate(BaseModel):
    follower_id: int
    following_id: int


class FollowRead(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardRead(BaseModel):
    user_stats: UserStatsRead
    followers_count: int
    following_count: int
    recent_activities: list[ActivityRead]


class SchemaStatusRead(BaseModel):
    users_table_exists: bool
    users_role_column_exists: bool
    users_role_index_exists: bool
    pending_runtime_migrations: list[str]


class ImportAnimeResult(BaseModel):
    anime: ReadAnime
    source: str


class RecommendationRead(BaseModel):
    # Resposta de recomendação já com score explicável.
    anime: ReadAnime
    recommendation_score: float
    reason: str


class NewsItemRead(BaseModel):
    # Item de feed de notícias/lançamentos.
    source: str
    title: str
    url: str | None = None
    summary: str | None = None
    published_at: datetime | None = None
    category: str


class AutoStatusResult(BaseModel):
    # Resultado de automação de status com trilha de alterações.
    updated_count: int
    details: list[str]


class CatalogImportRangeResult(BaseModel):
    start_year: int
    end_year: int
    seasons: list[str]
    pages_per_season: int
    inserted_or_updated: int
