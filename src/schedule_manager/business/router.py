from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.business.schemas import (
    BusinessAdd,
    BusinessOwnerAssign,
    BusinessResponse,
)
from schedule_manager.business.service import BusinessService
from schedule_manager.database.connection import get_session

router = APIRouter(prefix="/businesses", tags=["businesses"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> BusinessResponse:
    return await BusinessService.get(session, business_id, current_user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_business(
    business: BusinessAdd,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, UUID]:
    business_id = await BusinessService.create(
        session,
        business,
        current_user.id,
    )
    return {"id": business_id}


@router.post(
    "/{business_id}/owners",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def assign_business_owner(
    business_id: UUID,
    assignment: BusinessOwnerAssign,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await BusinessService.assign_owner(
        session,
        business_id,
        assignment.owner_id,
        current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{business_id}/owners/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_business_owner(
    business_id: UUID,
    owner_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await BusinessService.remove_owner(
        session,
        business_id,
        owner_id,
        current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await BusinessService.delete(session, business_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
