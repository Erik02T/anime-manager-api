"""
Arquivo: backend/app/repositories/social_repository.py
Camada: Module
Objetivo: Define responsabilidades deste modulo e sua funcao no sistema.
Dependencias: FastAPI/SQLAlchemy/Pydantic e utilitarios internos conforme necessario.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models


class SocialRepository:
    def create_review(self, db: Session, review: models.Review):
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    def create_comment(self, db: Session, comment: models.Comment):
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    def get_review(self, db: Session, review_id: int):
        return db.query(models.Review).filter(models.Review.id == review_id).first()

    def get_user(self, db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()

    def get_anime(self, db: Session, anime_id: int):
        return db.query(models.Anime).filter(models.Anime.id == anime_id).first()

    def create_follow(self, db: Session, follow: models.Follow):
        db.add(follow)
        db.commit()
        db.refresh(follow)
        return follow

    def get_follow(self, db: Session, follower_id: int, following_id: int):
        return (
            db.query(models.Follow)
            .filter(
                models.Follow.follower_id == follower_id,
                models.Follow.following_id == following_id,
            )
            .first()
        )

    def get_following_ids(self, db: Session, user_id: int):
        rows = db.query(models.Follow.following_id).filter(models.Follow.follower_id == user_id).all()
        return [row.following_id for row in rows]

    def create_activity(self, db: Session, activity: models.Activity):
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    def get_feed(self, db: Session, user_ids: list[int], limit: int = 20, offset: int = 0):
        if not user_ids:
            return []
        return (
            db.query(models.Activity)
            .filter(models.Activity.user_id.in_(user_ids))
            .order_by(models.Activity.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_recent_activities_for_user(self, db: Session, user_id: int, limit: int = 10, offset: int = 0):
        return (
            db.query(models.Activity)
            .filter(models.Activity.user_id == user_id)
            .order_by(models.Activity.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_followers_count(self, db: Session, user_id: int):
        return db.query(func.count(models.Follow.id)).filter(models.Follow.following_id == user_id).scalar()

    def get_following_count(self, db: Session, user_id: int):
        return db.query(func.count(models.Follow.id)).filter(models.Follow.follower_id == user_id).scalar()



