from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.database.connection import get_session
from schedule_manager.workstation.schemas import (
    WorkstationAdd,
    WorkstationResponse,
    WorkstationUpdate,
)
from schedule_manager.workstation.service import WorkstationService

router = APIRouter(prefix="/workstations", tags=["workstations"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workstation(
    workstation: WorkstationAdd,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, UUID]:
    workstation_id = await WorkstationService.create(
        session,
        workstation,
        current_user.id,
    )
    return {"id": workstation_id}


@router.get("/{workstation_id}", response_model=WorkstationResponse)
async def get_workstation(
    workstation_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> WorkstationResponse:
    return await WorkstationService.get(
        session,
        workstation_id,
        current_user.id,
    )


@router.patch("/{workstation_id}", response_model=WorkstationResponse)
async def update_workstation(
    workstation_id: UUID,
    request: WorkstationUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> WorkstationResponse:
    return await WorkstationService.update(
        session,
        workstation_id,
        request.name,
        current_user.id,
    )


@router.delete(
    "/{workstation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_workstation(
    workstation_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await WorkstationService.delete(
        session,
        workstation_id,
        current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
