from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.database.connection import get_session
from schedule_manager.user.schemas import UserAdd, UserResponse
from schedule_manager.user.service import UserService

router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/me", response_model=UserResponse)
async def get_user(
    current_user: CurrentUser,
    session: SessionDep,
) -> UserResponse:
    return await UserService.get(session, current_user.id, current_user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserAdd,
    session: SessionDep,
) -> dict[str, UUID]:
    user_id = await UserService.create(session, user)
    return {"id": user_id}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    await UserService.delete_user(session, current_user.id)
