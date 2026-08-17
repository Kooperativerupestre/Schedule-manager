import asyncio
from datetime import timedelta

from schedule_manager.business.memberships.models import BusinessMembershipInviteInput
from schedule_manager.core.errors import OverlappingSchedulesError
from schedule_manager.business.memberships.repository import MembershipRepository, MembershipInvitesRepository

async def test_same_membership_interval_only_allows_one_insert(
    setup_conn, connections, person_factory, create_business_with_owner,
) -> None:
    owner = await person_factory("membership-owner", "membership-owner-phone", setup_conn)
    member = await person_factory("membership-member", "membership-member-phone", setup_conn)
    business_id = await create_business_with_owner(owner.id, setup_conn)
    await setup_conn.commit()

    async def insert_membership(connection) -> None:
        async with connection.transaction():
            await MembershipRepository.add(member.id, business_id, connection)

    results = await asyncio.gather(*(insert_membership(connection) for connection in connections), return_exceptions=True)
    assert results.count(None) == 1
    assert all(result is None or isinstance(result, OverlappingSchedulesError) for result in results)


async def test_same_membership_invite_interval_only_allows_one_insert(
    setup_conn, connections, person_factory, create_business_with_owner,
) -> None:
    owner = await person_factory("invite-owner", "invite-owner-phone", setup_conn)
    business_id = await create_business_with_owner(owner.id, setup_conn)
    await setup_conn.commit()
    begin = datetime.now(timezone.utc)
    end = begin + timedelta(hours=1)
    
    async def insert_invite(connection) -> None:
        async with connection.transaction():
            await MembershipInvitesRepository.add(business_id,
            BusinessMembershipInviteInput("overlap@example.com", end) , connection)

    results = await asyncio.gather(*(insert_invite(connection) for connection in connections), return_exceptions=True)
    assert results.count(None) == 1
    assert all(result is None or isinstance(result, OverlappingSchedulesError) for result in results)
