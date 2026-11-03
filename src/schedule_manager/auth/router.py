from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.constants import SESSION_COOKIE_NAME, SESSION_TTL
from schedule_manager.auth.schemas import AuthenticationLogin
from schedule_manager.auth.service import AuthSessionService
from schedule_manager.database.connection import get_session

router = APIRouter(prefix="/auth", tags=["authentication"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(
    credentials: AuthenticationLogin,
    session: SessionDep,
    response: Response,
) -> None:
    token = await AuthSessionService.login(
        session,
        str(credentials.email),
        credentials.password,
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
