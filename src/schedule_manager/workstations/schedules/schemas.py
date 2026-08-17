from schedule_manager.utils.namespace import namespace
from pydantic import BaseModel, field_validator
from datetime import time
from schedule_manager.workstations.schedules.ranges import ScheduleRange, DaySchedule
from uuid import UUID
from schedule_manager.workstations.status import ScheduleStatus
from schedule_manager.common.missing import _Missing, MISSING


class DayScheduleRangeRequest(BaseModel):
    day: int
    hour: time

    @classmethod
    @field_validator("day")
    def validate_day(cls, value: int) -> int:
        if value < 0 or value > 20:
            raise ValueError("Value must be >0 and <=20")
        return value


class ScheduleRangeRequest(BaseModel):
    begin: DayScheduleRangeRequest
    end: DayScheduleRangeRequest


@namespace
class ScheduleRequestTranslator:
    @staticmethod
    def schedule_range_request_to_schedule_range(
        request: ScheduleRangeRequest,
    ) -> ScheduleRange:
        return ScheduleRange(
            begin=DaySchedule(day=request.begin.day, hour=request.begin.hour),
            end=DaySchedule(day=request.end.day, hour=request.end.hour),
        )

    @staticmethod
    def day_schedule_range_request_to_day_schedule(
        request: DayScheduleRangeRequest,
    ) -> DaySchedule:
        return DaySchedule(day=request.day, hour=request.hour)


class ScheduleAddRequest(BaseModel):
    workstation_id: UUID
    person_id: UUID
    status: ScheduleStatus = ScheduleStatus.SCHEDULED
    schedule_range: ScheduleRangeRequest


class ScheduleChangesRequest(BaseModel):
    person_id: UUID | _Missing = MISSING
    schedule_range: ScheduleRangeRequest | _Missing = MISSING
    status: ScheduleStatus | _Missing = MISSING
