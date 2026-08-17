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


router = APIRouter(prefix="/workstation-exceptions", tags=["workstation-exceptions"])


@router.post("")
async def add(
    request: WorkstationExceptionAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await WorkstationExceptionService.add(person_id, request, conn)


@router.patch("/{workstation_id}")
async def update(
    workstation_id: UUID,
    request: WorkstationExceptionUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await WorkstationExceptionService.update(person_id, workstation_id, request, conn)


@router.delete("/{workstation_id}")
async def delete(
    workstation_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await WorkstationExceptionService.delete(person_id, workstation_id, conn)


@router.get("/{workstation_id}")
async def get(
    workstation_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await WorkstationExceptionService.get(person_id, workstation_id, conn)
