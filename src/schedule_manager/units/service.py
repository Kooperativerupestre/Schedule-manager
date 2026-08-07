from schedule_manager.utils.namespace import namespace
from schedule_manager.units.models import UnitGetOutput, Unit, UnitChanges
from schedule_manager.units.repository import UnitRepository
from schedule_manager.units.schemas import UnitAddRequest, UnitUpdateRequest
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business.validator import BusinessValidator
from schedule_manager.units.validator import UnitValidator
from schedule_manager.common.missing import MISSING
from schedule_manager.units.errors import UnitNotFoundError
from schedule_manager.capabilities.capabilities import Capability, Resource, Action
from schedule_manager.capabilities.repository import CapabilitiesRepository
from schedule_manager.capabilities.models import CapabilityInput
from schedule_manager.core.ranges.constants import NEVER_END

@namespace
class RequestTranslator:
    @staticmethod
    def add_request_to_unit(request:UnitAddRequest) -> Unit:
        return Unit(
            name=request.name,
            business_id=request.business_id,
            description=request.description,
            phone_number=request.phone_number,
        )
    @staticmethod
    def update_request_to_changes(request:UnitUpdateRequest) -> UnitChanges:
        return UnitChanges(
            name=request.name,
            description=request.description,
            phone_number=request.phone_number,
            business_id=MISSING
        )

@namespace
class UnitService:
    @staticmethod
    async def add(person_id:UUID, unit:UnitAddRequest, conn:AsyncConnection[DictRow]) -> UUID:
        await BusinessValidator.validate_unit_lifecycle(person_id, unit.business_id, conn)

        response = await UnitRepository.add(
            RequestTranslator.add_request_to_unit(unit),
            conn
        )
        await CapabilitiesRepository.add(person_id, response.id, CapabilityInput(Resource.UNIT, Action.MANAGE, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, response.id, CapabilityInput(Resource.UNIT, Action.READ, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, response.id, CapabilityInput(Resource.WORKSTATION_LIFECYCLE, Action.MANAGE, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, response.id, CapabilityInput(Resource.UNIT_HOLIDAYS, Action.MANAGE, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, response.id, CapabilityInput(Resource.UNIT_HOLIDAYS, Action.READ, NEVER_END), conn)
        return response.id
    @staticmethod
    async def delete(person_id:UUID, business_id:UUID, unit_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await BusinessValidator.validate_unit_lifecycle(person_id, business_id, conn)

        r =  await UnitRepository.delete(
            unit_id,
            conn
        )
        if not r:
            raise UnitNotFoundError

    @staticmethod
    async def update(person_id:UUID, unit_id:UUID, request:UnitUpdateRequest, conn:AsyncConnection[DictRow]) -> None:
        await UnitValidator.validate_manage_capability(person_id, unit_id, conn)

        r =  await UnitRepository.update(
            unit_id,
            RequestTranslator.update_request_to_changes(request),
            conn
        )
        if not r:
            raise UnitNotFoundError
    @staticmethod
    async def get(person_id:UUID, unit_id:UUID, conn:AsyncConnection[DictRow]) -> UnitGetOutput | None:
        await UnitValidator.validate_read_capability(person_id, unit_id, conn)

        return await UnitRepository.get(unit_id, conn)

