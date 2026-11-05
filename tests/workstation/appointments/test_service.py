from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.workstation.appointments.model import (
    Appointment,
    AppointmentStatus,
)
from schedule_manager.workstation.appointments.repository import (
    AppointmentRepository,
)
from schedule_manager.workstation.appointments.schemas import AppointmentAdd
from schedule_manager.workstation.appointments.service import AppointmentService
from schedule_manager.workstation.schemas import WorkstationAdd
from schedule_manager.workstation.service import WorkstationService

from ..conftest import WorkstationContext


def _appointment(
    workstation_id: UUID,
    maker_id: UUID,
    begin_at: datetime,
    end_at: datetime,
) -> AppointmentAdd:
    return AppointmentAdd(
        workstation_id=workstation_id,
        maker_id=maker_id,
        begin_at=begin_at,
        end_at=end_at,
    )


@pytest.mark.anyio
async def test_can_schedule_rejects_overlap_but_allows_adjacent_period(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            unit_context.creator.id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )

    assert not await WorkstationService.can_schedule(
        test_session,
        workstation_id,
        begin_at + timedelta(minutes=30),
        begin_at + timedelta(hours=2),
    )
    assert await WorkstationService.can_schedule(
        test_session,
        workstation_id,
        begin_at + timedelta(hours=1),
        begin_at + timedelta(hours=2),
    )


@pytest.mark.anyio
async def test_cancelled_appointment_does_not_block_scheduling(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    cancelled = Appointment(
        workstation_id=workstation_id,
        maker_id=unit_context.creator.id,
        period=Range(begin_at, begin_at + timedelta(hours=1), bounds="[)"),
        status=AppointmentStatus.CANCELLED,
    )
    assert await AppointmentRepository.create(test_session, cancelled)

    assert await WorkstationService.can_schedule(
        test_session,
        workstation_id,
        begin_at,
        begin_at + timedelta(hours=1),
    )
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            unit_context.creator.id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )
    assert not await WorkstationService.can_schedule(
        test_session,
        workstation_id,
        begin_at,
        begin_at + timedelta(hours=1),
    )


@pytest.mark.anyio
async def test_overlapping_periods_are_allowed_on_different_workstations(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    second_workstation_id = await WorkstationService.create(
        test_session,
        WorkstationAdd(name="Second workstation", unit_id=unit_context.unit_id),
        unit_context.creator.id,
    )
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            unit_context.creator.id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )

    assert await WorkstationService.can_schedule(
        test_session,
        second_workstation_id,
        begin_at,
        begin_at + timedelta(hours=1),
    )


@pytest.mark.anyio
async def test_get_appointment_returns_utc_response(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    appointment = Appointment(
        workstation_id=workstation_id,
        maker_id=unit_context.creator.id,
        period=Range(begin_at, begin_at + timedelta(hours=1), bounds="[)"),
    )
    assert await AppointmentRepository.create(test_session, appointment)

    response = await AppointmentService.get(test_session, appointment.id)

    assert response is not None
    assert response.begin_at.tzinfo == UTC
    assert response.end_at.tzinfo == UTC
    assert response.made_at.tzinfo == UTC
    assert await AppointmentService.get(test_session, UUID(int=0)) is None


@pytest.mark.anyio
async def test_create_reports_exclusion_conflict_without_breaking_transaction(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    first = _appointment(
        workstation_id,
        unit_context.creator.id,
        begin_at,
        begin_at + timedelta(hours=1),
    )
    conflicting = _appointment(
        workstation_id,
        unit_context.creator.id,
        begin_at + timedelta(minutes=1),
        begin_at + timedelta(hours=1),
    )

    assert await AppointmentService.create(test_session, first)
    assert not await AppointmentService.create(test_session, conflicting)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            unit_context.creator.id,
            begin_at + timedelta(hours=1),
            begin_at + timedelta(hours=2),
        ),
    )


@pytest.mark.anyio
async def test_get_in_range_returns_all_intersecting_appointments(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    crossing = _appointment(
        workstation_id,
        unit_context.creator.id,
        begin_at - timedelta(minutes=30),
        begin_at + timedelta(minutes=30),
    )
    canceled = Appointment(
        workstation_id=workstation_id,
        maker_id=unit_context.creator.id,
        period=Range(
            begin_at + timedelta(minutes=30),
            begin_at + timedelta(hours=1),
            bounds="[)",
        ),
        status=AppointmentStatus.CANCELLED,
    )
    outside = _appointment(
        workstation_id,
        unit_context.creator.id,
        begin_at + timedelta(hours=1),
        begin_at + timedelta(hours=2),
    )

    assert await AppointmentService.create(test_session, crossing)
    assert await AppointmentRepository.create(test_session, canceled)
    assert await AppointmentService.create(test_session, outside)

    results = await AppointmentService.get_in_range(
        test_session,
        workstation_id,
        begin_at,
        begin_at + timedelta(hours=1),
    )

    assert {result.status for result in results} == {
        AppointmentStatus.PENDING,
        AppointmentStatus.CANCELLED,
    }
    assert len(results) == 2
    assert all(result.begin_at.tzinfo == UTC for result in results)


@pytest.mark.anyio
async def test_delete_appointment_returns_whether_it_existed(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            unit_context.creator.id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )
    appointment = await test_session.scalar(select(Appointment))
    assert appointment is not None

    assert await AppointmentService.delete(test_session, appointment.id)
    assert not await AppointmentService.delete(test_session, appointment.id)


def test_appointment_datetimes_are_normalized_to_utc_and_must_be_aware() -> None:
    offset = timezone(timedelta(hours=3))
    appointment = _appointment(
        UUID(int=1),
        UUID(int=2),
        datetime(2030, 1, 1, 12, tzinfo=offset),
        datetime(2030, 1, 1, 13, tzinfo=offset),
    )

    assert appointment.begin_at == datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert appointment.end_at == datetime(2030, 1, 1, 10, tzinfo=UTC)
    with pytest.raises(ValidationError):
        _appointment(
            UUID(int=1),
            UUID(int=2),
            datetime(2030, 1, 1, 9),
            datetime(2030, 1, 1, 10, tzinfo=UTC),
        )
    with pytest.raises(ValidationError):
        _appointment(
            UUID(int=1),
            UUID(int=2),
            datetime(2030, 1, 1, 10, tzinfo=UTC),
            datetime(2030, 1, 1, 9, tzinfo=UTC),
        )
