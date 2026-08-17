from pydantic import BaseModel
from schedule_manager.common.missing import _Missing, MISSING


class HolidayDatetimeRequest(BaseModel):
    month: int
    day: int
    minute: int
    hour: int
    second: int
    microssecond: int


class HolidayRangeRequest(BaseModel):
    begin_at: HolidayDatetimeRequest
    end_at: HolidayDatetimeRequest


class HolidayAddRequest(BaseModel):
    name: str
    description: str | None
    validity_range: HolidayRangeRequest


class HolidayUpdateRequest(BaseModel):
    name: str | _Missing = MISSING
    description: str | None | _Missing = MISSING
    validity_range: HolidayRangeRequest | _Missing = MISSING
