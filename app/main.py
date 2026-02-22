import logging
import os

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from .database import engine
from . import models
from .routers import animes, auth
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(auth.router)
app.include_router(animes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # pode usar ["*"] temporariamente
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    auto_create_tables = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"
    if not auto_create_tables:
        return

    try:
        models.Base.metadata.create_all(bind=engine)
    except OperationalError:
        logger.exception(
            "Nao foi possivel conectar ao banco no startup. Verifique DATABASE_URL e disponibilidade do Postgres."
        )
