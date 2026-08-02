from fastapi import APIRouter, Depends
from schedule_manager.auth.dependencies import get_current_person_id
from uuid import UUID
from schedule_manager.db.connection import get_connection, get_transaction
from psycopg import AsyncConnection
from schedule_manager.capabilities.schemas import CapabilityAddRequest, CapabilityEndRequest, CapabilityGetRequest
from schedule_manager.capabilities.service import CapabilitiesService
from psycopg.rows import DictRow

router = APIRouter(prefix='/capability', tags=['capability'])

@router.post('')
async def add(request:CapabilityAddRequest, target_person_id:UUID, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_transaction)):
    await CapabilitiesService.add(person_id, target_person_id, request, conn)

@router.patch('')
async def end(request:CapabilityEndRequest, target_person_id:UUID, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_transaction)):
    await CapabilitiesService.end_all(person_id, target_person_id, request, conn)

@router.get('/has/{target_id}/{capability}')
async def has(request:CapabilityGetRequest, target_person_id:UUID, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_connection)):
    return await CapabilitiesService.has(person_id, target_person_id, request, conn)

@router.get('/all/{target_id}/{capability}')
async def get_all(request:CapabilityGetRequest, target_person_id:UUID, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_connection)):
    return await CapabilitiesService.get_all(person_id, target_person_id, request, conn)

@router.get('/last/{target_id}/{capability}')
async def get_last(request:CapabilityGetRequest, target_person_id:UUID, person_id:UUID = Depends(get_current_person_id), conn:AsyncConnection[DictRow] = Depends(get_connection)):
    return await CapabilitiesService.get_last(person_id, target_person_id, request, conn)

