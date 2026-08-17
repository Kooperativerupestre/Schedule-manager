import asyncio
from datetime import time, timezone

from schedule_manager.core.errors import OverlappingSchedulesError
from schedule_manager.workstations.schedules.repository import ScheduleRepository
from schedule_manager.workstations.schedules.models import ScheduleAddInput
from schedule_manager.workstations.schedules.ranges import ScheduleRange, DaySchedule
from schedule_manager.workstations.status import ScheduleStatus

async def test_same_workstation_schedule_interval_only_allows_one_insert(
    setup_conn, connections, person_factory, create_business_with_owner,
    create_unit_with_owner, create_workstation_with_owner,
) -> None:
    owner = await person_factory("schedule-owner", "schedule-owner-phone", setup_conn)
    business_id = await create_business_with_owner(owner.id, setup_conn)
    unit_id = await create_unit_with_owner(owner.id, business_id, setup_conn)
    workstation_id = await create_workstation_with_owner(owner.id, unit_id, setup_conn)
    await setup_conn.commit()
    schedule_range = ScheduleRange(
        begin=DaySchedule(day=1, hour=time(10, 0, 0, tzinfo=timezone.utc)),
        end=DaySchedule(day=1, hour=time(11, 0, 0, tzinfo=timezone.utc)),
    )
    
    async def insert_schedule(connection) -> None:
        async with connection.transaction():
            await ScheduleRepository.add(
                ScheduleAddInput(
                    workstation_id=workstation_id,
                    person_id=owner.id,
                    schedule_range=schedule_range,
                    status=ScheduleStatus.SCHEDULED,
                ),
                connection,
            )

    results = await asyncio.gather(*(insert_schedule(connection) for connection in connections), return_exceptions=True)

    assert results.count(None) == 1
    assert all(result is None or isinstance(result, OverlappingSchedulesError) for result in results)


async def test_same_person_schedule_interval_only_allows_one_insert(
    setup_conn, connections, person_factory, create_business_with_owner,
    create_unit_with_owner, create_workstation_with_owner,
) -> None:
    owner = await person_factory("same-person-owner", "same-person-owner-phone", setup_conn)
    business_id = await create_business_with_owner(owner.id, setup_conn)
    unit_id = await create_unit_with_owner(owner.id, business_id, setup_conn)
    first_workstation_id = await create_workstation_with_owner(owner.id, unit_id, setup_conn)
    second_workstation_id = await create_workstation_with_owner(owner.id, unit_id, setup_conn)
    await setup_conn.commit()
    schedule_range = ScheduleRange(
        begin=DaySchedule(day=1, hour=time(10, 0, 0, tzinfo=timezone.utc)),
        end=DaySchedule(day=1, hour=time(11, 0, 0, tzinfo=timezone.utc)),
    )

    async def insert_schedule(connection) -> None:
        async with connection.transaction():
            await ScheduleRepository.add(
                ScheduleAddInput(
                    workstation_id=second_workstation_id,
                    person_id=owner.id,
                    schedule_range=schedule_range,
                    status=ScheduleStatus.SCHEDULED,
                ),
                connection,
            )

    results = await asyncio.gather(*(insert_schedule(connection) for connection in connections), return_exceptions=True)

    assert results.count(None) == 1
    assert all(result is None or isinstance(result, OverlappingSchedulesError) for result in results)
