from email_validator import EmailNotValidError, validate_email
from schedule_manager.core.errors import InvalidEmailError

def is_valid_email(email: str) -> str:
    try:
        validate_email(email, check_deliverability=False)
        return email
    except EmailNotValidError:
        raise InvalidEmailError("email {} is invalid".format(email))

    