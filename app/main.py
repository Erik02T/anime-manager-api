from fastapi import FastAPI
from .database import engine
from . import models
from .routers import animes, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(animes.router)
  models.Base.metadata.create_all(bind=engine)
