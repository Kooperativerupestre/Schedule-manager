from schedule_manager.utils.namespace import namespace
from schedule_manager.workstations.schedules.repository import ScheduleRepository
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.workstations.schedules.schemas import (
    ScheduleAddRequest,
    ScheduleChangesRequest,
    ScheduleRangeRequest,
    ScheduleRequestTranslator,
)
from schedule_manager.workstations.schedules.models import (
    ScheduleAddInput,
    ScheduleChanges,
    ScheduleGetOutput,
)
from schedule_manager.workstations.schedules.ranges import (
    schedule_range_to_holiday_range,
)
from schedule_manager.common.missing import MISSING
from schedule_manager.capabilities.capabilities import Resource
from schedule_manager.capabilities.validator import CapabilitiesValidator
from uuid import UUID
from schedule_manager.workstations.schedules.errors import ScheduleNotFoundError
from enum import Enum, auto

# holidays
from schedule_manager.workstations.holidays.repository import HolidayConfigWorkstationHolidays
from schedule_manager.units.holidays.repository import HolidayConfigUnitHolidays
from schedule_manager.business.holidays.repository import HolidayConfigBusinessHolidays
from schedule_manager.holidays.repository import HolidayRepository


# exceptions

from schedule_manager.workstations.exceptions.repository import WorkstationExceptionsRepository
from schedule_manager.utils.service_logging import log_service_errors, model_context
import logging

logger = logging.getLogger(__name__)

# schedule returns

class ScheduleReturns(Enum):
    BUSINESS_HOLIDAY_OVERLAPPING = auto()
    UNIT_HOLIDAY_OVERLAPPING = auto()
    WORKSTATION_HOLIDAY_OVERLAPPING = auto()
    EXCEPTION_OVERLAPPING = auto()
    SCHEDULE_OVERLAPPING = auto()
    OK = auto()

@namespace
class RequestTranslator:
    @staticmethod
    def add_request_to_add_input(request:ScheduleAddRequest) -> ScheduleAddInput:
        return ScheduleAddInput(
            workstation_id=request.workstation_id,
            person_id=request.person_id,
            schedule_range=ScheduleRequestTranslator.schedule_range_request_to_schedule_range(request.schedule_range),
            status=request.status
        )
    @staticmethod
    def changes_request_to_changes(request:ScheduleChangesRequest) -> ScheduleChanges:
        return ScheduleChanges(
            person_id=request.person_id,
            schedule_range=ScheduleRequestTranslator.schedule_range_request_to_schedule_range(request.schedule_range) if request.schedule_range is not MISSING else MISSING,
            status=request.status
        )
