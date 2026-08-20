from fastapi import APIRouter, Depends
from schedule_manager.workstations.schedules.service import ScheduleService
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.workstations.schedules.schemas import (
    ScheduleAddRequest,
    ScheduleChangesRequest,
    ScheduleRangeRequest,
)
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope

router = APIRouter(
    prefix="/workstations-schedules", tags=["workstations-schedules"]
)


@router.post(
    "/{schedule_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-schedules:add:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add_workstation_schedule(
    request: ScheduleAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await ScheduleService.add(person_id, request, conn)


@router.delete(
    "/{workstation_id}/{schedule_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-schedules:delete:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete_workstation_schedule(
    workstation_id: UUID,
    schedule_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await ScheduleService.delete(person_id, workstation_id, schedule_id, conn)


@router.patch(
    "/{workstation_id}/{schedule_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-schedules:update:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def update_workstation_schedule(
    workstation_id: UUID,
    schedule_id: UUID,
    request: ScheduleChangesRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await ScheduleService.update(
        person_id, workstation_id, schedule_id, request, conn
    )


@router.get(
    "/{workstation_id}/{schedule_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-schedules:get:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get_workstation_schedule(
    workstation_id: UUID,
    schedule_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await ScheduleService.get(person_id, workstation_id, schedule_id, conn)


@router.get(
    "/can-schedule/{workstation_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-schedules:can-schedule:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def can_schedule(
    business_id: UUID,
    unit_id: UUID,
    workstation_id: UUID,
    validity_range: ScheduleRangeRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await ScheduleService.can_schedule(
        person_id, business_id, unit_id, workstation_id, validity_range, conn
    )
