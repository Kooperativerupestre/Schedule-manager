from pydantic import BaseModel, field_validator
from schedule_manager.utils.email_validator import validate_email
class EmailRequest(BaseModel):
    email:str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return validate_email(v)