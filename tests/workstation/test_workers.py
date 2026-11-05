from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.user.errors import UserNotFoundError
from schedule_manager.user.model import User
from schedule_manager.workstation.errors import WorkstationForbiddenError
from schedule_manager.workstation.schemas import WorkstationAdd
from schedule_manager.workstation.service import WorkstationService
from schedule_manager.workstation.workers.errors import (
    WorkerForbiddenError,
    WorkerNotFoundError,
)
from schedule_manager.workstation.workers.model import Worker
from schedule_manager.workstation.workers.service import WorkerService

from .conftest import WorkstationContext


@pytest.mark.anyio
async def test_unit_owner_can_hire_worker_only_once_per_workstation(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    worker_id = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    repeated_hire = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )

    assert worker_id is not None
    assert repeated_hire is None
    worker = await test_session.get(Worker, worker_id)
    assert worker is not None
    assert worker.user_id == unit_context.invitee.id


@pytest.mark.anyio
async def test_unit_owner_can_hire_themselves(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    worker_id = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.creator.id,
        unit_context.creator.id,
    )

    assert worker_id is not None
    worker = await test_session.get(Worker, worker_id)
    assert worker is not None
    assert worker.user_id == unit_context.creator.id


@pytest.mark.anyio
async def test_workers_and_workstations_have_many_to_many_relationship(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    second_workstation_id = await WorkstationService.create(
        test_session,
        WorkstationAdd(name="Second workstation", unit_id=unit_context.unit_id),
        unit_context.creator.id,
    )
    worker_at_first = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    worker_at_second = await WorkerService.hire(
        test_session,
        second_workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    second_worker_at_first = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.outsider.id,
        unit_context.creator.id,
    )

    assert worker_at_first is not None
    assert worker_at_second is not None
    assert second_worker_at_first is not None
    assert len({worker_at_first, worker_at_second, second_worker_at_first}) == 3


@pytest.mark.anyio
async def test_non_owner_cannot_hire_worker(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    with pytest.raises(WorkstationForbiddenError):
        await WorkerService.hire(
            test_session,
            workstation_id,
            unit_context.invitee.id,
            unit_context.member.id,
        )


@pytest.mark.anyio
async def test_any_unit_member_can_get_worker(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )
    worker_id = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    assert worker_id is not None

    worker = await WorkerService.get(
        test_session,
        workstation_id,
        worker_id,
        unit_context.member.id,
    )

    assert worker.id == worker_id
    assert worker.user_id == unit_context.invitee.id
    assert worker.workstation_id == workstation_id


@pytest.mark.anyio
async def test_nonmember_cannot_get_worker(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    worker_id = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    assert worker_id is not None

    with pytest.raises(WorkerForbiddenError):
        await WorkerService.get(
            test_session,
            workstation_id,
            worker_id,
            unit_context.outsider.id,
        )


@pytest.mark.anyio
async def test_only_worker_can_dismiss_themselves(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    worker_id = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    assert worker_id is not None

    with pytest.raises(WorkerForbiddenError):
        await WorkerService.dismiss(
            test_session,
            workstation_id,
            worker_id,
            unit_context.creator.id,
        )

    assert await test_session.get(Worker, worker_id) is not None
    assert await WorkerService.dismiss(
        test_session,
        workstation_id,
        worker_id,
        unit_context.invitee.id,
    )
    assert await test_session.get(Worker, worker_id) is None


@pytest.mark.anyio
async def test_deleting_user_cascades_worker(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    worker_id = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    assert worker_id is not None

    user = await test_session.get(User, unit_context.invitee.id)
    assert user is not None
    await test_session.delete(user)
    await test_session.flush()

    assert (
        await test_session.scalar(select(Worker).where(Worker.id == worker_id))
        is None
    )


@pytest.mark.anyio
async def test_worker_must_exist_before_hiring(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    with pytest.raises(UserNotFoundError):
        await WorkerService.hire(
            test_session,
            workstation_id,
            UUID(int=0),
            unit_context.creator.id,
        )


@pytest.mark.anyio
async def test_get_missing_worker_raises_not_found(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    with pytest.raises(WorkerNotFoundError):
        await WorkerService.get(
            test_session,
            workstation_id,
            UUID(int=0),
            unit_context.creator.id,
        )
