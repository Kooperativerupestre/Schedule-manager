import pytest
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.capabilities.errors import ForbiddenError
from schedule_manager.workstations.workstation.schemas import (
    WorkstationAddRequest,
    WorkstationUpdateRequest,
)
from schedule_manager.workstations.workstation.service import WorkstationService


async def test_add_workstation_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow], single_person, unit
) -> None:
    with pytest.raises(ForbiddenError):
        await WorkstationService.add(
            single_person.id,
            WorkstationAddRequest(
                unit_id=unit.id,
                name="Workstation",
                description="test",
            ),
            conn,
        )


async def test_update_workstation_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id)
    stranger = await person_factory("stranger", "2000000000")

    with pytest.raises(ForbiddenError):
        await WorkstationService.update(
            stranger.id,
            workstation_id,
            WorkstationUpdateRequest(
                name="Updated Workstation",
                description="updated",
            ),
            conn,
        )


async def test_read_workstation_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id)
    stranger = await person_factory("stranger", "2000000000")

    with pytest.raises(ForbiddenError):
        await WorkstationService.get(stranger.id, workstation_id, conn)


async def test_delete_workstation_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id)
    stranger = await person_factory("stranger", "2000000000")

    with pytest.raises(ForbiddenError):
        await WorkstationService.delete(stranger.id, unit_id, workstation_id, conn)


async def test_add_workstation_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)

    await WorkstationService.add(
        owner.id,
        WorkstationAddRequest(
            unit_id=unit_id,
            name="Workstation",
            description="test",
        ),
        conn,
    )


async def test_manage_workstation_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id)

    await WorkstationService.update(
        owner.id,
        workstation_id,
        WorkstationUpdateRequest(
            name="Updated Workstation",
            description="updated",
        ),
        conn,
    )


async def test_read_workstation_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    await create_workstation_with_owner(owner.id, unit_id)


async def test_delete_workstation_with_permission(
    conn: AsyncConnection[DictRow],
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
) -> None:
    owner = await person_factory("owner", "1000000000")
    business_id = await create_business_with_owner(owner.id)
    unit_id = await create_unit_with_owner(owner.id, business_id)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id)

    await WorkstationService.delete(owner.id, unit_id, workstation_id, conn)
