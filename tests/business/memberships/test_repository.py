import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.memberships.repository import (
    MembershipRepository,
)

from .conftest import MembershipContext


@pytest.mark.anyio
async def test_add_returns_true_when_membership_is_new(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    assert await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )


@pytest.mark.anyio
async def test_add_returns_false_when_membership_already_exists(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    assert not await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )


@pytest.mark.anyio
async def test_get_returns_existing_membership(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    membership = await MembershipRepository.get(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    assert membership is not None
    assert membership.user_id == membership_context.member.id
    assert membership.business_id == membership_context.business_id
    assert membership.begin_at is not None


@pytest.mark.anyio
async def test_get_returns_none_when_membership_does_not_exist(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    assert (
        await MembershipRepository.get(
            test_session,
            membership_context.business_id,
            membership_context.member.id,
        )
        is None
    )


@pytest.mark.anyio
async def test_remove_returns_true_when_membership_exists(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    await MembershipRepository.add(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )

    assert await MembershipRepository.remove(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )


@pytest.mark.anyio
async def test_remove_returns_false_when_membership_does_not_exist(
    test_session: AsyncSession,
    membership_context: MembershipContext,
) -> None:
    assert not await MembershipRepository.remove(
        test_session,
        membership_context.business_id,
        membership_context.member.id,
    )
