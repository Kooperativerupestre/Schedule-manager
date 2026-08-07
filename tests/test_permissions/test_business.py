import pytest
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.business.schemas import BusinessAddRequest, BusinessUpdateRequest
from schedule_manager.business.service import BusinessService
from schedule_manager.business.memberships.service import MembershipService
from schedule_manager.capabilities.capabilities import Action, Resource
from schedule_manager.capabilities.errors import ForbiddenError
from schedule_manager.capabilities.service import CapabilitiesService
from schedule_manager.capabilities.schemas import CapabilityGetRequest, CapabilityAddRequest
from tests.helpers import GLOBAL_VALID_NUMBER
from schedule_manager.core.ranges.constants import NEVER_END


async def test_delete_business_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await BusinessService.delete(single_person.id, business, conn)


async def test_update_business_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await BusinessService.update(
            single_person.id,
            business,
            BusinessUpdateRequest(
                name='Updated Business',
                description='Updated description',
                phone_number=GLOBAL_VALID_NUMBER,
            ),
            conn,
        )


async def test_read_business_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await BusinessService.get(single_person.id, business, conn)


async def test_add_member_permission_requires_members_manage(
    conn: AsyncConnection[DictRow],
    person_factory,
) -> None:
    owner = await person_factory('owner', '1000000000')
    business_id = await BusinessService.add(
        owner.id,
        BusinessAddRequest(name='Business', description='test', phone_number=GLOBAL_VALID_NUMBER),
        conn,
    )
    member = await person_factory('member', '2000000000')

    await MembershipService.add(owner.id, member.id, business_id, conn)

    viewer = await person_factory('viewer', '3000000000')
    with pytest.raises(ForbiddenError):
        await CapabilitiesService.add(
            viewer.id,
            member.id,
            CapabilityAddRequest(
                resource=Resource.MEMBERS,
                action=Action.INVITE,
                target_id=business_id,
                end_at=NEVER_END,
            ),
            conn,
        )


async def test_delete_business_with_permission(
    conn: AsyncConnection[DictRow],
    single_person,
    create_business_with_owner,
) -> None:
    business_id = await create_business_with_owner(single_person.id)

    await BusinessService.delete(single_person.id, business_id, conn)


async def test_update_business_with_permission(
    conn: AsyncConnection[DictRow],
    single_person,
    create_business_with_owner,
) -> None:
    business_id = await create_business_with_owner(single_person.id)

    await BusinessService.update(
        single_person.id,
        business_id,
        BusinessUpdateRequest(
            name='Updated Business',
            description='Updated description',
            phone_number=GLOBAL_VALID_NUMBER,
        ),
        conn,
    )


async def test_read_business_with_permission(
    conn: AsyncConnection[DictRow],
    single_person,
    create_business_with_owner,
) -> None:
    business_id = await create_business_with_owner(single_person.id)

    business = await BusinessService.get(single_person.id, business_id, conn)

    assert business is not None
    assert business.phone_number == GLOBAL_VALID_NUMBER


async def test_add_business_grants_member_permissions(
    conn: AsyncConnection[DictRow],
    single_person,
) -> None:
    business_id = await BusinessService.add(
        single_person.id,
        BusinessAddRequest(name='Business', description='test', phone_number=GLOBAL_VALID_NUMBER),
        conn,
    )

    member_capability = await CapabilitiesService.has(
        single_person.id,
        single_person.id,
        CapabilityGetRequest(
            resource=Resource.MEMBERS,
            action=Action.MANAGE,
            target_id=business_id,
        ),
        conn,
    )

    assert member_capability is True
