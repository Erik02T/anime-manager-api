from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base


class Anime(Base):
    __tablename__ = "animes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String)
    episodes = Column(Integer)
    mal_id = Column(Integer, unique=True, nullable=True, index=True)
    external_score = Column(Integer, nullable=True)
    members = Column(Integer, nullable=True)
    external_status = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    synopsis = Column(Text, nullable=True)
    last_synced_at = Column(DateTime, nullable=True, index=True)
    user_entries = relationship("UserAnime", back_populates="anime", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="anime", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user", nullable=False, index=True)
    anime_entries = relationship("UserAnime", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")


class UserAnime(Base):
    __tablename__ = "user_animes"
    __table_args__ = (
        UniqueConstraint("user_id", "anime_id", name="uq_user_anime"),
        Index("ix_user_animes_user_status", "user_id", "status"),
        Index("ix_user_animes_anime_score", "anime_id", "score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey("animes.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    score = Column(Integer, nullable=True)
    episodes_watched = Column(Integer, default=0, nullable=False)
    start_date = Column(Date, nullable=True)
    finish_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="anime_entries")
    anime = relationship("Anime", back_populates="user_entries")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey("animes.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="reviews")
    anime = relationship("Anime", back_populates="reviews")
    comments = relationship("Comment", back_populates="review", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    review = relationship("Review", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follower_following"),
    )

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (
        Index("ix_activities_user_created", "user_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(String, nullable=False, index=True)
    target_type = Column(String, nullable=False)
    target_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="activities")
