from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Response
from schedule_manager.auth.schemas import LocalLoginRequest
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.db.connection import get_transaction
from schedule_manager.auth.service import AuthenticationService, InvalidCredentialsError
from schedule_manager.auth.cookies import set_cookie, clear_cookie
from schedule_manager.auth.dependencies import get_current_person_id
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login/local",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="auth:login:{ip}",
                        capacity=5,
                        refill_rate=0.2,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def login_local(
    data: LocalLoginRequest,
    response: Response,
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    try:
        await AuthenticationService.local_login(conn, data.id, data.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    set_cookie(response, data.id)


@router.post(
    "/logout",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="auth:logout:{ip}",
                        capacity=10,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def logout(response: Response):
    clear_cookie(response)


@router.delete(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="auth:delete:{ip}",
                        capacity=5,
                        refill_rate=0.2,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def delete_authentication(
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
    id: UUID = Depends(get_current_person_id),
):
    if id is None:
        raise HTTPException(status_code=400, detail="Missing authentication id")
    deleted = await AuthenticationService.delete(conn, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Authentication not found")
    return {"detail": "Authentication deleted"}
