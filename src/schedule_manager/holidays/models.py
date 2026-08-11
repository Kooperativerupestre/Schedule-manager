from dataclasses import dataclass
from uuid import UUID
from schedule_manager.common.missing import _Missing
from schedule_manager.core.ranges.models import DB_Range
from schedule_manager.core.ranges.constants import STANDARD_YEAR
from datetime import datetime

class HolidayDatetime:
    def __init__(self, month:int, day:int, minute:int, hour:int, second:int, microssecond:int):
        self.value = datetime(
            year=STANDARD_YEAR,
            month=month,
            day=day,
            minute=minute,
            hour=hour,
            second=second,
            microsecond=microssecond
        )
@dataclass(frozen=True)
class HolidayRange:
    begin_at:HolidayDatetime
    end_at:HolidayDatetime

def holiday_range_to_db(holiday_range:HolidayRange) -> DB_Range:
    return DB_Range(
        lower=holiday_range.begin_at.value,
        upper=holiday_range.end_at.value
    )
def db_range_to_holiday_range(db_range:DB_Range) -> HolidayRange:
    assert db_range.lower is not None
    assert db_range.upper is not None
    begin = db_range.lower
    end = db_range.upper
    return HolidayRange(
        begin_at=HolidayDatetime(
            month=begin.month,
            day=begin.day,
            minute=begin.minute,
            hour=begin.hour,
            second=begin.second,
            microssecond=begin.microsecond
        ),
        end_at=HolidayDatetime(
            month=end.month,
            day=end.day,
            minute=end.minute,
            hour=end.hour,
            second=end.second,
            microssecond=end.microsecond
        )
    )
    
@dataclass(frozen=True)
class Holiday:
    name: str
    description: str | None
    range: HolidayRange


@dataclass(frozen=True)
class HolidayChanges:
    name: str | _Missing
    description: str | None | _Missing
    range: HolidayRange | _Missing


@dataclass(frozen=True)
class HolidayRow:
    owner_id: UUID
    name: str
    description: str | None
    holiday_range: DB_Range
