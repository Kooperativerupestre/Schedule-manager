from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.constants import SESSION_COOKIE_NAME
from schedule_manager.auth.errors import AuthenticationSessionInvalidError
from schedule_manager.auth.model import Session as AuthSession
from schedule_manager.auth.service import AuthSessionService
from schedule_manager.database.connection import get_session
from schedule_manager.user.model import User
from schedule_manager.user.repository import UserRepository

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_auth_session(
    session: SessionDep,
    token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> AuthSession:
    if token is None:
        raise AuthenticationSessionInvalidError(
            "Authentication session is invalid or expired."
        )
    return await AuthSessionService.validate_session(session, token)


CurrentAuthSession = Annotated[
    AuthSession,
    Depends(get_current_auth_session),
]


async def get_current_user(
    session: SessionDep,
    auth_session: CurrentAuthSession,
) -> User:
    user = await UserRepository.get(session, auth_session.user_id)
    if user is None:
        raise AuthenticationSessionInvalidError(
            "Authentication session is invalid or expired."
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
