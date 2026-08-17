import asyncio
from datetime import time, timezone

from schedule_manager.core.errors import OverlappingSchedulesError
from schedule_manager.workstations.exceptions.repository import (
    WorkstationExceptionsRepository,
)
from schedule_manager.workstations.exceptions.models import WorkstationExceptionAddInput
from schedule_manager.workstations.schedules.ranges import ScheduleRange, DaySchedule
from schedule_manager.workstations.status import ScheduleTimeStatus


async def test_same_exception_interval_only_allows_one_insert(
    setup_conn,
    connections,
    person_factory,
    create_business_with_owner,
    create_unit_with_owner,
    create_workstation_with_owner,
) -> None:
    owner = await person_factory("exception-owner", "exception-owner-phone", setup_conn)
    business_id = await create_business_with_owner(owner.id, setup_conn)
    unit_id = await create_unit_with_owner(owner.id, business_id, setup_conn)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id, setup_conn)
    await setup_conn.commit()
    exception_range = ScheduleRange(
        begin=DaySchedule(day=1, hour=time(10, 0, 0, tzinfo=timezone.utc)),
        end=DaySchedule(day=1, hour=time(11, 0, 0, tzinfo=timezone.utc)),
    )

    async def insert_exception(connection) -> None:
        async with connection.transaction():
            await WorkstationExceptionsRepository.add(
                WorkstationExceptionAddInput(
                    workstation_id=workstation_id,
                    status=ScheduleTimeStatus.AVAILABLE,
                    description="stress test",
                    range=exception_range,
                ),
                connection,
            )

    results = await asyncio.gather(
        *(insert_exception(connection) for connection in connections),
        return_exceptions=True,
    )

    assert results.count(None) == 1
    assert all(
        result is None or isinstance(result, OverlappingSchedulesError)
        for result in results
    )
