from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.errors import (
    BusinessForbiddenError,
    BusinessNotFoundError,
)
from schedule_manager.business.schemas import (
    BusinessAdd,
    BusinessCreateRequest,
    BusinessOwnerAssign,
    BusinessResponse,
)
from schedule_manager.business.service import BusinessService
from schedule_manager.database.connection import get_session

router = APIRouter(prefix="/businesses", tags=["businesses"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: UUID,
    requester_id: UUID,
    session: SessionDep,
) -> BusinessResponse:
    try:
        return await BusinessService.get(
            session,
            business_id,
            requester_id,
        )
    except BusinessForbiddenError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    except BusinessNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_business(
    business: BusinessCreateRequest,
    session: SessionDep,
) -> dict[str, UUID]:
    business_id = await BusinessService.create(
        session,
        BusinessAdd(name=business.name),
        business.creator_id,
    )
    return {"id": business_id}


@router.post(
    "/{business_id}/owners",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def assign_business_owner(
    business_id: UUID,
    assignment: BusinessOwnerAssign,
    session: SessionDep,
) -> Response:
    try:
        await BusinessService.assign_owner(
            session,
            business_id,
            assignment.owner_id,
            assignment.assigner_id,
        )
    except BusinessForbiddenError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{business_id}/owners/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_business_owner(
    business_id: UUID,
    owner_id: UUID,
    assigner_id: UUID,
    session: SessionDep,
) -> Response:
    try:
        await BusinessService.remove_owner(
            session,
            business_id,
            owner_id,
            assigner_id,
        )
    except BusinessForbiddenError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: UUID,
    assigner_id: UUID,
    session: SessionDep,
) -> Response:
    try:
        await BusinessService.delete(session, business_id, assigner_id)
    except BusinessForbiddenError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    except BusinessNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
