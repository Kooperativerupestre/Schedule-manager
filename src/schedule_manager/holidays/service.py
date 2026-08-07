from datetime import datetime

from schedule_manager.core.ranges.constants import STANDARD_YEAR
from schedule_manager.utils.namespace import namespace
from schedule_manager.holidays.schemas import HolidayAddRequest, HolidayUpdateRequest, HolidayRangeRequest, HolidayDatetimeRequest
from schedule_manager.holidays.models import Holiday, HolidayChanges, HolidayDatetime, HolidayRange
from schedule_manager.core.ranges.models import StrictRange
from schedule_manager.common.missing import _Missing, MISSING

@namespace
class RequestTranslator:
    @staticmethod
    def holiday_datetime_request_to_holiday_datetime(request:HolidayDatetimeRequest) -> HolidayDatetime:
        return HolidayDatetime(
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            second=request.second,
            microssecond=request.microssecond
        )
    @staticmethod
    def holiday_range_request_to_holiday_range(request:HolidayRangeRequest) -> HolidayRange:
        return HolidayRange(
            begin_at=RequestTranslator.holiday_datetime_request_to_holiday_datetime(request.begin_at),
            end_at=RequestTranslator.holiday_datetime_request_to_holiday_datetime(request.end_at)
        )

    @staticmethod
    def add_request_to_holiday(request:HolidayAddRequest) -> Holiday:
        return Holiday(
            name=request.name,
            description=request.description,
            range=RequestTranslator.holiday_range_request_to_holiday_range(request.validity_range)
        )
    @staticmethod
    def update_request_to_holiday_changes(request: HolidayUpdateRequest) -> HolidayChanges:
        range: HolidayRange | _Missing = MISSING

        if request.validity_range is not MISSING:
            assert not isinstance(request.validity_range, _Missing)
            range = RequestTranslator.holiday_range_request_to_holiday_range(request.validity_range)

        return HolidayChanges(
            name=request.name,
            description=request.description,
            range=range,
        )