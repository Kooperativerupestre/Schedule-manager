from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.database.connection import get_session
from schedule_manager.workstation.workers.schemas import (
    WorkerCreateResponse,
    WorkerHireRequest,
    WorkerResponse,
)
from schedule_manager.workstation.workers.service import WorkerService

router = APIRouter(
    prefix="/workstations/{workstation_id}/workers",
    tags=["workers"],
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "",
    response_model=WorkerCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": WorkerCreateResponse}},
)
async def hire_worker(
    workstation_id: UUID,
    request: WorkerHireRequest,
    session: SessionDep,
    current_user: CurrentUser,
    response: Response,
) -> WorkerCreateResponse:
    worker_id = await WorkerService.hire(
        session,
        workstation_id,
        request.user_id,
        current_user.id,
    )
    if worker_id is None:
        response.status_code = status.HTTP_200_OK
        return WorkerCreateResponse(created=False)
    return WorkerCreateResponse(created=True, worker_id=worker_id)


@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    workstation_id: UUID,
    worker_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> WorkerResponse:
    return await WorkerService.get(
        session,
        workstation_id,
        worker_id,
        current_user.id,
    )


@router.delete(
    "/{worker_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def dismiss_worker(
    workstation_id: UUID,
    worker_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await WorkerService.dismiss(
        session,
        workstation_id,
        worker_id,
        current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
