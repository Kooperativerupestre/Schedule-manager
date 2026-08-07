from pydantic import BaseModel, field_validator
from schedule_manager.utils.datetime_validator import validate_datetime
from schedule_manager.common.missing import _Missing, MISSING
from datetime import datetime
from schedule_manager.core.ranges.constants import DB_BEGIN, _DB_Begin, NEVER_END, _NeverEnd


class StrictRangeRequest(BaseModel):
    begin_at:datetime | _DB_Begin = DB_BEGIN
    end_at:datetime

    @field_validator('begin_at')
    @classmethod
    def validate_begin(cls, value:datetime | _DB_Begin) -> datetime | _DB_Begin:
        if value is DB_BEGIN:
            return DB_BEGIN
        assert not isinstance(value, _DB_Begin)
        return validate_datetime(value)
    @field_validator('end_at')
    @classmethod
    def validate_end(cls, value:datetime) -> datetime:
        return validate_datetime(value)

class NormalRangeRequest(BaseModel):
    begin_at:datetime | _DB_Begin = DB_BEGIN
    end_at: datetime | _NeverEnd = NEVER_END

    @field_validator('begin_at')
    @classmethod
    def validate_begin(cls, value:datetime | _DB_Begin) -> datetime | _DB_Begin:
        if value is DB_BEGIN:
            return DB_BEGIN
        assert not isinstance(value, _DB_Begin)
        return validate_datetime(value)
    @field_validator('end_at')
    @classmethod
    def validate_end(cls, value:datetime | _NeverEnd) -> datetime | _NeverEnd:
        if value is NEVER_END:
            return NEVER_END
        assert not isinstance(value, _NeverEnd)
        return validate_datetime(value)
    