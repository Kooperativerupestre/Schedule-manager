from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import DictRow

from schedule_manager.capabilities.capabilities import Resource
from schedule_manager.capabilities.service import CapabilitiesValidator
from schedule_manager.utils.namespace import namespace


@namespace
class WorkstationValidator:
    @staticmethod
    async def validate_manage_capability(person_id: UUID, workstation_id: UUID, conn: AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.WORKSTATION, workstation_id, conn)

    @staticmethod
    async def validate_read_capability(person_id: UUID, workstation_id: UUID, conn: AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.WORKSTATION, workstation_id, conn)
    