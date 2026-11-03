from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.memberships.repository import (
    MembershipRepository,
)
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.user.model import User


@pytest.mark.anyio
async def test_business_creator_is_automatically_a_member(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")

    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )

    membership = await MembershipRepository.get(
        test_session,
        business_id,
        creator.id,
    )

    assert membership is not None
    assert membership.user_id == creator.id
    assert membership.business_id == business_id
