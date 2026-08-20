from uuid import UUID

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.auth.dependencies import get_current_person_id
from schedule_manager.business.memberships.schemas import MembershipInviteRequest
from schedule_manager.business.memberships.service import (
    MembershipInviteService,
    MembershipService,
)
from schedule_manager.business.memberships.status import MembershipStatus
from schedule_manager.db.connection import get_connection, get_transaction
from schedule_manager.infraestructure.redis.dependencies import rate_limit
from schedule_manager.infraestructure.redis.redis import RateLimitScope


router = APIRouter(prefix="/memberships", tags=["memberships"])
invites_router = APIRouter(prefix="/memberships/invites", tags=["memberships-invites"])


@router.post(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="memberships:add:{person_id}",
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
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await MembershipService.add(person_id, target_person_id, business_id, conn)


@router.patch(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="memberships:end:{person_id}",
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
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await MembershipService.end(person_id, target_person_id, business_id, conn)


@router.get(
    "/has/{target_person_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="memberships:has:{person_id}",
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
    target_person_id: UUID,
    business_id: UUID,
    status: MembershipStatus | None = None,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipService.has(
        person_id, target_person_id, business_id, status, conn
    )


@router.get(
    "/{target_person_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="memberships:get:{person_id}",
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
    target_person_id: UUID,
    business_id: UUID,
    status: MembershipStatus | None = None,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipService.get(
        person_id, target_person_id, business_id, conn, status
    )


@invites_router.post(
    "",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="membership-invites:add:{person_id}",
                        capacity=15,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def add_invite(
    request: MembershipInviteRequest,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await MembershipInviteService.add(person_id, request, business_id, conn)


@invites_router.patch(
    "/{invite_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="membership-invites:end:{person_id}",
                        capacity=15,
                        refill_rate=1,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def end_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await MembershipInviteService.end(person_id, invite_id, business_id, conn)


@invites_router.get(
    "/{invite_id}",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="membership-invites:get:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def get_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipInviteService.get(person_id, invite_id, business_id, conn)


@invites_router.get(
    "/{invite_id}/has-ended",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="membership-invites:has-ended:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def has_ended_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipInviteService.has_ended(
        person_id, invite_id, business_id, conn
    )


@invites_router.get(
    "/{invite_id}/has-expired",
    dependencies=[
        Depends(
            rate_limit(
                [
                    RateLimitScope(
                        bucket_key="membership-invites:has-expired:{person_id}",
                        capacity=60,
                        refill_rate=5,
                        ttl=60,
                    )
                ]
            )
        )
    ],
)
async def has_expired_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipInviteService.has_expired(
        person_id, invite_id, business_id, conn
    )
