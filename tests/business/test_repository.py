from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.memberships.model import BusinessMember
from schedule_manager.business.model import Business, BusinessOwner
from schedule_manager.business.repository import BusinessRepository
from schedule_manager.user.model import User


@pytest.mark.anyio
async def test_create_persists_business(
    test_session: AsyncSession,
) -> None:
    business = Business(name="Example business")

    created_business = await BusinessRepository.create(
        test_session,
        business,
    )

    assert created_business is business
    assert created_business.id is not None
    assert await test_session.scalar(
        select(Business.id).where(Business.id == created_business.id)
    ) == created_business.id


@pytest.mark.anyio
async def test_create_does_not_assign_owner(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
    business = await BusinessRepository.create(
        test_session,
        Business(name="Example business"),
    )

    owner_id = await test_session.scalar(
        select(BusinessOwner.owner_id).where(
            BusinessOwner.business_id == business.id,
            BusinessOwner.owner_id == creator.id,
        )
    )

    assert owner_id is None


@pytest.mark.anyio
async def test_create_does_not_add_creator_as_member(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
    business = await BusinessRepository.create(
        test_session,
        Business(name="Example business"),
    )

    member_id = await test_session.scalar(
        select(BusinessMember.user_id).where(
            BusinessMember.business_id == business.id,
            BusinessMember.user_id == creator.id,
        )
    )

    assert member_id is None
