from datetime import datetime

from sqlalchemy import select, or_, insert, delete

from dao.base import BaseDAO
from users.models import Users, RefreshTokens
from database import async_session_maker


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def find_user(cls, email_username: str):
        async with async_session_maker() as session:
            query = select(Users.__table__.columns).filter(
                or_(
                    Users.email == email_username,
                    Users.username == email_username,
                )
            )
            result = await session.execute(query)
            return result.mappings().fetchone()


class RefreshTokensDAO(BaseDAO):
    model = RefreshTokens

    @classmethod
    async def add_refresh_token(
        cls, user_id: int, token: str, expires_at: datetime, fingerprint: str
    ):
        async with async_session_maker() as session:
            query = insert(RefreshTokens).values(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                fingerprint=fingerprint,
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def find_refresh_token(cls, refresh_token: str):
        async with async_session_maker() as session:
            query = select(RefreshTokens).filter_by(token=refresh_token)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def delete_refresh_token(cls, refresh_token: str):
        async with async_session_maker() as session:
            query = delete(RefreshTokens).filter_by(token=refresh_token)
            await session.execute(query)
            await session.commit()
