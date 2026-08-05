from schedule_manager.utils.namespace import namespace
from schedule_manager.capabilities.capabilities import Scope, Resource, Capability, Action
from schedule_manager.capabilities.validator import CapabilitiesValidator
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business.holidays.repository import HolidayConfigBusinesslHolidays as HolidayRepositoryContext
from schedule_manager.holidays.repository import HolidayRepository, Holiday
from schedule_manager.holidays.service import RequestTranslator
from schedule_manager.holidays.schemas import HolidayAddRequest, HolidayUpdateRequest
from schedule_manager.core.errors import NotFoundError


@namespace
class BusinessHolidayService:
    @staticmethod
    async def add(person_id:UUID, business_id:UUID, request:HolidayAddRequest, conn:AsyncConnection[DictRow]) -> UUID:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)

        try:
            id = await HolidayRepository.add(HolidayRepositoryContext, business_id, RequestTranslator.add_request_to_holiday(request), conn)
            return id
        except Exception:
            raise
    @staticmethod
    async def delete(person_id:UUID, holiday_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)

        has_deleted = await HolidayRepository.delete(HolidayRepositoryContext, holiday_id, conn)

        if not has_deleted:
            raise NotFoundError
    @staticmethod
    async def update(person_id:UUID, holiday_id:UUID, business_id:UUID, changes:HolidayUpdateRequest, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)

        has_updated = await HolidayRepository.update(HolidayRepositoryContext, holiday_id, RequestTranslator.update_request_to_holiday_changes(changes), conn)
        if not has_updated:
            raise NotFoundError
        await conn.commit()
    @staticmethod
    async def get(person_id:UUID, business_id:UUID, holiday_id:UUID, conn:AsyncConnection[DictRow]) -> Holiday | None:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)
        return await HolidayRepository.get(HolidayRepositoryContext, holiday_id, conn)
