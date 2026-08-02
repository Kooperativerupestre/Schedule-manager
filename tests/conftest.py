import pytest_asyncio
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row, DictRow
from schedule_manager.config import settings
from schedule_manager.db.connection import get_connection
from schedule_manager.main import app
from typing import Generator
from fastapi.testclient import TestClient
import pytest
import psycopg
from psycopg import AsyncConnection
from schedule_manager.business.service import BusinessService
from uuid import UUID
from schedule_manager.business.schemas import BusinessAddRequest
from schedule_manager.people.repository import PeopleRepository
from schedule_manager.business.repository import BusinessRepository
from schedule_manager.business.models import Business
from schedule_manager.people.models import AddPersonInput

test_pool = AsyncConnectionPool(
    conninfo=settings.test_database_url,
    min_size=1,
    max_size=5,
    timeout=5,
    kwargs={"row_factory": dict_row},
    open=False
)

async def get_test_connection():
    async with test_pool.connection() as conn:
        async with conn.transaction() as tx:
            yield conn
            raise psycopg.Rollback(tx)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _manage_test_pool():
    await test_pool.open()

    print(test_pool.get_stats())

    yield

    await test_pool.close()
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_connection] = get_test_connection
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def conn():
    async with test_pool.connection() as connection:
        async with connection.transaction() as tx:
            yield connection
            raise psycopg.Rollback(tx)

# fixtures

GLOBAL_VALID_NUMBER = '2198765432'



@pytest.fixture
async def single_person(conn: AsyncConnection[DictRow]):
    return await PeopleRepository.add(
        conn,
        AddPersonInput(
            'Jépac',
            GLOBAL_VALID_NUMBER
        )
    )
@pytest.fixture

async def person_factory(conn: AsyncConnection[DictRow]):
    async def _create_person(name: str, phone_number: str):
        return await PeopleRepository.add(
            conn,
            AddPersonInput(
                name,
                phone_number
            ),
        )
    return _create_person


@pytest.fixture
async def business(conn: AsyncConnection[DictRow]):
    return await BusinessRepository.add(
        Business(
            'Business',
            'test',
            GLOBAL_VALID_NUMBER
        ),
        conn
    )
@pytest.fixture
async def create_business_with_owner(conn:AsyncConnection[DictRow]):
    async def _create(owner:UUID):

        business_id = await BusinessService.add(owner, BusinessAddRequest(name='213', description='3', phone_number=GLOBAL_VALID_NUMBER), conn)
        return business_id
    return _create