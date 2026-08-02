from pydantic import BaseModel, field_validator
from schedule_manager.utils.phone_validator import validate_phone
from schedule_manager.common.missing import _Missing, MISSING

class PersonCreateRequest(BaseModel):
    name:str
    phone_number:str
    provider:str
    password:str
    identifier:str

class LocalPersonCreateRequest(BaseModel):
    name:str
    phone_number:str
    password:str

class PersonUpdateRequest(BaseModel):
    name:str | _Missing = MISSING
    phone_number:str | _Missing = MISSING
    status:bool | _Missing = MISSING

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value:str | _Missing) -> str | _Missing:
        if value is MISSING:
            return value
        return validate_phone(value)
