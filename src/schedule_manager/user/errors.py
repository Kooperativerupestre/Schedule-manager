from schedule_manager.core.errors import ForbiddenError, NotFoundError


class UserForbiddenError(ForbiddenError):
    pass


class UserNotFoundError(NotFoundError):
    pass
