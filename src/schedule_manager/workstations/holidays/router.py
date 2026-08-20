from fastapi import APIRouter, Depends
from schedule_manager.workstations.holidays.service import WorkstationHolidayService
from schedule_manager.holidays.schemas import (
    HolidayAddRequest as WorkstationHolidayAddRequest,
    HolidayUpdateRequest as WorkstationHolidayUpdateRequest,
)
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope

router = APIRouter(prefix="/workstation-holidays", tags=["workstation-holidays"])


@router.post(
    "/{workstation_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-holidays:add:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add_workstation_holiday(
    workstation_id: UUID,
    request: WorkstationHolidayAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await WorkstationHolidayService.add(person_id, workstation_id, request, conn)


@router.patch(
    "/{workstation_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-holidays:update:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def update_workstation_holiday(
    workstation_id: UUID,
    holiday_id: UUID,
    request: WorkstationHolidayUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await WorkstationHolidayService.update(
        person_id, workstation_id, holiday_id, request, conn
    )


@router.delete(
    "/{workstation_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-holidays:delete:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete_workstation_holiday(
    workstation_id: UUID,
    holiday_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await WorkstationHolidayService.delete(
        person_id, workstation_id, holiday_id, conn
    )


@router.get(
    "/{workstation_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-holidays:get:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get_workstation_holiday(
    workstation_id: UUID,
    holiday_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await WorkstationHolidayService.get(
        person_id, workstation_id, holiday_id, conn
    )
