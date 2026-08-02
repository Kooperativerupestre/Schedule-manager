from pydantic import BaseModel, field_validator
from schedule_manager.utils.phone_validator import validate_phone
from schedule_manager.common.missing import _Missing, MISSING
from uuid import UUID

class UnitAddRequest(BaseModel):
    name:str
    business_id:UUID
    description:str | None
    phone_number:str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value:str) -> str | None:
        return validate_phone(value)
class UnitUpdateRequest(BaseModel):
    name:str | _Missing = MISSING
    description:str | None | _Missing = MISSING
    phone_number:str | _Missing = MISSING

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value:str | _Missing) -> str | _Missing:
        if not isinstance(value, str):
            return value
        return validate_phone(value)
    