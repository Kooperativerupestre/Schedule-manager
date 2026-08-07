from schedule_manager.utils.namespace import namespace
from schedule_manager.core.ranges.models import StrictRange, NormalRange
from schedule_manager.workstations.schedules.models import ScheduleRange
from psycopg.types.range import Range as DB_Range
from datetime import datetime
from schedule_manager.core.ranges.constants import STANDARD_YEAR, STANDARD_MONTH

@namespace
class RangeConverts:
    @staticmethod
    def db_range_to_normal_range(range:DB_Range) -> NormalRange:
        return NormalRange(range.lower, range.upper) # type: ignore

    @staticmethod
    def db_range_to_strict_range(range:DB_Range) -> StrictRange:
        if range.upper is None or range.lower is None:
            raise ValueError('range value(s) cannot be None')
        return StrictRange(range.lower, range.upper)

    @staticmethod
    def schedule_range_to_strict_range(range:ScheduleRange) -> StrictRange:
        return StrictRange(
            begin_date=datetime(
                year=STANDARD_YEAR,
                month=STANDARD_MONTH,
                day=range.begin.day,
                hour=range.begin.hour.hour,
                minute=range.begin.hour.minute,
                second=range.begin.hour.second,
                microsecond=range.begin.hour.microsecond
            ),
            end_date=datetime(
                year=STANDARD_YEAR,
                month=STANDARD_MONTH,
                day=range.end.day,
                hour=range.end.hour.hour,
                minute=range.end.hour.minute,
                second=range.end.hour.second,
                microsecond=range.end.hour.microsecond
            )
        )
    