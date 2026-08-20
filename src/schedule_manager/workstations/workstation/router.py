from uuid import UUID

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.auth.dependencies import get_current_person_id
from schedule_manager.db.connection import get_connection, get_transaction
from schedule_manager.workstations.workstation.schemas import (
    WorkstationAddRequest,
    WorkstationUpdateRequest,
)
from schedule_manager.workstations.workstation.service import WorkstationService
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope


router = APIRouter(prefix="/workstations", tags=["workstations"])


@router.post(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstations:add:{person_id}",
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
    request: WorkstationAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await WorkstationService.add(person_id, request, conn)


@router.delete(
    "/{unit_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstations:delete:{person_id}",
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
    unit_id: UUID,
    workstation_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await WorkstationService.delete(person_id, unit_id, workstation_id, conn)


@router.patch(
    "/{workstation_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstations:update:{person_id}",
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
    request: WorkstationUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await WorkstationService.update(person_id, workstation_id, request, conn)


@router.get(
    "/{workstation_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="workstations:get:{person_id}",
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
    return await WorkstationService.get(person_id, workstation_id, conn)
