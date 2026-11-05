from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.database.connection import get_session
from schedule_manager.unit.memberships.errors import (
    UnitMembershipNotFoundError,
)
from schedule_manager.unit.memberships.schemas import (
    UnitMembershipAddRequest,
    UnitMembershipCreateResponse,
    UnitMembershipResponse,
)
from schedule_manager.unit.memberships.service import UnitMembershipService

router = APIRouter(
    prefix="/units/{unit_id}/memberships",
    tags=["unit memberships"],
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "",
    response_model=UnitMembershipCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": UnitMembershipCreateResponse}},
)
async def add_unit_member(
    unit_id: UUID,
    request: UnitMembershipAddRequest,
    session: SessionDep,
    current_user: CurrentUser,
    response: Response,
) -> UnitMembershipCreateResponse:
    created = await UnitMembershipService.add(
        session,
        unit_id,
        request.member_id,
        current_user.id,
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return UnitMembershipCreateResponse(created=created)


@router.get("/{member_id}", response_model=UnitMembershipResponse)
async def get_unit_membership(
    unit_id: UUID,
    member_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> UnitMembershipResponse:
    membership = await UnitMembershipService.get(
        session,
        unit_id,
        member_id,
        current_user.id,
    )
    if membership is None:
        raise UnitMembershipNotFoundError("Unit membership not found.")
    return UnitMembershipResponse.model_validate(membership)


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_unit_member(
    unit_id: UUID,
    member_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    removed = await UnitMembershipService.remove(
        session,
        unit_id,
        member_id,
        current_user.id,
    )
    if not removed:
        raise UnitMembershipNotFoundError("Unit membership not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
