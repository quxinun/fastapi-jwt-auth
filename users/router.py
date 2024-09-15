import re

from fastapi import APIRouter, Depends, Response

from users.auth import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    authenticate_user,
)
from users.dependencies import (
    get_current_user,
    get_finger_print,
    get_refresh_token,
    check_refresh_token,
)
from users.models import Users
from users.schemas import SUserLogin, SUserRegister
from users.dao import UsersDAO, RefreshTokensDAO
import exceptions


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(new_user: SUserRegister):
    if not re.match(r"^[a-zA-Z]\w*$", new_user.username) or (
        len(new_user.username) > 20 or len(new_user.username) < 3
    ):
        raise exceptions.IncorrcetFormatUsername

    existing_email = await UsersDAO.find_one_or_none(email=new_user.email)
    existing_username = await UsersDAO.find_one_or_none(username=new_user.username)

    if existing_email and existing_username:
        raise exceptions.UsernameEmailAlreadyExistsException
    elif existing_email:
        raise exceptions.EmailAlreadyExistsException
    elif existing_username:
        raise exceptions.UsernameAlreadyExistsException

    hashed_password = get_password_hash(new_user.password)
    await UsersDAO.add(
        username=new_user.username,
        email=new_user.email,
        hashed_password=hashed_password,
    )


@router.post("/login")
async def login(
    response: Response,
    user_data: SUserLogin,
    fingerprint: str = Depends(get_finger_print),
):
    user = await authenticate_user(user_data.email_username, user_data.password)
    if not user:
        raise exceptions.IncorrectEmailLoginUserOrPassword

    await create_refresh_token(response, user.id, fingerprint)
    create_access_token(response, {"sub": str(user.id)})


@router.post("/refresh-tokens")
async def refresh_tokens(
    response: Response,
    old_refresh_token: str = Depends(get_refresh_token),
    fingerprint: str = Depends(get_finger_print),
):
    refresh_token = await RefreshTokensDAO.find_refresh_token(old_refresh_token)
    if refresh_token:
        await RefreshTokensDAO.delete_refresh_token(old_refresh_token)

    await check_refresh_token(response, refresh_token, fingerprint)
    create_access_token(response, {"sub": str(refresh_token.user_id)})


@router.post("/logout")
async def logout_user(
    response: Response, refresh_token: str = Depends(get_refresh_token)
):
    response.delete_cookie("auth_refresh_token")
    response.delete_cookie("auth_access_token")
    await RefreshTokensDAO.delete_refresh_token(refresh_token)


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user
