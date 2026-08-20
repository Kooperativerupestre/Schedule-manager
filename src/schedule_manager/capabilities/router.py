from fastapi import APIRouter, Depends
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from schedule_manager.capabilities.schemas import (
    CapabilityAddRequest,
    CapabilityEndRequest,
    CapabilityGetRequest,
)
from schedule_manager.capabilities.service import CapabilitiesService
from psycopg.rows import DictRow
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope

router = APIRouter(prefix="/capability", tags=["capability"])


@router.post(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="capabilities:add:{person_id}",
                        capacity=15,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add(
    request: CapabilityAddRequest,
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await CapabilitiesService.add(
        person_id, target_person_id, business_id, request, conn
    )


@router.patch(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="capabilities:end:{person_id}",
                        capacity=15,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def end(
    request: CapabilityEndRequest,
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await CapabilitiesService.end_all(
        person_id, target_person_id, business_id, request, conn
    )


@router.get(
    "/has/{target_id}/{capability}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="capabilities:has:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def has(
    request: CapabilityGetRequest,
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await CapabilitiesService.has(
        person_id, target_person_id, business_id, request, conn
    )


@router.get(
    "/all/{target_id}/{capability}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="capabilities:all:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get_all(
    request: CapabilityGetRequest,
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await CapabilitiesService.get_all(
        person_id, target_person_id, business_id, request, conn
    )


@router.get(
    "/last/{target_id}/{capability}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="capabilities:last:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get_last(
    request: CapabilityGetRequest,
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await CapabilitiesService.get_last(
        person_id, target_person_id, business_id, request, conn
    )
