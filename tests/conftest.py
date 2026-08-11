import pytest_asyncio
from psycopg.rows import DictRow
from schedule_manager.db.connection import get_connection
from schedule_manager.main import app
from typing import Generator
from fastapi.testclient import TestClient
import pytest
import psycopg
from psycopg import AsyncConnection
from schedule_manager.business.service import BusinessService
from schedule_manager.units.service import UnitService
from schedule_manager.workstations.workstation.service import WorkstationService
from schedule_manager.capabilities.repository import CapabilitiesRepository
from schedule_manager.capabilities.capabilities import Resource, Action
from schedule_manager.units.models import Unit
from schedule_manager.capabilities.models import CapabilityInput
from schedule_manager.units.repository import UnitRepository
from uuid import UUID
from schedule_manager.business.schemas import BusinessAddRequest
from schedule_manager.units.schemas import UnitAddRequest
from schedule_manager.workstations.workstation.schemas import WorkstationAddRequest
from schedule_manager.people.repository import PeopleRepository
from schedule_manager.business.repository import BusinessRepository
from schedule_manager.business.models import Business
from schedule_manager.people.models import AddPersonInput
from schedule_manager.core.ranges.constants import NEVER_END
from schedule_manager.db.connection import test_pool, get_test_connection

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
async def unit(business, conn:AsyncConnection[DictRow]):
    return await UnitRepository.add(
        Unit(
            business,
            '234',
            '234',
            GLOBAL_VALID_NUMBER
        ),  conn
    )
@pytest.fixture
async def create_business_with_owner(conn:AsyncConnection[DictRow]):
    async def _create(owner:UUID):

        business_id = await BusinessService.add(owner, BusinessAddRequest(name='213', description='3', phone_number=GLOBAL_VALID_NUMBER), conn)
        return business_id
    return _create

@pytest.fixture
async def create_business_context(conn: AsyncConnection[DictRow], person_factory):
    async def _create():
        owner = await person_factory('owner', '1111111111')
        business_id = await BusinessService.add(
            owner.id,
            BusinessAddRequest(name='Business', description='test', phone_number=GLOBAL_VALID_NUMBER),
            conn,
        )
        return owner, business_id

    return _create


@pytest.fixture
async def create_unit_with_owner(conn: AsyncConnection[DictRow]):
    async def _create(owner_id: UUID, business_id: UUID):
        unit = await UnitService.add(
            owner_id,
            UnitAddRequest(
                name='Unit',
                business_id=business_id,
                description='test',
                phone_number=GLOBAL_VALID_NUMBER,
            ),
            conn,
        )
        return unit

    return _create

@pytest.fixture
async def create_workstation_with_owner(conn: AsyncConnection[DictRow]):
    async def _create(owner_id: UUID, unit_id: UUID):
        workstation_id = await WorkstationService.add(
            owner_id,
            WorkstationAddRequest(
                unit_id=unit_id,
                name='Workstation',
                description='test',
            ),
            conn,
        )
        return workstation_id

    return _create


@pytest.fixture
async def grant_capability(conn: AsyncConnection[DictRow]):
    async def _grant(person_id: UUID, target_id: UUID, resource: Resource, action: Action):
        return await CapabilitiesRepository.add(
            person_id,
            target_id,
            CapabilityInput(resource=resource, action=action, end_at=NEVER_END),
            conn,
        )

    return _grant
