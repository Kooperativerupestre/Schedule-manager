from schedule_manager.core.errors import ForbiddenError, NotFoundError


class BusinessForbiddenError(ForbiddenError):
    pass


class BusinessNotFoundError(NotFoundError):
    pass
