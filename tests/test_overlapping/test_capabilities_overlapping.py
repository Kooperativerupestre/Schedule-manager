import asyncio

import pytest
from schedule_manager.core.errors import OverlappingSchedulesError
from schedule_manager.capabilities.repository import CapabilitiesRepository
from schedule_manager.capabilities.models import CapabilityInput
from schedule_manager.capabilities.capabilities import Resource, Action
from schedule_manager.core.ranges.constants import NEVER_END

async def test_same_capability_interval_only_allows_one_insert(
    setup_conn,
    connections,
    person_factory,
    create_business_with_owner,
) -> None:
    owner = await person_factory(
        "capability-owner",
        "capability-owner-phone",
        setup_conn,
    )
    member = await person_factory(
        "capability-member",
        "capability-member-phone",
        setup_conn,
    )
    business_id = await create_business_with_owner(owner.id, setup_conn)

    async def insert_capability(connection) -> None:
        async with connection.transaction():
            await CapabilitiesRepository.add(
                member.id,
                business_id,
                CapabilityInput(Resource.BUSINESS_HOLIDAYS, Action.MANAGE, NEVER_END),
                connection
            )
        

    results = await asyncio.gather(
        *(insert_capability(connection) for connection in connections),
        return_exceptions=True,
    )

    assert results.count(None) == 1
    assert all(
        result is None or isinstance(result, OverlappingSchedulesError)
        for result in results
    )
