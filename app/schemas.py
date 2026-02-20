from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


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

    class Config:
        orm_mode = True