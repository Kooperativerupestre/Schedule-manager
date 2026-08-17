from dataclasses import dataclass
from datetime import time, timedelta, timezone, UTC
from psycopg.types.range import Range
from schedule_manager.core.ranges.constants import STANDARD_DTT_YEAR_MONTH
from schedule_manager.holidays.models import HolidayRange, HolidayDatetime


@dataclass(frozen=True)
class DaySchedule:
    day: int
    hour: time

    @property
    def timezone(self) -> timezone:
        return UTC

    def __post_init__(self) -> None:
        if self.day < 0 or self.day > 20:
            raise ValueError(f"Day of value {self.day} must be >0 and <20")
        if self.hour.tzinfo != UTC:
            raise ValueError("Timezone is different from UTC")


@dataclass(frozen=True)
class ScheduleRange:
    begin: DaySchedule
    end: DaySchedule


def schedule_range_to_holiday_range(schedule: ScheduleRange) -> HolidayRange:
    return HolidayRange(
        begin_at=HolidayDatetime(
            month=schedule.begin.day,
            day=schedule.begin.hour.hour,
            minute=schedule.begin.hour.minute,
            hour=schedule.begin.hour.second,
            second=schedule.begin.hour.microsecond,
            microssecond=schedule.begin.hour.microsecond,
        ),
        end_at=HolidayDatetime(
            month=schedule.end.day,
            day=schedule.end.hour.hour,
            minute=schedule.end.hour.minute,
            hour=schedule.end.hour.second,
            second=schedule.end.hour.microsecond,
            microssecond=schedule.end.hour.microsecond,
        ),
    )


def convert_to_db_range(schedule: ScheduleRange) -> Range:
    begin = STANDARD_DTT_YEAR_MONTH
    begin += timedelta(
        days=schedule.begin.day,
        seconds=schedule.begin.hour.second,
        microseconds=schedule.begin.hour.microsecond,
        minutes=schedule.begin.hour.minute,
        hours=schedule.begin.hour.hour,
    )

    end = STANDARD_DTT_YEAR_MONTH
    end += timedelta(
        days=schedule.end.day,
        seconds=schedule.end.hour.second,
        microseconds=schedule.end.hour.microsecond,
        minutes=schedule.end.hour.minute,
        hours=schedule.end.hour.hour,
    )
    return Range(begin, end)


def convert_to_schedule_range(db_range: Range) -> ScheduleRange:
    assert db_range.lower is not None
    assert db_range.upper is not None

    begin_delta = db_range.lower - STANDARD_DTT_YEAR_MONTH
    end_delta = db_range.upper - STANDARD_DTT_YEAR_MONTH

    begin_hours, begin_remainder = divmod(begin_delta.seconds, 3600)
    begin_minutes, begin_seconds = divmod(begin_remainder, 60)

    end_hours, end_remainder = divmod(end_delta.seconds, 3600)
    end_minutes, end_seconds = divmod(end_remainder, 60)

    begin = DaySchedule(
        day=begin_delta.days,
        hour=time(begin_hours, begin_minutes, begin_seconds, begin_delta.microseconds),
    )
    end = DaySchedule(
        day=end_delta.days,
        hour=time(end_hours, end_minutes, end_seconds, end_delta.microseconds),
    )

    return ScheduleRange(begin=begin, end=end)
