from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.memberships.model import BusinessMember
from schedule_manager.business.model import BusinessOwner
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.unit.errors import UnitForbiddenError
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.repository import UnitRepository
from schedule_manager.unit.schemas import UnitAdd
from schedule_manager.unit.service import UnitService
from schedule_manager.user.model import User

from .conftest import UnitContext


@pytest.mark.anyio
async def test_business_owner_can_create_unit_and_joins_it(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    creator = await create_user(test_session, "Business creator")
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
    unit = await UnitService.get(test_session, unit_id, creator.id)

    assert unit.id == unit_id
    assert unit.business_id == business_id
    assert not await UnitRepository.is_owner(test_session, unit_id, creator.id)


@pytest.mark.anyio
async def test_deleting_business_cascades_unit_memberships_and_ownership(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    assert await UnitRepository.is_owner(
        test_session,
        unit_context.unit_id,
        unit_context.creator.id,
    )

    assert await BusinessService.delete(
        test_session,
        unit_context.business_id,
        unit_context.creator.id,
    )

    assert (
        await test_session.get(
            BusinessOwner,
            (unit_context.business_id, unit_context.creator.id),
        )
        is None
    )
    assert (
        await test_session.get(
            BusinessMember,
            (unit_context.creator.id, unit_context.business_id),
        )
        is None
    )
    assert await UnitRepository.get(test_session, unit_context.unit_id) is None
    assert (
        await UnitMembershipRepository.get(
            test_session,
            unit_context.unit_id,
            unit_context.creator.id,
        )
        is None
    )
    assert not await UnitRepository.is_owner(
        test_session,
        unit_context.unit_id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_deleting_unit_cascades_memberships_and_ownership(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    assert await UnitRepository.delete_unit(
        test_session,
        unit_context.unit_id,
    )

    assert (
        await UnitMembershipRepository.get(
            test_session,
            unit_context.unit_id,
            unit_context.creator.id,
        )
        is None
    )
    assert not await UnitRepository.is_owner(
        test_session,
        unit_context.unit_id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_non_owner_cannot_create_unit(
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

    with pytest.raises(UnitForbiddenError):
        await UnitService.create(
            test_session,
            UnitAdd(name="Example unit", business_id=business_id),
            non_owner.id,
        )


@pytest.mark.anyio
async def test_nonmember_cannot_get_unit(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    with pytest.raises(UnitForbiddenError):
        await UnitService.get(
            test_session,
            unit_context.unit_id,
            unit_context.outsider.id,
        )


@pytest.mark.anyio
async def test_only_business_owner_can_delete_unit(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    with pytest.raises(UnitForbiddenError):
        await UnitService.delete(
            test_session,
            unit_context.unit_id,
            unit_context.member.id,
        )

    assert await UnitService.delete(
        test_session,
        unit_context.unit_id,
        unit_context.creator.id,
    )
