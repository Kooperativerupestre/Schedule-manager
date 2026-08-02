from schedule_manager.utils.namespace import namespace
from schedule_manager.holidays.schemas import HolidayAddRequest, HolidayUpdateRequest
from schedule_manager.holidays.models import Holiday, HolidayChanges
from schedule_manager.core.ranges import StrictRange
from schedule_manager.common.missing import _Missing, MISSING

@namespace
class RequestTranslator:
    @staticmethod
    def add_request_to_holiday(request:HolidayAddRequest) -> Holiday:
        return Holiday(
            name=request.name,
            description=request.description,
            range=StrictRange(request.begin_at, request.end_at)
        )
    @staticmethod
    def update_request_to_holiday_changes(request: HolidayUpdateRequest) -> HolidayChanges:
        range: StrictRange | _Missing = MISSING

        if request.begin_at is not MISSING and request.end_at is not MISSING:
            range = StrictRange(request.begin_at, request.end_at)  # type: ignore

        return HolidayChanges(
            name=request.name,
            description=request.description,
            range=range,
        )
    

