from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.errors import BusinessForbiddenError
from schedule_manager.business.memberships.repository import (
    MembershipRepository,
)
from schedule_manager.business.model import BusinessOwner
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.user.model import User


@pytest.mark.anyio
async def test_only_business_owners_can_assign_ownership(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
    other_owner = await create_user(test_session, "New owner")
    non_owner = await create_user(test_session, "Non-owner")
    rejected_owner = await create_user(test_session, "Rejected owner")
    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )
    assert await MembershipRepository.add(
        test_session,
        business_id,
        other_owner.id,
    )

    assert await BusinessService.assign_owner(
        test_session, business_id, other_owner.id, creator.id
    )
    assert not await BusinessService.assign_owner(
        test_session, business_id, other_owner.id, creator.id
    )
    with pytest.raises(BusinessForbiddenError):
        await BusinessService.assign_owner(
            test_session,
            business_id,
            rejected_owner.id,
            non_owner.id,
        )

    assigned_owner_ids = set(
        (
            await test_session.scalars(
                select(BusinessOwner.owner_id).where(
                    BusinessOwner.business_id == business_id
                )
            )
        ).all()
    )
    assert assigned_owner_ids == {creator.id, other_owner.id}


@pytest.mark.anyio
async def test_only_business_owners_can_remove_owner_capability(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
    owner = await create_user(test_session, "Owner")
    non_owner = await create_user(test_session, "Non-owner")
    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )
    assert await MembershipRepository.add(
        test_session,
        business_id,
        owner.id,
    )
    assert await BusinessService.assign_owner(
        test_session, business_id, owner.id, creator.id
    )

    with pytest.raises(BusinessForbiddenError):
        await BusinessService.remove_owner(
            test_session, business_id, owner.id, non_owner.id
        )

    assert await BusinessService.remove_owner(
        test_session, business_id, owner.id, creator.id
    )
    assert not await BusinessService.remove_owner(
        test_session, business_id, owner.id, creator.id
    )


@pytest.mark.anyio
async def test_only_business_owners_can_delete_business(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
    non_owner = await create_user(test_session, "Non-owner")
    business_id = await BusinessService.create(
        test_session,
        BusinessAdd(name="Example business"),
        creator.id,
    )

    with pytest.raises(BusinessForbiddenError):
        await BusinessService.delete(test_session, business_id, non_owner.id)

    assert await BusinessService.delete(test_session, business_id, creator.id)


@pytest.mark.anyio
async def test_cannot_assign_nonmember_as_owner(
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
        await BusinessService.assign_owner(
            test_session,
            business_id,
            nonmember.id,
            creator.id,
        )
