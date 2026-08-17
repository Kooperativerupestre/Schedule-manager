import pytest
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.capabilities.errors import ForbiddenError
from schedule_manager.units.schemas import UnitAddRequest, UnitUpdateRequest
from schedule_manager.units.service import UnitService
from tests.helpers import GLOBAL_VALID_NUMBER


async def test_add_unit_without_business_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business,
) -> None:
    with pytest.raises(ForbiddenError):
        await UnitService.add(
            single_person.id,
            UnitAddRequest(
                name="Unit",
                business_id=business,
                description="test",
                phone_number=GLOBAL_VALID_NUMBER,
            ),
            conn,
        )


async def test_update_unit_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    stranger = await person_factory("stranger", "2000000000")

    with pytest.raises(ForbiddenError):
        await UnitService.update(
            stranger.id,
            unit_id,
            UnitUpdateRequest(
                name="Updated Unit",
                description="updated",
                phone_number=GLOBAL_VALID_NUMBER,
            ),
            conn,
        )


async def test_read_unit_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    stranger = await person_factory("stranger", "2000000000")

    with pytest.raises(ForbiddenError):
        await UnitService.get(stranger.id, unit_id, conn)


async def test_delete_unit_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    stranger = await person_factory("stranger", "2000000000")

    with pytest.raises(ForbiddenError):
        await UnitService.delete(stranger.id, business_id, unit_id, conn)


async def test_add_unit_with_permission(
    conn: AsyncConnection[DictRow],
    create_business_context,
) -> None:
    owner, business_id = await create_business_context()

    unit_id = await UnitService.add(
        owner.id,
        UnitAddRequest(
            name="Unit",
            business_id=business_id,
            description="test",
            phone_number=GLOBAL_VALID_NUMBER,
        ),
        conn,
    )

    assert unit_id is not None


async def test_manage_unit_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)

    await UnitService.update(
        owner.id,
        unit_id,
        UnitUpdateRequest(
            name="Updated Unit",
            description="updated",
            phone_number=GLOBAL_VALID_NUMBER,
        ),
        conn,
    )


async def test_read_unit_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)

    await UnitService.get(owner.id, unit_id, conn)


async def test_delete_unit_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)

    await UnitService.delete(owner.id, business_id, unit_id, conn)
