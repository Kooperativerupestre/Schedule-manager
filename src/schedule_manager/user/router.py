from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.database.connection import get_session
from schedule_manager.user.schemas import UserAdd
from schedule_manager.user.service import UserService

router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserAdd,
    session: SessionDep,
) -> dict[str, UUID]:
    user_id = await UserService.create(session, user)
    return {"id": user_id}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    session: SessionDep,
) -> None:
    deleted = await UserService.delete_user(session, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
