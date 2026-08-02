from schedule_manager.utils.namespace import namespace
from schedule_manager.capabilities.service import CapabilitiesValidator
from uuid import UUID
from psycopg import AsyncConnection
from schedule_manager.capabilities.capabilities import Resource
from psycopg.rows import DictRow
@namespace
class BusinessValidator:
    @staticmethod
    async def validate_manage_business_capability(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.BUSINESS, business_id, conn)
    @staticmethod
    async def validate_read_business_capability(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.BUSINESS, business_id, conn)
