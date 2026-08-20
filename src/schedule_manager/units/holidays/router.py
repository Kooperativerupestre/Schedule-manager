from fastapi import APIRouter, Depends
from schedule_manager.units.holidays.service import UnitHolidayService
from schedule_manager.holidays.schemas import HolidayAddRequest, HolidayUpdateRequest
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.holidays.schemas import HolidayRangeRequest
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope

router = APIRouter(prefix="/units-holidays", tags=["units-holidays"])


@router.post(
    "/{unit_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="units-holidays:add:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add_unit_holiday(
    unit_id: UUID,
    request: HolidayAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await UnitHolidayService.add(person_id, unit_id, request, conn)


@router.delete(
    "/{unit_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="units-holidays:delete:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete_unit_holiday(
    unit_id: UUID,
    holiday_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await UnitHolidayService.delete(person_id, unit_id, holiday_id, conn)


@router.patch(
    "/{unit_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="units-holidays:update:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def update_unit_holiday(
    unit_id: UUID,
    holiday_id: UUID,
    request: HolidayUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await UnitHolidayService.update(
        person_id, unit_id, holiday_id, request, conn
    )


@router.get(
    "/{unit_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="units-holidays:get:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get_unit_holiday(
    unit_id: UUID,
    holiday_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await UnitHolidayService.get(person_id, unit_id, holiday_id, conn)


@router.get(
    "/{unit_id}/has-overlapping-interval",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="units-holidays:overlap:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def has_overlapping_interval(
    unit_id: UUID,
    validity_range: HolidayRangeRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await UnitHolidayService.has_overlapping_interval(
        person_id, unit_id, validity_range, conn
    )
