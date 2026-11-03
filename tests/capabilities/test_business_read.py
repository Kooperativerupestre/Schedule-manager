from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.errors import BusinessForbiddenError
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.user.model import User


@pytest.mark.anyio
async def test_business_member_can_get_business(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )

    business = await BusinessService.get(
        test_session,
        business_id,
        creator.id,
    )

    assert business.id == business_id


@pytest.mark.anyio
async def test_nonmember_cannot_get_business(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
    nonmember = await create_user(test_session, "Nonmember")
    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )

    with pytest.raises(BusinessForbiddenError):
        await BusinessService.get(
            test_session,
            business_id,
            nonmember.id,
        )
