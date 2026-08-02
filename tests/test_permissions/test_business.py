from tests.helpers import GLOBAL_VALID_NUMBER
import pytest
from schedule_manager.business.service import BusinessService
from schedule_manager.business.schemas import BusinessUpdateRequest
from psycopg import AsyncConnection
from schedule_manager.capabilities.errors import ForbiddenError
from psycopg.rows import DictRow



## forbidden



async def test_delete_business_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business
) -> None:
    with pytest.raises(ForbiddenError):
        await BusinessService.delete(
            single_person.id,
            business,
            conn
        )


async def test_manage_business_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business
) -> None:
    with pytest.raises(ForbiddenError):
        await BusinessService.update(
            single_person.id,
            business,
            BusinessUpdateRequest(
            ),
            conn
        )


async def test_read_business_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business
) -> None:
    with pytest.raises(ForbiddenError):
        await BusinessService.get(
            single_person.id,
            business,
            conn
        )
async def test_update_business_without_permission_raises_forbidden(
    conn: AsyncConnection[DictRow],
    single_person,
    business
) -> None:
    with pytest.raises(ForbiddenError):
        await BusinessService.update(
            single_person.id,
            business,
            BusinessUpdateRequest(
                name='Updated Business',
                description='Updated description',
                phone_number=GLOBAL_VALID_NUMBER
            ),
            conn
        )

## allowed

async def test_delete_business_with_permission(
    conn:AsyncConnection[DictRow],
    single_person,
    create_business_with_owner
) -> None:
    
    business_id = await create_business_with_owner(single_person.id)
    await BusinessService.delete(
            single_person.id,
            business_id,
            conn
        )
async def test_manage_business_with_permission(
    conn:AsyncConnection[DictRow],
    single_person,
    create_business_with_owner
) -> None:
    
    business_id = await create_business_with_owner(single_person.id)
    await BusinessService.update(
            single_person.id,
            business_id,
            BusinessUpdateRequest(
                name='Updated Business',
                description='Updated description',
                phone_number='2198765432'
            ),
            conn
        )
async def test_read_business_with_permission(
    conn:AsyncConnection[DictRow],
    single_person,
    create_business_with_owner
) -> None:
    
    business_id = await create_business_with_owner(single_person.id)

async def test_update_business_with_permission(
        conn:AsyncConnection[DictRow],
        single_person,
        create_business_with_owner
) -> None:
    business_id = await create_business_with_owner(single_person.id)