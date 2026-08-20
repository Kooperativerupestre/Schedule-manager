from uuid import UUID

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.auth.dependencies import get_current_person_id
from schedule_manager.db.connection import get_connection, get_transaction
from schedule_manager.workstations.exceptions.schemas import (
    WorkstationExceptionAddRequest,
    WorkstationExceptionUpdateRequest,
)
from schedule_manager.workstations.exceptions.service import WorkstationExceptionService
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope


router = APIRouter(prefix="/workstation-exceptions", tags=["workstation-exceptions"])


@router.post(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-exceptions:add:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add(
    request: WorkstationExceptionAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await WorkstationExceptionService.add(person_id, request, conn)


@router.patch(
    "/{workstation_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-exceptions:update:{person_id}",
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
    workstation_id: UUID,
    request: WorkstationExceptionUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await WorkstationExceptionService.update(person_id, workstation_id, request, conn)


@router.delete(
    "/{workstation_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-exceptions:delete:{person_id}",
                        capacity=20,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete(
    workstation_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await WorkstationExceptionService.delete(person_id, workstation_id, conn)


@router.get(
    "/{workstation_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstation-exceptions:get:{person_id}",
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
    workstation_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await WorkstationExceptionService.get(person_id, workstation_id, conn)
