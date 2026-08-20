from fastapi import APIRouter, Depends
from schedule_manager.business.holidays.service import BusinessHolidayService
from schedule_manager.holidays.schemas import HolidayAddRequest, HolidayUpdateRequest
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope

router = APIRouter(prefix="/business-holidays", tags=["business-holidays"])


@router.post(
    "/{business_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business-holidays:add:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add_business_holiday(
    business_id: UUID,
    request: HolidayAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await BusinessHolidayService.add(person_id, business_id, request, conn)


@router.delete(
    "/{business_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business-holidays:delete:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete_business_holiday(
    business_id: UUID,
    holiday_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await BusinessHolidayService.delete(person_id, business_id, holiday_id, conn)


@router.patch(
    "/{business_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business-holidays:update:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def update_business_holiday(
    business_id: UUID,
    holiday_id: UUID,
    request: HolidayUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await BusinessHolidayService.update(
        person_id, business_id, holiday_id, request, conn
    )


@router.get(
    "/{business_id}/{holiday_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business-holidays:get:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get_business_holiday(
    business_id: UUID,
    holiday_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await BusinessHolidayService.get(person_id, business_id, holiday_id, conn)
