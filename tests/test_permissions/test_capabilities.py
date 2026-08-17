import pytest
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.capabilities.capabilities import Action, Resource
from schedule_manager.capabilities.errors import ForbiddenError
from schedule_manager.capabilities.service import CapabilitiesService
from schedule_manager.capabilities.schemas import (
    CapabilityGetRequest,
    CapabilityAddRequest,
    CapabilityEndRequest,
)
from schedule_manager.core.ranges.constants import NEVER_END
from schedule_manager.business.memberships.service import MembershipService


async def test_read_capability_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await CapabilitiesService.has(
            single_person.id,
            single_person.id,
            business,
            CapabilityGetRequest(
                resource=Resource.BUSINESS, action=Action.READ, target_id=business
            ),
            conn,
        )


async def test_add_capability_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await CapabilitiesService.add(
            single_person.id,
            single_person.id,
            business,
            CapabilityAddRequest(
                resource=Resource.BUSINESS,
                action=Action.MANAGE,
                target_id=business,
                end_at=NEVER_END,
            ),
            conn,
        )


async def test_end_all_capability_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await CapabilitiesService.end_all(
            single_person.id,
            business,
            business,
            CapabilityEndRequest(
                resource=Resource.BUSINESS, action=Action.MANAGE, target_id=business
            ),
            conn,
        )


async def test_end_capability_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await CapabilitiesService.end(
            single_person.id, single_person.id, business, conn
        )


async def test_get_all_capability_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    business,
) -> None:
    A = await person_factory("31", "1111", conn)
    B = await person_factory("32", "111123", conn)

    with pytest.raises(ForbiddenError):
        await CapabilitiesService.get_all(
            A.id,
            B.id,
            business,
            CapabilityGetRequest(
                resource=Resource.BUSINESS, action=Action.READ, target_id=business
            ),
            conn,
        )


async def test_get_last_capability_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    business,
) -> None:
    A = await person_factory("31", "1111", conn)
    B = await person_factory("32", "111123", conn)
    with pytest.raises(ForbiddenError):
        await CapabilitiesService.get_last(
            A.id,
            B.id,
            business,
            CapabilityGetRequest(
                resource=Resource.BUSINESS, action=Action.READ, target_id=business
            ),
            conn,
        )


async def test_add_capability_grants_capabilities_permissions(
    conn: AsyncConnection[DictRow],
    single_person,
    create_business_with_owner,
) -> None:
    business_id = await create_business_with_owner(single_person.id)

    manage_capability = await CapabilitiesService.has(
        single_person.id,
        single_person.id,
        business_id,
        CapabilityGetRequest(
            resource=Resource.CAPABILITIES,
            action=Action.MANAGE,
            target_id=business_id,
        ),
        conn,
    )

    read_capability = await CapabilitiesService.has(
        single_person.id,
        single_person.id,
        business_id,
        CapabilityGetRequest(
            resource=Resource.CAPABILITIES,
            action=Action.READ,
            target_id=business_id,
        ),
        conn,
    )

    assert manage_capability is True
    assert read_capability is True


async def test_add_capability_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    A = await person_factory("A", "1111111111")
    B = await person_factory("B", "2222222222")
    business_id = await create_business_with_owner(A.id)

    await MembershipService.add(A.id, B.id, business_id, conn)
    await CapabilitiesService.add(
        A.id,
        B.id,
        business_id,
        CapabilityAddRequest(
            resource=Resource.UNIT_LIFECYCLE,
            action=Action.MANAGE,
            target_id=business_id,
        ),
        conn,
    )


async def test_end_all_capability_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
) -> None:
    A = await person_factory("A", "1111111111")
    B = await person_factory("B", "2222222222")
    business_id = await create_business_with_owner(A.id)

    await MembershipService.add(A.id, B.id, business_id, conn)
    await CapabilitiesService.add(
        A.id,
        B.id,
        business_id,
        CapabilityAddRequest(
            resource=Resource.UNIT_LIFECYCLE,
            action=Action.MANAGE,
            target_id=business_id,
        ),
        conn,
    )
    await CapabilitiesService.end_all(
        A.id,
        B.id,
        business_id,
        CapabilityEndRequest(
            resource=Resource.UNIT_LIFECYCLE,
            action=Action.MANAGE,
            target_id=business_id,
        ),
        conn,
    )


async def test_end_capability_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    A = await person_factory("A", "1111111111")
    B = await person_factory("B", "2222222222")
    business_id = await create_business_with_owner(A.id)

    await MembershipService.add(A.id, B.id, business_id, conn)
    await CapabilitiesService.add(
        A.id,
        B.id,
        business_id,
        CapabilityAddRequest(
            resource=Resource.UNIT_LIFECYCLE,
            action=Action.MANAGE,
            target_id=business_id,
        ),
        conn,
    )


async def test_get_all_capability_with_permission(
    conn: AsyncConnection[DictRow],
    single_person,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    business_id = await create_business_with_owner(single_person.id)
    unit_id = await create_unit_with_owner(single_person.id, business_id)

    await CapabilitiesService.get_all(
        single_person.id,
        single_person.id,
        business_id,
        CapabilityGetRequest(
            resource=Resource.UNIT, action=Action.MANAGE, target_id=unit_id
        ),
        conn,
    )


async def test_get_last_capability_with_permission(
    conn: AsyncConnection[DictRow],
    single_person,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    business_id = await create_business_with_owner(single_person.id)
    unit_id = await create_unit_with_owner(single_person.id, business_id)

    await CapabilitiesService.get_last(
        single_person.id,
        single_person.id,
        business_id,
        CapabilityGetRequest(
            resource=Resource.UNIT, action=Action.MANAGE, target_id=unit_id
        ),
        conn,
    )
