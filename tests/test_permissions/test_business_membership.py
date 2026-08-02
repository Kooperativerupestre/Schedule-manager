import pytest

from schedule_manager.business_memberships.service import MembershipInviteService, MembershipService
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.capabilities.errors import ForbiddenError
from tests.conftest import single_person

# membership

## forbidden
async def test_add_member_forbidden(
        conn:AsyncConnection[DictRow],
        single_person,
        business
) -> None:
    with pytest.raises(ForbiddenError):
        await MembershipService.add(
            single_person.id,
            single_person.id,
            business,
            conn
        )
async def test_end_member_forbidden(
        conn:AsyncConnection[DictRow],
        single_person,
        business
) -> None:
    with pytest.raises(ForbiddenError):
        await MembershipService.end(
            single_person.id,
            single_person.id,
            business,
            conn
        )
async def test_get_member_forbidden(
        conn:AsyncConnection[DictRow],
        person_factory,
        business
) -> None:
    p_1 = await person_factory('3', '3')
    p_2 = await person_factory('4', '4')
    with pytest.raises(ForbiddenError):
        await MembershipService.get(
            p_1.id,
            p_2.id,
            business,
            conn
        )
async def test_has_member_forbidden(
        conn:AsyncConnection[DictRow],
        person_factory,
        business
) -> None:
    p_1 = await person_factory('3', '3')
    p_2 = await person_factory('4', '4')
    with pytest.raises(ForbiddenError):
        await MembershipService.has(
            p_1.id,
            p_2.id,
            business,
            None,
            conn
        )
## allowed

async def test_add_member_allowed(
        conn:AsyncConnection[DictRow],
        create_business_with_owner,
        person_factory
) -> None:
    owner = await person_factory('3', '3')
    business_id = await create_business_with_owner(owner.id)
    member = await person_factory('4', '4')
    await MembershipService.add(
        owner.id,
        member.id,
        business_id,
        conn
    )
async def test_end_member_allowed(
        conn:AsyncConnection[DictRow],
        create_business_with_owner,
        person_factory
) -> None:
    owner = await person_factory('3', '3')
    business_id = await create_business_with_owner(owner.id)
    member = await person_factory('4', '4')
    await MembershipService.add(
        owner.id,
        member.id,
        business_id,
        conn
    )
    await MembershipService.end(
        owner.id,
        member.id,
        business_id,
        conn
    )
async def test_get_member_allowed(
        conn:AsyncConnection[DictRow],
        create_business_with_owner,
        person_factory
) -> None:
    owner = await person_factory('3', '3')
    business_id = await create_business_with_owner(owner.id)
    member = await person_factory('4', '4')
    await MembershipService.add(
        owner.id,
        member.id,
        business_id,
        conn
    )
    await MembershipService.get(
        owner.id,
        member.id,
        business_id,
        conn
    )
async def test_has_member_allowed(
        conn:AsyncConnection[DictRow],
        create_business_with_owner,
        person_factory
) -> None:
    owner = await person_factory('3', '3')
    business_id = await create_business_with_owner(owner.id)
    member = await person_factory('4', '4')
    await MembershipService.add(
        owner.id,
        member.id,
        business_id,
        conn
    )
    await MembershipService.has(
        owner.id,
        member.id,
        business_id,
        None,
        conn
    )

# invite

## forbidden

async def test_invite_member_forbidden(
        conn:AsyncConnection[DictRow],
        single_person,
        business
) -> None:
    with pytest.raises(ForbiddenError):
        await MembershipInviteService.add(
            single_person.id,
            single_person.id,
            business,
            conn
        )  
async def test_get_invite_member_forbidden(
        conn:AsyncConnection[DictRow],
        single_person,
        business
) -> None:
    with pytest.raises(ForbiddenError):
        await MembershipInviteService.get(
            single_person.id,
            single_person.id,
            business,
            conn
        )
async def test_has_ended_invite_member_forbidden(
        conn:AsyncConnection[DictRow],
        single_person,
        business
) -> None:
    with pytest.raises(ForbiddenError):
        await MembershipInviteService.has_ended(
            single_person.id,
            single_person.id,
            business,
            conn)
async def test_has_expired_invite_member_forbidden(
        conn:AsyncConnection[DictRow],
        single_person,
        business
) -> None:
    with pytest.raises(ForbiddenError):
        await MembershipInviteService.has_expired(
            single_person.id,
            single_person.id,
            business,
            conn
        )