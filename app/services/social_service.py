import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app import models
from app.events.bus import event_bus
from app.repositories.social_repository import SocialRepository
from app import schemas
from app.services.stats_service import StatsService


class SocialService:
    def __init__(self, repository: SocialRepository | None = None, stats_service: StatsService | None = None):
        self.repository = repository or SocialRepository()
        self.stats_service = stats_service or StatsService()
        self.logger = logging.getLogger(__name__)

    def create_review(self, db: Session, payload: schemas.ReviewCreate):
        if not self.repository.get_user(db, payload.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        if not self.repository.get_anime(db, payload.anime_id):
            raise HTTPException(status_code=404, detail="Anime not found")

        review = models.Review(
            user_id=payload.user_id,
            anime_id=payload.anime_id,
            score=payload.score,
            content=payload.content,
        )
        try:
            created = self.repository.create_review(db, review)
            try:
                event_bus.publish(
                    "activity.created",
                    {
                        "db": db,
                        "user_id": payload.user_id,
                        "activity_type": "review_created",
                        "target_type": "review",
                        "target_id": created.id,
                        "message": f"Published a review with score {payload.score}",
                    },
                )
            except Exception:
                self.logger.exception("failed to publish review activity")
            return created
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=503, detail="Database unavailable")

    def create_comment(self, db: Session, review_id: int, payload: schemas.CommentCreate):
        if not self.repository.get_user(db, payload.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        review = self.repository.get_review(db, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        comment = models.Comment(
            review_id=review_id,
            user_id=payload.user_id,
            content=payload.content,
        )
        try:
            created = self.repository.create_comment(db, comment)
            try:
                event_bus.publish(
                    "activity.created",
                    {
                        "db": db,
                        "user_id": payload.user_id,
                        "activity_type": "comment_created",
                        "target_type": "comment",
                        "target_id": created.id,
                        "message": "Posted a comment",
                    },
                )
            except Exception:
                self.logger.exception("failed to publish comment activity")
            return created
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=503, detail="Database unavailable")

    def follow_user(self, db: Session, follower_id: int, following_id: int):
        if follower_id == following_id:
            raise HTTPException(status_code=400, detail="You cannot follow yourself")

        if not self.repository.get_user(db, follower_id) or not self.repository.get_user(db, following_id):
            raise HTTPException(status_code=404, detail="User not found")

        if self.repository.get_follow(db, follower_id, following_id):
            raise HTTPException(status_code=400, detail="Already following this user")

        follow = models.Follow(follower_id=follower_id, following_id=following_id)
        try:
            created = self.repository.create_follow(db, follow)
            try:
                event_bus.publish(
                    "activity.created",
                    {
                        "db": db,
                        "user_id": follower_id,
                        "activity_type": "follow_created",
                        "target_type": "user",
                        "target_id": following_id,
                        "message": f"Started following user {following_id}",
                    },
                )
            except Exception:
                self.logger.exception("failed to publish follow activity")
            return created
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid follow relationship")
        except OperationalError:
            db.rollback()
            raise HTTPException(status_code=503, detail="Database unavailable")

    def get_feed(self, db: Session, user_id: int, limit: int = 20, offset: int = 0):
        if not self.repository.get_user(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")
        following_ids = self.repository.get_following_ids(db, user_id)
        return self.repository.get_feed(db, following_ids, limit=limit, offset=offset)

    def get_dashboard(self, db: Session, user_id: int, activity_limit: int = 10, activity_offset: int = 0):
        user_stats = self.stats_service.get_user_stats(db, user_id)
        followers_count = int(self.repository.get_followers_count(db, user_id) or 0)
        following_count = int(self.repository.get_following_count(db, user_id) or 0)
        recent_activities = self.repository.get_recent_activities_for_user(
            db,
            user_id,
            limit=activity_limit,
            offset=activity_offset,
        )

        return {
            "user_stats": user_stats,
            "followers_count": followers_count,
            "following_count": following_count,
            "recent_activities": [
                {
                    "id": activity.id,
                    "user_id": activity.user_id,
                    "activity_type": activity.activity_type,
                    "target_type": activity.target_type,
                    "target_id": activity.target_id,
                    "message": activity.message,
                    "created_at": activity.created_at,
                }
                for activity in recent_activities
            ],
        }
