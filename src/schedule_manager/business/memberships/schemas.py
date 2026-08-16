from pydantic import BaseModel, field_validator
from schedule_manager.utils.email_validator import validate_email
from schedule_manager.utils.datetime_validator import validate_datetime
from datetime import datetime

class EmailRequest(BaseModel):
    email:str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return validate_email(v)

class MembershipInviteRequest(BaseModel):
    email:str
    expires_at:datetime

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return validate_email(v)
    @field_validator("expires_at")
    @classmethod
    def validate(cls, v):
        return validate_datetime(v)
