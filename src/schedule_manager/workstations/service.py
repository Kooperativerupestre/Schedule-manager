from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.units.validator import UnitValidator
from schedule_manager.common.missing import MISSING
from schedule_manager.utils.namespace import namespace
from schedule_manager.workstations.errors import WorkstationNotFoundError
from schedule_manager.workstations.models import Workstation, WorkstationChanges, WorkstationGetOutput
from schedule_manager.workstations.repository import WorkstationRepository
from schedule_manager.workstations.schemas import WorkstationAddRequest, WorkstationUpdateRequest
from schedule_manager.workstations.validator import WorkstationValidator
from schedule_manager.capabilities.repository import CapabilitiesRepository
from schedule_manager.capabilities.models import CapabilityInput
from schedule_manager.capabilities.capabilities import Resource, Action


@namespace
class RequestTranslator:
    @staticmethod
    def add_request_to_workstation(request: WorkstationAddRequest) -> Workstation:
        return Workstation(
            unit_id=request.unit_id,
            name=request.name,
            description=request.description,
        )

    @staticmethod
    def update_request_to_changes(request: WorkstationUpdateRequest) -> WorkstationChanges:
        fields = request.model_fields_set
        return WorkstationChanges(
            name=request.name if "name" in fields else MISSING,
            description=request.description if "description" in fields else MISSING,
        )


@namespace
class WorkstationService:
    @staticmethod
    async def add(person_id: UUID, request: WorkstationAddRequest, conn: AsyncConnection[DictRow]) -> UUID:
        await UnitValidator.validate_workstation_lifecycle_capability(person_id, request.unit_id, conn)
        response = await WorkstationRepository.add(RequestTranslator.add_request_to_workstation(request), conn)

        await CapabilitiesRepository.add(person_id, response.id, CapabilityInput(Resource.WORKSTATION, Action.MANAGE, None), conn)
        await CapabilitiesRepository.add(person_id, response.id, CapabilityInput(Resource.WORKSTATION, Action.READ, None), conn)
        return response.id

    @staticmethod
    async def delete(person_id: UUID, unit_id: UUID, workstation_id: UUID, conn: AsyncConnection[DictRow]) -> None:
        await UnitValidator.validate_workstation_lifecycle_capability(person_id, unit_id, conn)
        r = await WorkstationRepository.delete(workstation_id, conn)
        if not r:
            raise WorkstationNotFoundError

    @staticmethod
    async def update(person_id: UUID, workstation_id: UUID, request: WorkstationUpdateRequest, conn: AsyncConnection[DictRow]) -> None:
        await WorkstationValidator.validate_manage_capability(person_id, workstation_id, conn)
        r = await WorkstationRepository.update(workstation_id, RequestTranslator.update_request_to_changes(request), conn)
        if not r:
            raise WorkstationNotFoundError

    @staticmethod
    async def get(person_id: UUID, workstation_id: UUID, conn: AsyncConnection[DictRow]) -> WorkstationGetOutput | None:
        await WorkstationValidator.validate_read_capability(person_id, workstation_id, conn)
        return await WorkstationRepository.get(workstation_id, conn)
