from collections.abc import Awaitable, Callable
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.errors import UnitNotFoundError
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.user.model import User
from schedule_manager.workstation.errors import (
    WorkstationForbiddenError,
    WorkstationNotFoundError,
)
from schedule_manager.workstation.schemas import (
    WorkstationAdd,
    WorkstationResponse,
)
from schedule_manager.workstation.service import WorkstationService
from schedule_manager.workstation.workers.repository import WorkerRepository
from schedule_manager.workstation.workers.service import WorkerService

from .conftest import WorkstationContext


@pytest.mark.anyio
async def test_unit_owner_can_create_and_update_workstation(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
) -> None:
    workstation_id = await WorkstationService.create(
        test_session,
        WorkstationAdd(name="Original", unit_id=unit_context.unit_id),
        unit_context.creator.id,
    )

    updated = await WorkstationService.update(
        test_session,
        workstation_id,
        "Updated",
        unit_context.creator.id,
    )

    assert updated == WorkstationResponse(
        id=workstation_id,
        name="Updated",
        unit_id=unit_context.unit_id,
    )


@pytest.mark.anyio
async def test_unit_member_can_get_workstation(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    workstation = await WorkstationService.get(
        test_session,
        workstation_id,
        unit_context.member.id,
    )

    assert workstation.id == workstation_id
    assert workstation.unit_id == unit_context.unit_id


@pytest.mark.anyio
async def test_non_owner_cannot_create_update_or_delete_workstation(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    with pytest.raises(WorkstationForbiddenError):
        await WorkstationService.create(
            test_session,
            WorkstationAdd(name="Unauthorized", unit_id=unit_context.unit_id),
            unit_context.member.id,
        )
    with pytest.raises(WorkstationForbiddenError):
        await WorkstationService.update(
            test_session,
            workstation_id,
            "Unauthorized",
            unit_context.member.id,
        )
    with pytest.raises(WorkstationForbiddenError):
        await WorkstationService.delete(
            test_session,
            workstation_id,
            unit_context.member.id,
        )


@pytest.mark.anyio
async def test_nonmember_cannot_get_workstation(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> None:
    with pytest.raises(WorkstationForbiddenError):
        await WorkstationService.get(
            test_session,
            workstation_id,
            unit_context.outsider.id,
        )


@pytest.mark.anyio
async def test_creating_workstation_for_missing_unit_fails(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    user = await create_user(test_session, "User")

    with pytest.raises(UnitNotFoundError):
        await WorkstationService.create(
            test_session,
            WorkstationAdd(name="Orphan", unit_id=UUID(int=0)),
            user.id,
        )


@pytest.mark.anyio
async def test_deleting_workstation_cascades_workers(
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

    assert await WorkstationService.delete(
        test_session,
        workstation_id,
        unit_context.creator.id,
    )

    assert await WorkerRepository.get(test_session, workstation_id, worker_id) is None


@pytest.mark.anyio
async def test_missing_workstation_raises_not_found(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
) -> None:
    with pytest.raises(WorkstationNotFoundError):
        await WorkstationService.get(
            test_session,
            UUID(int=0),
            unit_context.creator.id,
        )
