import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.errors import UnitForbiddenError
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.repository import UnitRepository
from schedule_manager.unit.service import UnitService

from .conftest import UnitContext


@pytest.mark.anyio
async def test_business_owner_can_assign_unit_owner_to_a_member(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    assert await UnitService.assign_owner(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
        unit_context.creator.id,
    )
    assert not await UnitService.assign_owner(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_business_owner_cannot_assign_nonmember_as_unit_owner(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    with pytest.raises(UnitForbiddenError, match="must be a unit member"):
        await UnitService.assign_owner(
            test_session,
            unit_context.unit_id,
            unit_context.invitee.id,
            unit_context.creator.id,
        )


@pytest.mark.anyio
async def test_only_business_owner_can_assign_unit_ownership(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    with pytest.raises(UnitForbiddenError, match="business owner"):
        await UnitService.assign_owner(
            test_session,
            unit_context.unit_id,
            unit_context.member.id,
            unit_context.member.id,
        )


@pytest.mark.anyio
async def test_only_business_owner_can_revoke_unit_ownership(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    with pytest.raises(UnitForbiddenError, match="business owner"):
        await UnitService.remove_owner(
            test_session,
            unit_context.unit_id,
            unit_context.creator.id,
            unit_context.member.id,
        )

    assert await UnitService.remove_owner(
        test_session,
        unit_context.unit_id,
        unit_context.creator.id,
        unit_context.creator.id,
    )
    assert not await UnitRepository.is_owner(
        test_session,
        unit_context.unit_id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_business_owner_can_revoke_other_unit_owner(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )
    assert await UnitService.assign_owner(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
        unit_context.creator.id,
    )

    assert await UnitService.remove_owner(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
        unit_context.creator.id,
    )
    assert not await UnitRepository.is_owner(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )
