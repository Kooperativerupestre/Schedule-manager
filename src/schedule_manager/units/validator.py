from schedule_manager.utils.namespace import namespace
from schedule_manager.capabilities.validator import CapabilitiesValidator
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.capabilities.capabilities import Resource


@namespace
class UnitValidator:
    @staticmethod
    async def validate_manage_capability(
        person_id: UUID, unit_id: UUID, conn: AsyncConnection[DictRow]
    ) -> None:
        await CapabilitiesValidator.validate_manage_capability(
            person_id, Resource.UNIT, unit_id, conn
        )

    @staticmethod
    async def validate_read_capability(
        person_id: UUID, unit_id: UUID, conn: AsyncConnection[DictRow]
    ) -> None:
        await CapabilitiesValidator.validate_read_capability(
            person_id, Resource.UNIT, unit_id, conn
        )

    @staticmethod
    async def validate_workstation_lifecycle_capability(
        person_id: UUID, unit_id: UUID, conn: AsyncConnection[DictRow]
    ) -> None:
        await CapabilitiesValidator.validate_manage_capability(
            person_id, Resource.WORKSTATION_LIFECYCLE, unit_id, conn
        )
