from schedule_manager.utils.namespace import namespace
from schedule_manager.capabilities.capabilities import Resource
from schedule_manager.capabilities.validator import CapabilitiesValidator
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.units.holidays.repository import HolidayConfigUnitHolidays as HolidayRepositoryContext
from schedule_manager.holidays.repository import HolidayRepository, Holiday
from schedule_manager.holidays.service import RequestTranslator
from schedule_manager.holidays.schemas import HolidayAddRequest, HolidayUpdateRequest, HolidayRangeRequest
from schedule_manager.units.errors import UnitNotFoundError
from schedule_manager.utils.service_logging import log_service_errors, model_context
import logging

logger = logging.getLogger(__name__)

@log_service_errors
@namespace
class UnitHolidayService:
    @staticmethod
    async def add(person_id:UUID, unit_id:UUID, request:HolidayAddRequest, conn:AsyncConnection[DictRow]) -> UUID:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.UNIT_HOLIDAYS, unit_id, conn)
    
        id = await HolidayRepository.add(HolidayRepositoryContext, unit_id, RequestTranslator.add_request_to_holiday(request), conn)
        logger.info("unit_holiday.created", extra={"actor_id": str(person_id), "unit_id": str(unit_id), "holiday_id": str(id), "request": model_context(request)})
        return id
    @staticmethod
    async def delete(person_id:UUID, unit_id:UUID, holiday_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.UNIT_HOLIDAYS, unit_id, conn)

        has_deleted = await HolidayRepository.delete(HolidayRepositoryContext, holiday_id, conn)

        if not has_deleted:
            raise UnitNotFoundError
        logger.info("unit_holiday.deleted", extra={"actor_id": str(person_id), "unit_id": str(unit_id), "holiday_id": str(holiday_id)})
    @staticmethod
    async def update(person_id:UUID, unit_id:UUID, holiday_id:UUID, changes:HolidayUpdateRequest, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.UNIT_HOLIDAYS, unit_id, conn)

        has_updated = await HolidayRepository.update(HolidayRepositoryContext, holiday_id, RequestTranslator.update_request_to_holiday_changes(changes), conn)
        if not has_updated:
            raise UnitNotFoundError
        logger.info("unit_holiday.updated", extra={"actor_id": str(person_id), "unit_id": str(unit_id), "holiday_id": str(holiday_id), "request": model_context(changes)})
    @staticmethod
    async def get(person_id:UUID, unit_id:UUID, holiday_id:UUID, conn:AsyncConnection[DictRow]) -> Holiday | None:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.UNIT_HOLIDAYS, unit_id, conn)
        return await HolidayRepository.get(HolidayRepositoryContext, holiday_id, conn)
    @staticmethod
    async def has_overlapping_interval(person_id:UUID, unit_id:UUID, validity_range:HolidayRangeRequest, conn:AsyncConnection[DictRow]) -> bool:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.UNIT_HOLIDAYS, unit_id, conn)

        return await HolidayRepository.has_overlapping_interval(HolidayRepositoryContext, unit_id,
                            RequestTranslator.holiday_range_request_to_holiday_range(validity_range), conn)
