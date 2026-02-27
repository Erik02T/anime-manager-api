"""initial schema

Revision ID: 20260227_01
Revises:
Create Date: 2026-02-27 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260227_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "animes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("genre", sa.String(), nullable=True),
        sa.Column("episodes", sa.Integer(), nullable=True),
        sa.Column("mal_id", sa.Integer(), nullable=True),
        sa.Column("external_score", sa.Integer(), nullable=True),
        sa.Column("members", sa.Integer(), nullable=True),
        sa.Column("external_status", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("synopsis", sa.Text(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_animes_id", "animes", ["id"], unique=False)
    op.create_index("ix_animes_last_synced_at", "animes", ["last_synced_at"], unique=False)
    op.create_index("ix_animes_mal_id", "animes", ["mal_id"], unique=True)
    op.create_index("ix_animes_title", "animes", ["title"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("role", sa.String(), nullable=False, server_default="user"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(), nullable=False),
        sa.Column("target_type", sa.String(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_activity_type", "activities", ["activity_type"], unique=False)
    op.create_index("ix_activities_created_at", "activities", ["created_at"], unique=False)
    op.create_index("ix_activities_id", "activities", ["id"], unique=False)
    op.create_index("ix_activities_user_created", "activities", ["user_id", "created_at"], unique=False)
    op.create_index("ix_activities_user_id", "activities", ["user_id"], unique=False)

    op.create_table(
        "follows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.Column("following_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["following_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("follower_id", "following_id", name="uq_follower_following"),
    )
    op.create_index("ix_follows_follower_id", "follows", ["follower_id"], unique=False)
    op.create_index("ix_follows_following_id", "follows", ["following_id"], unique=False)
    op.create_index("ix_follows_id", "follows", ["id"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("anime_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["anime_id"], ["animes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_anime_id", "reviews", ["anime_id"], unique=False)
    op.create_index("ix_reviews_created_at", "reviews", ["created_at"], unique=False)
    op.create_index("ix_reviews_id", "reviews", ["id"], unique=False)
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"], unique=False)

    op.create_table(
        "user_animes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("anime_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("episodes_watched", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("finish_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["anime_id"], ["animes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "anime_id", name="uq_user_anime"),
    )
    op.create_index("ix_user_animes_anime_id", "user_animes", ["anime_id"], unique=False)
    op.create_index("ix_user_animes_anime_score", "user_animes", ["anime_id", "score"], unique=False)
    op.create_index("ix_user_animes_id", "user_animes", ["id"], unique=False)
    op.create_index("ix_user_animes_user_id", "user_animes", ["user_id"], unique=False)
    op.create_index("ix_user_animes_user_status", "user_animes", ["user_id", "status"], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_created_at", "comments", ["created_at"], unique=False)
    op.create_index("ix_comments_id", "comments", ["id"], unique=False)
    op.create_index("ix_comments_review_id", "comments", ["review_id"], unique=False)
    op.create_index("ix_comments_user_id", "comments", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_comments_user_id", table_name="comments")
    op.drop_index("ix_comments_review_id", table_name="comments")
    op.drop_index("ix_comments_id", table_name="comments")
    op.drop_index("ix_comments_created_at", table_name="comments")
    op.drop_table("comments")

    op.drop_index("ix_user_animes_user_status", table_name="user_animes")
    op.drop_index("ix_user_animes_user_id", table_name="user_animes")
    op.drop_index("ix_user_animes_id", table_name="user_animes")
    op.drop_index("ix_user_animes_anime_score", table_name="user_animes")
    op.drop_index("ix_user_animes_anime_id", table_name="user_animes")
    op.drop_table("user_animes")

    op.drop_index("ix_reviews_user_id", table_name="reviews")
    op.drop_index("ix_reviews_id", table_name="reviews")
    op.drop_index("ix_reviews_created_at", table_name="reviews")
    op.drop_index("ix_reviews_anime_id", table_name="reviews")
    op.drop_table("reviews")

    op.drop_index("ix_follows_id", table_name="follows")
    op.drop_index("ix_follows_following_id", table_name="follows")
    op.drop_index("ix_follows_follower_id", table_name="follows")
    op.drop_table("follows")

    op.drop_index("ix_activities_user_id", table_name="activities")
    op.drop_index("ix_activities_user_created", table_name="activities")
    op.drop_index("ix_activities_id", table_name="activities")
    op.drop_index("ix_activities_created_at", table_name="activities")
    op.drop_index("ix_activities_activity_type", table_name="activities")
    op.drop_table("activities")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_animes_title", table_name="animes")
    op.drop_index("ix_animes_mal_id", table_name="animes")
    op.drop_index("ix_animes_last_synced_at", table_name="animes")
    op.drop_index("ix_animes_id", table_name="animes")
    op.drop_table("animes")
