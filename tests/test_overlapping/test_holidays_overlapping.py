import asyncio

import pytest

from schedule_manager.business.holidays.repository import HolidayConfigBusinessHolidays
from schedule_manager.units.holidays.repository import HolidayConfigUnitHolidays
from schedule_manager.workstations.holidays.repository import (
    HolidayConfigWorkstationHolidays,
)
from schedule_manager.core.errors import OverlappingSchedulesError
from schedule_manager.holidays.models import Holiday, HolidayDatetime, HolidayRange
from schedule_manager.holidays.repository import HolidayRepository


@pytest.mark.parametrize(
    ("config", "owner_key"),
    [
        (HolidayConfigBusinessHolidays, "business_id"),
        (HolidayConfigUnitHolidays, "unit_id"),
        (HolidayConfigWorkstationHolidays, "workstation_id"),
    ],
)
async def test_same_holiday_interval_only_allows_one_insert(
    setup_conn,
    connections,
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
    config,
    owner_key: str,
) -> None:
    owner = await person_factory("holiday-owner", "holiday-owner-phone", setup_conn)

    business_id = await create_business_with_owner(owner.id, setup_conn)
    unit_id = await create_unit_with_owner(owner.id, business_id, setup_conn)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id, setup_conn)

    owner_ids = {
        "business_id": business_id,
        "unit_id": unit_id,
        "workstation_id": workstation_id,
    }

    holiday = Holiday(
        name="same holiday",
        description="stress test",
        range=HolidayRange(
            begin_at=HolidayDatetime(
                month=1, day=1, hour=10, minute=0, second=0, microssecond=0
            ),
            end_at=HolidayDatetime(
                month=1, day=1, hour=11, minute=0, second=0, microssecond=0
            ),
        ),
    )

    async def insert_holiday(connection) -> None:
        async with connection.transaction():
            await HolidayRepository.add(
                config=config,
                owner_id=owner_ids[owner_key],
                holiday=holiday,
                conn=connection,
            )

    results = await asyncio.gather(
        *(insert_holiday(connection) for connection in connections),
        return_exceptions=True,
    )

    assert results.count(None) == 1
    assert all(
        result is None or isinstance(result, OverlappingSchedulesError)
        for result in results
    )
