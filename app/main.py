import logging
import time
import uuid
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from . import models
from .core.config import settings
from .core.db_migrations import apply_runtime_migrations
from .core.logging import configure_logging
from .database import engine
from .events.activity_handlers import register_activity_handlers
from .jobs.anime_sync_job import anime_sync_loop
from .routers import admin, ai, animes, auth, social, stats, user_animes, users

configure_logging()
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "anime_manager_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "anime_manager_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

origins = [
    "http://localhost:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "https://anime-manager-web.vercel.app",
]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    sync_task = None
    register_activity_handlers()
    if settings.REQUIRE_ALEMBIC_IN_PRODUCTION and settings.ENVIRONMENT.lower() == "production":
        inspector = inspect(engine)
        if not inspector.has_table("alembic_version"):
            logger.error("alembic.version.table.missing")
    if settings.AUTO_CREATE_TABLES:
        try:
            models.Base.metadata.create_all(bind=engine)
            if settings.ENABLE_RUNTIME_MIGRATIONS:
                apply_runtime_migrations(engine, logger)
        except OperationalError:
            logger.exception("database startup connection failed")
        except Exception:
            logger.exception("unexpected startup error while creating tables")
    if settings.ENABLE_ANIME_SYNC_JOB:
        sync_task = asyncio.create_task(anime_sync_loop())
    yield
    if sync_task:
        sync_task.cancel()
        try:
            await sync_task
        except asyncio.CancelledError:
            logger.info("sync.catalog.task.cancelled")


app = FastAPI(
    title="Anime Manager API",
    version="2.0.0",
    description="Scalable backend for anime tracking, social activity and rankings.",
    lifespan=lifespan,
    contact={"name": "Erik Sant", "url": "https://github.com/Erik02T"},
    openapi_tags=[
        {"name": "Auth", "description": "Authentication and access token issuance."},
        {"name": "Users", "description": "User resource lookup."},
        {"name": "Animes", "description": "Anime catalog management."},
        {"name": "UserAnimes", "description": "User-to-anime tracking, progress and score."},
        {"name": "Stats", "description": "User and global ranking/statistics endpoints."},
        {"name": "Social", "description": "Reviews, comments, follows, feeds and dashboard."},
        {"name": "Admin", "description": "Role-protected administrative/audit endpoints."},
        {"name": "AI", "description": "Recommendation engine, trends and automation endpoints."},
        {"name": "Health", "description": "Operational health endpoints."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    duration_seconds = (time.perf_counter() - start)
    path = request.url.path
    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(duration_seconds)
    logger.info(
        "request.completed",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", tags=["Health"])
def healthcheck():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/metrics", tags=["Health"])
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(auth.router)
app.include_router(animes.router)
app.include_router(users.router)
app.include_router(user_animes.router)
app.include_router(stats.router)
app.include_router(social.router)
app.include_router(admin.router)
app.include_router(ai.router)
