from pydantic import BaseModel, field_validator
from schedule_manager.utils.datetime_validator import validate_datetime
from schedule_manager.common.missing import _Missing, MISSING
from datetime import datetime

class HolidayAddRequest(BaseModel):
    name:str
    description: str | None
    begin_at:datetime
    end_at:datetime

    @field_validator("begin_at")
    @classmethod
    def validate_begint_at(cls, value:datetime) -> datetime:
        return validate_datetime(value)
    @field_validator("end_at")
    @classmethod
    def validate_end_at(cls, value:datetime) -> datetime:
        return validate_datetime(value)

class HolidayUpdateRequest(BaseModel):
    name: str | _Missing = MISSING
    description: str | None | _Missing = MISSING
    begin_at: datetime | _Missing = MISSING
    end_at: datetime | _Missing = MISSING

    @field_validator("begin_at")
    @classmethod
    def validate_begin_at(cls, value: datetime) -> datetime:
        return validate_datetime(value)

    @field_validator("end_at")
    @classmethod
    def validate_end_at(cls, value: datetime) -> datetime:
        return validate_datetime(value)