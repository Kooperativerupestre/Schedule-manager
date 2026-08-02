from schedule_manager.capabilities.repository import CapabilitiesRepository
from schedule_manager.utils.namespace import namespace
from schedule_manager.capabilities.capabilities import Resource, Action, Capability
from schedule_manager.capabilities.errors import ForbiddenError
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow

@namespace
class CapabilitiesValidator:
    @staticmethod
    async def validate(person_id:UUID, target_id:UUID, capability:Capability, conn:AsyncConnection[DictRow]) -> None:
        if not await CapabilitiesRepository.has(person_id, target_id, capability, conn):
            raise ForbiddenError
    @staticmethod
    async def validate_manage_capability(person_id:UUID, resource:Resource, target_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        capability = Capability(resource, Action.MANAGE)
        await CapabilitiesValidator.validate(person_id, target_id, capability, conn)
    @staticmethod
    async def validate_read_capability(person_id:UUID, resource:Resource, target_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        capability = Capability(resource, Action.READ)
        await CapabilitiesValidator.validate(person_id, target_id, capability, conn)
    