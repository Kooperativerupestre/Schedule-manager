from fastapi import APIRouter, HTTPException, Depends, Response
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.db.connection import get_connection, get_transaction
from schedule_manager.people.service import PeopleService, PersonNotFoundError
from schedule_manager.people.repository import PhoneNumberAlreadyExistsError
from schedule_manager.people.schemas import (
    PersonUpdateRequest,
    LocalPersonCreateRequest,
)
from schedule_manager.auth.dependencies import get_current_person_id
from schedule_manager.auth.cookies import set_cookie
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope


router = APIRouter(prefix="/people", tags=["people"])


@router.post(
    "/local",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="people:create:{ip}",
                        capacity=5,
                        refill_rate=0.2,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add_local(
    data: LocalPersonCreateRequest,
    response: Response,
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    try:
        r = await PeopleService.create_local(conn, data)
    except PhoneNumberAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    set_cookie(response, r.id)


@router.delete(
    "/",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="people:delete:{person_id}",
                        capacity=5,
                        refill_rate=0.2,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete(
    id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    try:
        r = await PeopleService.delete(conn, id)
        return r
    except PersonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500)


@router.patch(
    "/",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="people:update:{person_id}",
                        capacity=10,
                        refill_rate=0.5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def update(
    update: PersonUpdateRequest,
    id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    try:
        await PeopleService.update(conn, id, update)
    except PersonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500)


@router.get(
    "/",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="people:get:{person_id}",
                        capacity=30,
                        refill_rate=2,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get(
    id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    try:
        r = await PeopleService.get(conn, id)
        return r
    except PersonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
