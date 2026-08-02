import re
from schedule_manager.core.errors import InvalidPhoneNumberError

def validate_phone(value:str) -> str:
    if not re.fullmatch(r"\+?1?\d{10}", value):
        raise InvalidPhoneNumberError("phone number {} is invalid".format(value))
    return value
