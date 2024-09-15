from datetime import datetime
import hashlib

from fastapi import Depends, Header, Request, Response, WebSocket
import jwt

import exceptions
from config import settings
from users.dao import UsersDAO
from users.auth import create_refresh_token
from users.models import RefreshTokens


def get_access_token(request: Request = None, websocket: WebSocket = None):
    if request:
        access_token = request.cookies.get("auth_access_token")
    elif websocket:
        access_token = websocket.cookies.get("auth_access_token")
    else:
        raise exceptions.TokenAbsentException

    if not access_token:
        raise exceptions.TokenAbsentException

    return access_token


def get_refresh_token(request: Request):
    refresh_token = request.cookies.get("auth_refresh_token")
    if not refresh_token:
        raise exceptions.TokenAbsentException
    return refresh_token


async def check_refresh_token(
    response: Response, refresh_token: RefreshTokens, fingerprint: str
):
    if (not refresh_token) or int(
        refresh_token.expires_at.timestamp()
    ) < datetime.utcnow().timestamp():
        raise exceptions.TokenExpiredException

    if refresh_token.fingerprint != fingerprint:
        raise exceptions.INVALID_REFRESH_SESSION

    await create_refresh_token(response, refresh_token.user_id, fingerprint)


def get_finger_print(
    fingerprint: str = None,
    user_agent: str = Header(None),
    accept_language: str = Header(None),
    accept: str = Header(None),
    dnt: str = Header(None),
    connection: str = Header(None),
):
    if fingerprint is None:
        fingerprint = (
            f"{user_agent}-{accept_language}-{accept}-{dnt}-{connection}".replace(
                " ", ""
            )
        )
        return hashlib.sha256(fingerprint.encode()).hexdigest()

    return fingerprint


async def get_current_user(
    request: Request = None,
    websocket: WebSocket = None,
    access_token: str = Depends(get_access_token),
):
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, settings.ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredException
    except jwt.PyJWTError:
        raise exceptions.IncorrectTokenException

    user_id: str = payload.get("sub")
    if not user_id:
        raise exceptions.UserIsNotPresentException
    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise exceptions.UserIsNotPresentException

    return user
