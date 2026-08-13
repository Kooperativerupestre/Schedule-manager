from schedule_manager.utils.namespace import namespace
from schedule_manager.capabilities.capabilities import Resource
from schedule_manager.capabilities.validator import CapabilitiesValidator
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business.holidays.repository import HolidayConfigBusinessHolidays as HolidayRepositoryContext
from schedule_manager.holidays.repository import HolidayRepository, Holiday
from schedule_manager.holidays.service import RequestTranslator
from schedule_manager.holidays.schemas import HolidayAddRequest, HolidayUpdateRequest, HolidayRangeRequest
from schedule_manager.core.errors import NotFoundError
from schedule_manager.utils.service_logging import log_service_errors, model_context
import logging

logger = logging.getLogger(__name__)

@log_service_errors
@namespace
class BusinessHolidayService:
    @staticmethod
    async def add(person_id:UUID, business_id:UUID, request:HolidayAddRequest, conn:AsyncConnection[DictRow]) -> UUID:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)

        try:
            id = await HolidayRepository.add(HolidayRepositoryContext, business_id, RequestTranslator.add_request_to_holiday(request), conn)
            logger.info("business_holiday.created", extra={"actor_id": str(person_id), "business_id": str(business_id), "holiday_id": str(id), "request": model_context(request)})
            return id
        except Exception:
            raise
    @staticmethod
    async def delete(person_id:UUID, holiday_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)

        has_deleted = await HolidayRepository.delete(HolidayRepositoryContext, holiday_id, conn)

        if not has_deleted:
            raise NotFoundError
        logger.info("business_holiday.deleted", extra={"actor_id": str(person_id), "business_id": str(business_id), "holiday_id": str(holiday_id)})
    @staticmethod
    async def update(person_id:UUID, holiday_id:UUID, business_id:UUID, changes:HolidayUpdateRequest, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)

        has_updated = await HolidayRepository.update(HolidayRepositoryContext, holiday_id, RequestTranslator.update_request_to_holiday_changes(changes), conn)
        if not has_updated:
            raise NotFoundError
        await conn.commit()
        logger.info("business_holiday.updated", extra={"actor_id": str(person_id), "business_id": str(business_id), "holiday_id": str(holiday_id), "request": model_context(changes)})
    @staticmethod
    async def get(person_id:UUID, business_id:UUID, holiday_id:UUID, conn:AsyncConnection[DictRow]) -> Holiday | None:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)
        return await HolidayRepository.get(HolidayRepositoryContext, holiday_id, conn)
    @staticmethod
    async def has_overlapping_interval(person_id:UUID, business_id:UUID, validity_range:HolidayRangeRequest, conn:AsyncConnection[DictRow]) -> bool:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.BUSINESS_HOLIDAYS, business_id, conn)

        return await HolidayRepository.has_overlapping_interval(HolidayRepositoryContext, business_id,
                            RequestTranslator.holiday_range_request_to_holiday_range(validity_range), conn)