@log_service_errors
@namespace
class ScheduleService:
    @staticmethod
    async def add(person_id:UUID, request:ScheduleAddRequest, conn:AsyncConnection[DictRow]) -> UUID:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.WORKSTATION_WORK, request.workstation_id, conn)

        schedule_id = await ScheduleRepository.add(
            RequestTranslator.add_request_to_add_input(request), conn
        )
        logger.info("schedule.created", extra={"actor_id": str(person_id), "workstation_id": str(request.workstation_id), "person_id": str(request.person_id), "schedule_id": str(schedule_id), "request": model_context(request)})
        return schedule_id
    @staticmethod
    async def delete(person_id:UUID, workstation_id:UUID, schedule_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.WORKSTATION_WORK, workstation_id, conn)

        r=  await ScheduleRepository.delete(schedule_id, conn)
        if not r:
            raise ScheduleNotFoundError
        logger.info("schedule.deleted", extra={"actor_id": str(person_id), "workstation_id": str(workstation_id), "schedule_id": str(schedule_id)})
    @staticmethod
    async def update(person_id:UUID, workstation_id:UUID, schedule_id:UUID, request:ScheduleChangesRequest, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, Resource.WORKSTATION_WORK, workstation_id, conn)

        r = await ScheduleRepository.update(
            schedule_id, RequestTranslator.changes_request_to_changes(request), conn
        )
        if not r:
            raise ScheduleNotFoundError
        logger.info("schedule.updated", extra={"actor_id": str(person_id), "workstation_id": str(workstation_id), "schedule_id": str(schedule_id), "request": model_context(request)})
    @staticmethod
    async def get(person_id:UUID, workstation_id:UUID, schedule_id:UUID, conn:AsyncConnection[DictRow]) -> ScheduleGetOutput | None:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.WORKSTATION_WORK, workstation_id, conn)

        return await ScheduleRepository.get(schedule_id, conn)
    @staticmethod
    async def can_schedule(
        person_id: UUID,
        business_id: UUID,
        unit_id: UUID,
        workstation_id: UUID,
        interval: ScheduleRangeRequest,
        conn: AsyncConnection[DictRow],
    ) -> ScheduleReturns:
        await CapabilitiesValidator.validate_read_capability(
            person_id,
            Resource.WORKSTATION_WORK,
            workstation_id,
            conn,
        )

        schedule_range = ScheduleRequestTranslator.schedule_range_request_to_schedule_range(interval)
        holiday_range = schedule_range_to_holiday_range(schedule_range)

        if await HolidayRepository.has_overlapping_interval(
            HolidayConfigBusinessHolidays,
            business_id,
            holiday_range,
            conn,
        ):
            logger.info("schedule.rejected", extra={"actor_id": str(person_id), "business_id": str(business_id), "unit_id": str(unit_id), "workstation_id": str(workstation_id), "reason": ScheduleReturns.BUSINESS_HOLIDAY_OVERLAPPING.name, "request": model_context(interval)})
            return ScheduleReturns.BUSINESS_HOLIDAY_OVERLAPPING

        if await HolidayRepository.has_overlapping_interval(
            HolidayConfigUnitHolidays,
            unit_id,
            holiday_range,
            conn,
        ):
            logger.info("schedule.rejected", extra={"actor_id": str(person_id), "business_id": str(business_id), "unit_id": str(unit_id), "workstation_id": str(workstation_id), "reason": ScheduleReturns.UNIT_HOLIDAY_OVERLAPPING.name, "request": model_context(interval)})
            return ScheduleReturns.UNIT_HOLIDAY_OVERLAPPING

        if await HolidayRepository.has_overlapping_interval(
            HolidayConfigWorkstationHolidays,
            workstation_id,
            holiday_range,
            conn,
        ):
            logger.info("schedule.rejected", extra={"actor_id": str(person_id), "business_id": str(business_id), "unit_id": str(unit_id), "workstation_id": str(workstation_id), "reason": ScheduleReturns.WORKSTATION_HOLIDAY_OVERLAPPING.name, "request": model_context(interval)})
            return ScheduleReturns.WORKSTATION_HOLIDAY_OVERLAPPING

        if await WorkstationExceptionsRepository.has_overlapping_interval(
            workstation_id,
            schedule_range,
            conn,
        ):
            logger.info("schedule.rejected", extra={"actor_id": str(person_id), "business_id": str(business_id), "unit_id": str(unit_id), "workstation_id": str(workstation_id), "reason": ScheduleReturns.EXCEPTION_OVERLAPPING.name, "request": model_context(interval)})
            return ScheduleReturns.SCHEDULE_OVERLAPPING

        if await ScheduleRepository.has_overlapping_interval(
            workstation_id,
            schedule_range,
            conn,
        ):
            logger.info("schedule.rejected", extra={"actor_id": str(person_id), "business_id": str(business_id), "unit_id": str(unit_id), "workstation_id": str(workstation_id), "reason": ScheduleReturns.SCHEDULE_OVERLAPPING.name, "request": model_context(interval)})
            return ScheduleReturns.SCHEDULE_OVERLAPPING

        return ScheduleReturns.OK
