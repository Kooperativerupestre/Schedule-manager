import asyncio
import pytest_asyncio
from psycopg.rows import DictRow, dict_row
from schedule_manager.db.connection import get_connection
from schedule_manager.main import app
from typing import Generator
from fastapi.testclient import TestClient
import pytest
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
from schedule_manager.db.connection import (
    get_test_connection_auto_rollback,
    settings,
    get_test_connection,
    test_pool,
)
from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack

@pytest_asyncio.fixture(scope="session", autouse=True)
async def _manage_test_pool():
    await test_pool.open()

    yield

    await test_pool.close()
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_connection] = get_test_connection_auto_rollback
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def conn() -> AsyncGenerator[AsyncConnection[DictRow], None]:
    async with get_test_connection_auto_rollback() as connection:
        yield connection
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
    async def _create_person(name: str, phone_number: str, connection:AsyncConnection[DictRow] | None = None):
        _conn = connection if connection is not None else conn
        person = await PeopleRepository.add(
            _conn,
            AddPersonInput(
                name,
                phone_number
            ),
        )
        if connection is not None:
            await connection.commit()
        return person
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
    async def _create(owner:UUID, connection:AsyncConnection[DictRow] | None = None):
        _conn = connection if connection is not None else conn
        business_id = await BusinessService.add(owner, BusinessAddRequest(name='213', description='3', phone_number=GLOBAL_VALID_NUMBER), _conn)
        if connection is not None:
            await connection.commit()
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
    async def _create(owner_id: UUID, business_id: UUID, connection:AsyncConnection[DictRow] | None = None):
        _conn = connection if connection is not None else conn
        unit = await UnitService.add(
            owner_id,
            UnitAddRequest(
                name='Unit',
                business_id=business_id,
                description='test',
                phone_number=GLOBAL_VALID_NUMBER,
            ),
            _conn,
        )
        if connection is not None:
            await connection.commit()
        return unit

    return _create

@pytest.fixture
async def create_workstation_with_owner(conn: AsyncConnection[DictRow]):
    async def _create(owner_id: UUID, unit_id: UUID, connection:AsyncConnection[DictRow] | None = None):
        _conn = connection if connection is not None else conn
        workstation_id = await WorkstationService.add(
            owner_id,
            WorkstationAddRequest(
                unit_id=unit_id,
                name='Workstation',
                description='test',
            ),
            _conn,
        )
        if connection is not None:
            await connection.commit()
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



@pytest_asyncio.fixture
async def connections() -> AsyncGenerator[list[AsyncConnection[DictRow]], None]:
    async with AsyncExitStack() as stack:
        connections = [
            await stack.enter_async_context(
                get_test_connection()
            )
            for _ in range(2)
        ]

        yield connections


@pytest_asyncio.fixture
async def setup_conn() -> AsyncGenerator[AsyncConnection[DictRow], None]:
    async with get_test_connection() as connection:
        yield connection

@pytest_asyncio.fixture(autouse=True)
async def truncate_overlapping_tables():
    yield

    async with test_pool.connection() as connection:
        await connection.execute(
            """
            TRUNCATE TABLE
                business_membership_invites,
                business_memberships,
                person_capabilities,
                business_holidays,
                unit_holidays,
                workstation_holidays,
                schedules,
                workstation_exceptions,
                workstations,
                units,
                businesses,
                people
            CASCADE
            """
        )

        await connection.commit()
