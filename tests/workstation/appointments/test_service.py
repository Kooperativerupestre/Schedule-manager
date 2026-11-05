from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.workstation.appointments.model import (
    Appointment,
    AppointmentStatus,
)
from schedule_manager.workstation.appointments.repository import (
    AppointmentRepository,
)
from schedule_manager.workstation.appointments.schemas import (
    AppointmentActionResult,
    AppointmentAdd,
)
from schedule_manager.workstation.appointments.service import AppointmentService
from schedule_manager.workstation.schemas import WorkstationAdd
from schedule_manager.workstation.service import WorkstationService
from schedule_manager.workstation.workers.service import WorkerService

from ..conftest import WorkstationContext


def _appointment(
    workstation_id: UUID,
    worker_id: UUID,
    maker_id: UUID,
    begin_at: datetime,
    end_at: datetime,
) -> AppointmentAdd:
    return AppointmentAdd(
        workstation_id=workstation_id,
        worker_id=worker_id,
        maker_id=maker_id,
        begin_at=begin_at,
        end_at=end_at,
    )


@pytest.mark.anyio
async def test_can_schedule_rejects_overlap_but_allows_adjacent_period(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            appointment_worker_id,
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
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    cancelled = Appointment(
        workstation_id=workstation_id,
        worker_id=appointment_worker_id,
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
            appointment_worker_id,
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
    appointment_worker_id: UUID,
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
            appointment_worker_id,
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
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    appointment = Appointment(
        workstation_id=workstation_id,
        worker_id=appointment_worker_id,
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
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    first = _appointment(
        workstation_id,
        appointment_worker_id,
        unit_context.creator.id,
        begin_at,
        begin_at + timedelta(hours=1),
    )
    conflicting = _appointment(
        workstation_id,
        appointment_worker_id,
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
            appointment_worker_id,
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
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    crossing = _appointment(
        workstation_id,
        appointment_worker_id,
        unit_context.creator.id,
        begin_at - timedelta(minutes=30),
        begin_at + timedelta(minutes=30),
    )
    canceled = Appointment(
        workstation_id=workstation_id,
        worker_id=appointment_worker_id,
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
        appointment_worker_id,
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
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            appointment_worker_id,
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
        UUID(int=3),
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
            UUID(int=3),
            datetime(2030, 1, 1, 9),
            datetime(2030, 1, 1, 10, tzinfo=UTC),
        )
    with pytest.raises(ValidationError):
        _appointment(
            UUID(int=1),
            UUID(int=2),
            UUID(int=3),
            datetime(2030, 1, 1, 10, tzinfo=UTC),
            datetime(2030, 1, 1, 9, tzinfo=UTC),
        )


@pytest.mark.anyio
@pytest.mark.parametrize("authorized_role", ["maker", "assigned_worker", "unit_owner"])
async def test_only_maker_assigned_worker_or_unit_owner_can_cancel(
    authorized_role: str,
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    maker_id = unit_context.outsider.id
    appointment = _appointment(
        workstation_id,
        appointment_worker_id,
        maker_id,
        begin_at,
        begin_at + timedelta(hours=1),
    )
    assert await AppointmentService.create(test_session, appointment)
    persisted = await test_session.scalar(select(Appointment))
    assert persisted is not None
    requester_id = {
        "maker": maker_id,
        "assigned_worker": unit_context.invitee.id,
        "unit_owner": unit_context.creator.id,
    }[authorized_role]

    result = await AppointmentService.cancel(
        test_session,
        persisted.id,
        requester_id,
    )

    assert result == AppointmentActionResult.CANCELLED
    assert persisted.status == AppointmentStatus.CANCELLED


@pytest.mark.anyio
async def test_unrelated_user_cannot_cancel_appointment(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            appointment_worker_id,
            unit_context.outsider.id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )
    appointment = await test_session.scalar(select(Appointment))
    assert appointment is not None

    result = await AppointmentService.cancel(
        test_session,
        appointment.id,
        unit_context.member.id,
    )

    assert result == AppointmentActionResult.FORBIDDEN
    assert appointment.status == AppointmentStatus.PENDING


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("actor_role", "expected"),
    [
        ("assigned_worker", AppointmentActionResult.COMPLETED),
        ("maker", AppointmentActionResult.FORBIDDEN),
        ("unit_owner", AppointmentActionResult.FORBIDDEN),
    ],
)
async def test_only_assigned_worker_can_complete_appointment(
    actor_role: str,
    expected: AppointmentActionResult,
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    maker_id = unit_context.outsider.id
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            appointment_worker_id,
            maker_id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )
    appointment = await test_session.scalar(select(Appointment))
    assert appointment is not None
    requester_id = {
        "assigned_worker": unit_context.invitee.id,
        "maker": maker_id,
        "unit_owner": unit_context.creator.id,
    }[actor_role]

    result = await AppointmentService.complete(
        test_session,
        appointment.id,
        requester_id,
    )

    assert result == expected
    assert appointment.status == (
        AppointmentStatus.SUCCESSFUL
        if expected == AppointmentActionResult.COMPLETED
        else AppointmentStatus.PENDING
    )


@pytest.mark.anyio
async def test_terminal_appointments_report_state_results(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            appointment_worker_id,
            unit_context.outsider.id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )
    appointment = await test_session.scalar(select(Appointment))
    assert appointment is not None

    assert (
        await AppointmentService.complete(
            test_session,
            appointment.id,
            unit_context.invitee.id,
        )
        == AppointmentActionResult.COMPLETED
    )
    assert (
        await AppointmentService.complete(
            test_session,
            appointment.id,
            unit_context.invitee.id,
        )
        == AppointmentActionResult.ALREADY_COMPLETED
    )
    assert (
        await AppointmentService.cancel(
            test_session,
            appointment.id,
            unit_context.outsider.id,
        )
        == AppointmentActionResult.ALREADY_COMPLETED
    )
    assert (
        await AppointmentService.complete(
            test_session,
            UUID(int=0),
            unit_context.invitee.id,
        )
        == AppointmentActionResult.NOT_FOUND
    )
    cancelled_begin = begin_at + timedelta(hours=2)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            appointment_worker_id,
            unit_context.outsider.id,
            cancelled_begin,
            cancelled_begin + timedelta(hours=1),
        ),
    )
    cancelled_appointment = await test_session.scalar(
        select(Appointment).where(
            Appointment.status == AppointmentStatus.PENDING,
            Appointment.maker_id == unit_context.outsider.id,
        )
    )
    assert cancelled_appointment is not None
    assert (
        await AppointmentService.cancel(
            test_session,
            cancelled_appointment.id,
            unit_context.outsider.id,
        )
        == AppointmentActionResult.CANCELLED
    )
    assert (
        await AppointmentService.cancel(
            test_session,
            cancelled_appointment.id,
            unit_context.outsider.id,
        )
        == AppointmentActionResult.ALREADY_CANCELLED
    )
    assert (
        await AppointmentService.complete(
            test_session,
            cancelled_appointment.id,
            unit_context.invitee.id,
        )
        == AppointmentActionResult.ALREADY_CANCELLED
    )


@pytest.mark.anyio
async def test_worker_removal_preserves_appointment_history(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
    appointment_worker_id: UUID,
) -> None:
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    assert await AppointmentService.create(
        test_session,
        _appointment(
            workstation_id,
            appointment_worker_id,
            unit_context.outsider.id,
            begin_at,
            begin_at + timedelta(hours=1),
        ),
    )
    pending = await test_session.scalar(
        select(Appointment).where(Appointment.status == AppointmentStatus.PENDING)
    )
    assert pending is not None
    assert await WorkerService.dismiss(
        test_session,
        workstation_id,
        appointment_worker_id,
        unit_context.invitee.id,
    )
    await test_session.refresh(pending)

    assert pending.worker_id is None
    assert pending.status == AppointmentStatus.PENDING
    assert (
        await AppointmentService.complete(
            test_session,
            pending.id,
            unit_context.invitee.id,
        )
        == AppointmentActionResult.FORBIDDEN
    )
    assert (
        await AppointmentService.cancel(
            test_session,
            pending.id,
            unit_context.outsider.id,
        )
        == AppointmentActionResult.CANCELLED
    )


@pytest.mark.anyio
async def test_worker_assignment_must_belong_to_the_appointment_workstation(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    another_workstation_id = await WorkstationService.create(
        test_session,
        WorkstationAdd(name="Another workstation", unit_id=unit_context.unit_id),
        unit_context.creator.id,
    )
    another_worker_id = await WorkerService.hire(
        test_session,
        another_workstation_id,
        unit_context.outsider.id,
        unit_context.creator.id,
    )
    assert another_worker_id is not None
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    appointment = Appointment(
        workstation_id=workstation_id,
        worker_id=another_worker_id,
        maker_id=unit_context.creator.id,
        period=Range(begin_at, begin_at + timedelta(hours=1), bounds="[)"),
    )

    with pytest.raises(IntegrityError):
        await AppointmentRepository.create(test_session, appointment)

    assert await test_session.scalar(select(Appointment)) is None
