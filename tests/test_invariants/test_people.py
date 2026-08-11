import pytest
from tests.helpers import GLOBAL_VALID_NUMBER
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.people.service import PeopleService
from schedule_manager.people.schemas import LocalPersonCreateRequest
from schedule_manager.core.errors import PhoneNumberAlreadyExistsError

async def test_duplicate_phone_number_error(
        conn:AsyncConnection[DictRow]
) -> None:
    await PeopleService.create_local(
        conn,
        LocalPersonCreateRequest(
            name='123',
            phone_number=GLOBAL_VALID_NUMBER,
            password='234'
        )
    )
    with pytest.raises(PhoneNumberAlreadyExistsError):
        await PeopleService.create_local(
            conn,
            LocalPersonCreateRequest(
                name='3123',
                phone_number=GLOBAL_VALID_NUMBER,
                password='234'
            )
        )
    