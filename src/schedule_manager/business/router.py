from fastapi import APIRouter, Depends
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business.schemas import BusinessAddRequest, BusinessUpdateRequest
from schedule_manager.business.service import BusinessService
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope

router = APIRouter(prefix="/business", tags=["business"])


@router.post(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business:create:{person_id}",
                        capacity=10,
                        refill_rate=0.5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add(
    request: BusinessAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await BusinessService.add(person_id, request, conn)


@router.delete(
    "/{business_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business:delete:{person_id}",
                        capacity=10,
                        refill_rate=0.5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete(
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await BusinessService.delete(person_id, business_id, conn)


@router.patch(
    "/{business_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business:update:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def update(
    business_id: UUID,
    request: BusinessUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await BusinessService.update(person_id, business_id, request, conn)


@router.get(
    "/{business_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="business:get:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get(
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await BusinessService.get(person_id, business_id, conn)
