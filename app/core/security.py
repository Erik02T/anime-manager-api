from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from .config import settings

# New hashes use pbkdf2_sha256 (no 72-byte bcrypt ceiling).
# Keep bcrypt for verifying existing users created before migration.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {
            "exp": expire,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
        }
    )
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
