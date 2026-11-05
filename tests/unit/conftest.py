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


@dataclass
class UnitContext:
    business_id: UUID
    unit_id: UUID
    creator: User
    member: User
    invitee: User
    outsider: User


@pytest.fixture
async def unit_context(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> UnitContext:
    creator = await create_user(test_session, "Unit creator")
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
    return UnitContext(
        business_id=business_id,
        unit_id=unit_id,
        creator=creator,
        member=member,
        invitee=invitee,
        outsider=outsider,
    )
