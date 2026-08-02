from fastapi import APIRouter, Depends
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business.schemas import BusinessAddRequest, BusinessUpdateRequest
from schedule_manager.business.service import BusinessService

router = APIRouter(prefix='/business', tags=['business'])

@router.post('')
async def add(request:BusinessAddRequest, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_transaction)):
    await BusinessService.add(person_id, request, conn)
@router.delete('/{business_id}')
async def delete(business_id:UUID, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_transaction)):
    await BusinessService.delete(person_id, business_id, conn)
@router.patch('/{business_id}')
async def update(business_id:UUID, request:BusinessUpdateRequest, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_transaction)):
    await BusinessService.update(person_id, business_id, request, conn)
@router.get('/{business_id}')
async def get(business_id:UUID, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_connection)):
    return await BusinessService.get(person_id, business_id, conn)