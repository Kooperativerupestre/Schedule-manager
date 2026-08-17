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


router = APIRouter(prefix="/memberships", tags=["memberships"])
invites_router = APIRouter(
    prefix="/memberships/invites", tags=["memberships-invites"]
)


@router.post("")
async def add(
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await MembershipService.add(person_id, target_person_id, business_id, conn)


@router.patch("")
async def end(
    target_person_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await MembershipService.end(person_id, target_person_id, business_id, conn)


@router.get("/has/{target_person_id}")
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


@router.get("/{target_person_id}")
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


@invites_router.post("")
async def add_invite(
    request: MembershipInviteRequest,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await MembershipInviteService.add(person_id, request, business_id, conn)


@invites_router.patch("/{invite_id}")
async def end_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await MembershipInviteService.end(person_id, invite_id, business_id, conn)


@invites_router.get("/{invite_id}")
async def get_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipInviteService.get(person_id, invite_id, business_id, conn)


@invites_router.get("/{invite_id}/has-ended")
async def has_ended_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipInviteService.has_ended(
        person_id, invite_id, business_id, conn
    )


@invites_router.get("/{invite_id}/has-expired")
async def has_expired_invite(
    invite_id: UUID,
    business_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await MembershipInviteService.has_expired(
        person_id, invite_id, business_id, conn
    )
