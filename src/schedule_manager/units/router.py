from fastapi import APIRouter, Depends
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.units.schemas import UnitAddRequest, UnitUpdateRequest
from schedule_manager.units.service import UnitService


router = APIRouter(prefix="/units", tags=["units"])


@router.post("")
async def add(
    request: UnitAddRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    return await UnitService.add(person_id, request, conn)


@router.delete("/{business_id}")
async def delete(
    business_id: UUID,
    unit_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await UnitService.delete(person_id, business_id, unit_id, conn)


@router.patch("/{unit_id}")
async def update(
    unit_id: UUID,
    request: UnitUpdateRequest,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_transaction),
):
    await UnitService.update(person_id, unit_id, request, conn)


@router.get("/{unit_id}")
async def get(
    unit_id: UUID,
    person_id: UUID = Depends(get_current_person_id),
    conn: AsyncConnection[DictRow] = Depends(get_connection),
):
    return await UnitService.get(person_id, unit_id, conn)
