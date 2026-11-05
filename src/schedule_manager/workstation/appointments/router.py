from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.database.connection import get_session
from schedule_manager.workstation.appointments.errors import (
    AppointmentNotFoundError,
)
from schedule_manager.workstation.appointments.schemas import (
    AppointmentActionResponse,
    AppointmentActionResult,
    AppointmentAdd,
    AppointmentAvailabilityResponse,
    AppointmentCreateRequest,
    AppointmentCreateResponse,
    AppointmentResponse,
    AppointmentTimeRange,
)
from schedule_manager.workstation.appointments.service import AppointmentService
from schedule_manager.workstation.service import WorkstationService

router = APIRouter(
    prefix="/workstations/{workstation_id}/appointments",
    tags=["appointments"],
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _validate_time_range(begin_at: datetime, end_at: datetime) -> None:
    try:
        AppointmentTimeRange(begin_at=begin_at, end_at=end_at)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Appointment range must be timezone-aware and end after its start.",
        ) from error


async def _require_workstation_access(
    session: AsyncSession,
    workstation_id: UUID,
    current_user_id: UUID,
) -> None:
    await WorkstationService.get(session, workstation_id, current_user_id)


@router.post(
    "",
    response_model=AppointmentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": AppointmentCreateResponse}},
)
async def create_appointment(
    workstation_id: UUID,
    request: AppointmentCreateRequest,
    session: SessionDep,
    current_user: CurrentUser,
    response: Response,
) -> AppointmentCreateResponse:
    await _require_workstation_access(session, workstation_id, current_user.id)
    created = await AppointmentService.create(
        session,
        AppointmentAdd(
            workstation_id=workstation_id,
            worker_id=request.worker_id,
            maker_id=current_user.id,
            begin_at=request.begin_at,
            end_at=request.end_at,
        ),
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return AppointmentCreateResponse(created=created)


@router.get("", response_model=list[AppointmentResponse])
async def get_appointments_in_range(
    workstation_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    begin_at: Annotated[datetime, Query()],
    end_at: Annotated[datetime, Query()],
) -> list[AppointmentResponse]:
    _validate_time_range(begin_at, end_at)
    await _require_workstation_access(session, workstation_id, current_user.id)
    return await AppointmentService.get_in_range(
        session,
        workstation_id,
        begin_at,
        end_at,
    )


@router.get(
    "/availability",
    response_model=AppointmentAvailabilityResponse,
)
async def can_schedule_appointment(
    workstation_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    begin_at: Annotated[datetime, Query()],
    end_at: Annotated[datetime, Query()],
) -> AppointmentAvailabilityResponse:
    _validate_time_range(begin_at, end_at)
    await _require_workstation_access(session, workstation_id, current_user.id)
    can_schedule = await WorkstationService.can_schedule(
        session,
        workstation_id,
        begin_at,
        end_at,
    )
    return AppointmentAvailabilityResponse(can_schedule=can_schedule)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    workstation_id: UUID,
    appointment_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> AppointmentResponse:
    await _require_workstation_access(session, workstation_id, current_user.id)
    appointment = await AppointmentService.get(session, appointment_id)
    if appointment is None or appointment.workstation_id != workstation_id:
        raise AppointmentNotFoundError("Appointment not found.")
    return appointment


@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentActionResponse,
)
async def cancel_appointment(
    workstation_id: UUID,
    appointment_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> AppointmentActionResponse:
    appointment = await AppointmentService.get(session, appointment_id)
    if appointment is None or appointment.workstation_id != workstation_id:
        return AppointmentActionResponse(result=AppointmentActionResult.NOT_FOUND)
    result = await AppointmentService.cancel(
        session,
        appointment_id,
        current_user.id,
    )
    return AppointmentActionResponse(result=result)


@router.post(
    "/{appointment_id}/complete",
    response_model=AppointmentActionResponse,
)
async def complete_appointment(
    workstation_id: UUID,
    appointment_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> AppointmentActionResponse:
    appointment = await AppointmentService.get(session, appointment_id)
    if appointment is None or appointment.workstation_id != workstation_id:
        return AppointmentActionResponse(result=AppointmentActionResult.NOT_FOUND)
    result = await AppointmentService.complete(
        session,
        appointment_id,
        current_user.id,
    )
    return AppointmentActionResponse(result=result)


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_appointment(
    workstation_id: UUID,
    appointment_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    await _require_workstation_access(session, workstation_id, current_user.id)
    appointment = await AppointmentService.get(session, appointment_id)
    if appointment is None or appointment.workstation_id != workstation_id:
        raise AppointmentNotFoundError("Appointment not found.")
    if not await AppointmentService.delete(session, appointment_id):
        raise AppointmentNotFoundError("Appointment no longer exists.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
