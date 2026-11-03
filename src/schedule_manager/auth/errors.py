from schedule_manager.core.errors import UnauthorizedError


class AuthenticationInvalidCredentialsError(UnauthorizedError):
    pass


class AuthenticationSessionInvalidError(UnauthorizedError):
    pass
