from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import Response
import jwt

from config import settings
from users.dao import UsersDAO, RefreshTokensDAO



def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hash_password: str):
    return get_password_hash(plain_password) == hash_password


def create_access_token(response: Response, data: dict) -> str:
    to_encode = data.copy()
    expires = timedelta(minutes=30)
    expire = datetime.utcnow() + expires
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    response.set_cookie(
        "auth_access_token", encode_jwt, max_age=int(expires.total_seconds())
    )


async def create_refresh_token(
    response: Response, user_id: int, fingerprint: str
) -> str:
    expires = timedelta(days=60)
    refresh_token = secrets.token_hex(32)
    expire = datetime.utcnow() + expires
    await RefreshTokensDAO.add_refresh_token(
        user_id, refresh_token, expire, fingerprint
    )
    response.set_cookie(
        "auth_refresh_token",
        refresh_token,
        httponly=True,
        max_age=int(expires.total_seconds()),
    )


async def authenticate_user(email_username: str, password: str):
    user = await UsersDAO.find_user(email_username)
    if not user:
        return None

    if verify_password(password, user.hashed_password):
        return user

    return None
