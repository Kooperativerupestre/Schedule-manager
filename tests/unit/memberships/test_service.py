import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.errors import UnitForbiddenError
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.memberships.service import UnitMembershipService
from schedule_manager.unit.service import UnitService

from ..conftest import UnitContext


@pytest.mark.anyio
async def test_unit_owner_can_add_another_member(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    assert await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    assert await UnitMembershipService.add(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_unit_owner_gets_false_when_adding_existing_member(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
    )

    assert not await UnitMembershipService.add(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_member_who_is_not_an_owner_cannot_add_a_member(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    with pytest.raises(UnitForbiddenError):
        await UnitMembershipService.add(
            test_session,
            unit_context.unit_id,
            unit_context.invitee.id,
            unit_context.member.id,
        )


@pytest.mark.anyio
async def test_nonmember_cannot_add_a_member(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    with pytest.raises(UnitForbiddenError):
        await UnitMembershipService.add(
            test_session,
            unit_context.unit_id,
            unit_context.invitee.id,
            unit_context.outsider.id,
        )


@pytest.mark.anyio
async def test_unit_owner_can_remove_another_member(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
    )

    assert await UnitMembershipService.remove(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_unit_owner_gets_false_when_removing_nonmember(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    assert not await UnitMembershipService.remove(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )


@pytest.mark.anyio
async def test_member_who_is_not_an_owner_cannot_remove_a_member(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    with pytest.raises(UnitForbiddenError):
        await UnitMembershipService.remove(
            test_session,
            unit_context.unit_id,
            unit_context.member.id,
            unit_context.member.id,
        )


@pytest.mark.anyio
async def test_existing_member_can_get_another_member_membership(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
    )

    membership = await UnitMembershipService.get(
        test_session,
        unit_context.unit_id,
        unit_context.invitee.id,
        unit_context.member.id,
    )

    assert membership is not None
    assert membership.user_id == unit_context.invitee.id


@pytest.mark.anyio
async def test_existing_member_gets_none_for_missing_membership(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    assert (
        await UnitMembershipService.get(
            test_session,
            unit_context.unit_id,
            unit_context.invitee.id,
            unit_context.member.id,
        )
        is None
    )


@pytest.mark.anyio
async def test_nonmember_cannot_get_membership(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    await UnitMembershipRepository.add(
        test_session,
        unit_context.unit_id,
        unit_context.member.id,
    )

    with pytest.raises(UnitForbiddenError):
        await UnitMembershipService.get(
            test_session,
            unit_context.unit_id,
            unit_context.member.id,
            unit_context.outsider.id,
        )


@pytest.mark.anyio
async def test_unit_owner_membership_cannot_be_removed(
    test_session: AsyncSession,
    unit_context: UnitContext,
) -> None:
    with pytest.raises(UnitForbiddenError, match="business owner revokes"):
        await UnitMembershipService.remove(
            test_session,
            unit_context.unit_id,
            unit_context.creator.id,
            unit_context.creator.id,
        )

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
        unit_context.creator.id,
        unit_context.creator.id,
    )
    assert await UnitMembershipService.remove(
        test_session,
        unit_context.unit_id,
        unit_context.creator.id,
        unit_context.member.id,
    )
