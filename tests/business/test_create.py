from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.model import BusinessOwner
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.user.model import User


@pytest.mark.anyio
async def test_business_creator_is_assigned_as_owner(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")

    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )

    owner_id = await test_session.scalar(
        select(BusinessOwner.owner_id).where(
            BusinessOwner.business_id == business_id
        )
    )
    assert owner_id == creator.id
