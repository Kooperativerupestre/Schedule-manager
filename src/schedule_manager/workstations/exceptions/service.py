from schedule_manager.utils.namespace import namespace
from schedule_manager.workstations.exceptions.repository import WorkstationExceptionsRepository
from schedule_manager.workstations.exceptions.schemas import (
    WorkstationExceptionAddRequest,
    WorkstationExceptionUpdateRequest,
    
)
from schedule_manager.workstations.exceptions.models import WorkstationExceptionAddInput, WorkstationExceptionChanges, WorkstationExceptionGetOutput

from schedule_manager.workstations.schedules.schemas import ScheduleRequestTranslator as ScheduleRequestTranslator, ScheduleRangeRequest
from schedule_manager.common.missing import MISSING
from schedule_manager.capabilities.validator import CapabilitiesValidator
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.workstations.exceptions.errors import WorkstationExceptionNotFoundError
from schedule_manager.capabilities.capabilities import Resource

@namespace
class RequestTranslator:
    @staticmethod
    def add_request_to_workstation(request:WorkstationExceptionAddRequest) -> WorkstationExceptionAddInput:
        return WorkstationExceptionAddInput(
            workstation_id=request.workstation_id,
            status=request.status,
            description=request.description,
            range=ScheduleRequestTranslator.schedule_range_request_to_schedule_range(request.range)
        )
    @staticmethod
    def update_request_to_workstation(request:WorkstationExceptionUpdateRequest) -> WorkstationExceptionChanges:
        return WorkstationExceptionChanges(
            status=request.status,
            description=request.description,
            range=ScheduleRequestTranslator.schedule_range_request_to_schedule_range(request.range) if request.range is not MISSING else MISSING # type: ignore
        )

@namespace
class WorkstationExceptionService:
    @staticmethod
    async def add(person_id:UUID, request:WorkstationExceptionAddRequest, conn:AsyncConnection[DictRow]) -> UUID:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.WORKSTATION_WORK, request.workstation_id, conn)
        return await WorkstationExceptionsRepository.add(
            RequestTranslator.add_request_to_workstation(request), conn
        )
    @staticmethod
    async def update(person_id:UUID, workstation_id:UUID, request:WorkstationExceptionUpdateRequest, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.WORKSTATION_WORK, workstation_id, conn)
        r = await WorkstationExceptionsRepository.update(
            workstation_id, RequestTranslator.update_request_to_workstation(request), conn
        )
        if not r:
            raise WorkstationExceptionNotFoundError
    @staticmethod
    async def delete(person_id:UUID, workstation_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.WORKSTATION_WORK, workstation_id, conn)
        r = await WorkstationExceptionsRepository.delete(workstation_id, conn)
        if not r:
            raise WorkstationExceptionNotFoundError
    @staticmethod
    async def get(person_id:UUID, workstation_id:UUID, conn:AsyncConnection[DictRow]) -> WorkstationExceptionGetOutput | None:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.WORKSTATION_WORK, workstation_id, conn)
        return await WorkstationExceptionsRepository.get(workstation_id, conn)
    @staticmethod
    async def has_overlapping_interval(person_id:UUID, workstation_id:UUID, schedule:ScheduleRangeRequest, conn:AsyncConnection[DictRow]) -> bool:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.WORKSTATION_WORK, workstation_id, conn)

        return await WorkstationExceptionsRepository.has_overlapping_interval(workstation_id,
        ScheduleRequestTranslator.schedule_range_request_to_schedule_range(schedule), conn)
    