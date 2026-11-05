from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.database.connection import get_session
from schedule_manager.unit.schemas import (
    UnitAdd,
    UnitOwnerAssign,
    UnitResponse,
)
from schedule_manager.unit.service import UnitService

router = APIRouter(prefix="/units", tags=["units"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> UnitResponse:
    return await UnitService.get(session, unit_id, current_user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_unit(
    unit: UnitAdd,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, UUID]:
    unit_id = await UnitService.create(session, unit, current_user.id)
    return {"id": unit_id}


@router.post(
    "/{unit_id}/owners",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def assign_unit_owner(
    unit_id: UUID,
    assignment: UnitOwnerAssign,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await UnitService.assign_owner(
        session,
        unit_id,
        assignment.owner_id,
        current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{unit_id}/owners/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_unit_owner(
    unit_id: UUID,
    owner_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await UnitService.remove_owner(
        session,
        unit_id,
        owner_id,
        current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(
    unit_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await UnitService.delete(session, unit_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
