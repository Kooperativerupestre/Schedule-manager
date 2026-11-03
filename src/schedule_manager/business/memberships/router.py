from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.dependencies import CurrentUser
from schedule_manager.business.memberships.errors import MembershipNotFoundError
from schedule_manager.business.memberships.schemas import (
    MembershipAddRequest,
    MembershipCreateResponse,
    MembershipResponse,
)
from schedule_manager.business.memberships.service import MembershipService
from schedule_manager.database.connection import get_session

router = APIRouter(
    prefix="/businesses/{business_id}/memberships",
    tags=["business memberships"],
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "",
    response_model=MembershipCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": MembershipCreateResponse}},
)
async def add_business_member(
    business_id: UUID,
    request: MembershipAddRequest,
    session: SessionDep,
    current_user: CurrentUser,
    response: Response,
) -> MembershipCreateResponse:
    created = await MembershipService.add(
        session,
        business_id,
        request.member_id,
        current_user.id,
    )

    if not created:
        response.status_code = status.HTTP_200_OK
    return MembershipCreateResponse(created=created)


@router.get(
    "/{member_id}",
    response_model=MembershipResponse,
)
async def get_business_membership(
    business_id: UUID,
    member_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> MembershipResponse:
    membership = await MembershipService.get(
        session,
        business_id,
        member_id,
        current_user.id,
    )

    if membership is None:
        raise MembershipNotFoundError("Business membership not found.")
    return MembershipResponse.model_validate(membership)


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_business_member(
    business_id: UUID,
    member_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    removed = await MembershipService.remove(
        session,
        business_id,
        member_id,
        current_user.id,
    )

    if not removed:
        raise MembershipNotFoundError("Business membership not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
