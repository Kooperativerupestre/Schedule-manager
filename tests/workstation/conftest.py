from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.unit.schemas import UnitAdd
from schedule_manager.unit.service import UnitService
from schedule_manager.user.model import User
from schedule_manager.workstation.schemas import WorkstationAdd
from schedule_manager.workstation.service import WorkstationService

CreateUser = Callable[[AsyncSession, str], Awaitable[User]]


@dataclass
class WorkstationContext:
    unit_id: UUID
    creator: User
    member: User
    invitee: User
    outsider: User


@pytest.fixture
async def unit_context(
    test_session: AsyncSession,
    create_user: CreateUser,
) -> WorkstationContext:
    creator = await create_user(test_session, "Unit owner")
    member = await create_user(test_session, "Unit member")
    invitee = await create_user(test_session, "Invitee")
    outsider = await create_user(test_session, "Outsider")
    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )
    unit_id = await UnitService.create(
        test_session,
        UnitAdd(name="Example unit", business_id=business_id),
        creator.id,
    )
    assert await UnitService.assign_owner(
        test_session,
        unit_id,
        creator.id,
        creator.id,
    )
    return WorkstationContext(
        unit_id=unit_id,
        creator=creator,
        member=member,
        invitee=invitee,
        outsider=outsider,
    )


@pytest.fixture
async def workstation_id(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
) -> UUID:
    return await WorkstationService.create(
        test_session,
        WorkstationAdd(name="Example workstation", unit_id=unit_context.unit_id),
        unit_context.creator.id,
    )
