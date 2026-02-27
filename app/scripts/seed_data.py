from app import models
from app.database import SessionLocal, engine
from app.core.security import hash_password


def run() -> None:
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.User).count() > 0:
            print("Seed skipped: users already exist.")
            return

        user = models.User(
            username="demo_user",
            email="demo_user@example.com",
            hashed_password=hash_password("demo123"),
        )
        anime_1 = models.Anime(title="Fullmetal Alchemist: Brotherhood", genre="Shounen", episodes=64)
        anime_2 = models.Anime(title="Steins;Gate", genre="Sci-Fi", episodes=24)
        db.add_all([user, anime_1, anime_2])
        db.commit()
        db.refresh(user)
        db.refresh(anime_1)
        db.refresh(anime_2)

        entry_1 = models.UserAnime(
            user_id=user.id,
            anime_id=anime_1.id,
            status="completed",
            score=10,
            episodes_watched=64,
        )
        entry_2 = models.UserAnime(
            user_id=user.id,
            anime_id=anime_2.id,
            status="watching",
            score=9,
            episodes_watched=8,
        )
        db.add_all([entry_1, entry_2])
        db.commit()
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
