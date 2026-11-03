from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.user.model import User


@dataclass
class MembershipContext:
    business_id: UUID
    creator: User
    member: User
    invitee: User
    outsider: User


@pytest.fixture
async def membership_context(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> MembershipContext:
    creator = await create_user(test_session, "Business creator")
    member = await create_user(test_session, "Business member")
    invitee = await create_user(test_session, "Invitee")
    outsider = await create_user(test_session, "Outsider")
    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )
    return MembershipContext(
        business_id=business_id,
        creator=creator,
        member=member,
        invitee=invitee,
        outsider=outsider,
    )
