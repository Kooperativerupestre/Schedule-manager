import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.errors import BusinessForbiddenError
from schedule_manager.business.memberships.repository import (
    MembershipRepository,
)
from schedule_manager.business.memberships.service import MembershipService

from .conftest import MembershipContext


@pytest.mark.anyio
async def test_existing_member_can_add_another_member(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    assert await MembershipService.add(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
        membership_context.member.id,
    )


@pytest.mark.anyio
async def test_existing_member_gets_false_when_adding_existing_member(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
    )

    assert not await MembershipService.add(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
        membership_context.member.id,
    )


@pytest.mark.anyio
async def test_nonmember_cannot_add_a_member(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    with pytest.raises(BusinessForbiddenError):
        await MembershipService.add(
            test_session,
            membership_context.business_id,
            membership_context.invitee.id,
            membership_context.outsider.id,
        )


@pytest.mark.anyio
async def test_existing_member_can_remove_another_member(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
    )

    assert await MembershipService.remove(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
        membership_context.member.id,
    )


@pytest.mark.anyio
async def test_existing_member_gets_false_when_removing_nonmember(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    assert not await MembershipService.remove(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
        membership_context.member.id,
    )


@pytest.mark.anyio
async def test_nonmember_cannot_remove_a_member(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    with pytest.raises(BusinessForbiddenError):
        await MembershipService.remove(
            test_session,
            membership_context.business_id,
            membership_context.member.id,
            membership_context.outsider.id,
        )


@pytest.mark.anyio
async def test_existing_member_can_get_another_member_membership(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
    )

    membership = await MembershipService.get(
        test_session,
        membership_context.business_id,
        membership_context.invitee.id,
        membership_context.member.id,
    )

    assert membership is not None
    assert membership.user_id == membership_context.invitee.id


@pytest.mark.anyio
async def test_existing_member_gets_none_for_missing_membership(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    assert (
        await MembershipService.get(
            test_session,
            membership_context.business_id,
            membership_context.invitee.id,
            membership_context.member.id,
        )
        is None
    )


@pytest.mark.anyio
async def test_nonmember_cannot_get_membership(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    with pytest.raises(BusinessForbiddenError):
        await MembershipService.get(
            test_session,
            membership_context.business_id,
            membership_context.member.id,
            membership_context.outsider.id,
        )
