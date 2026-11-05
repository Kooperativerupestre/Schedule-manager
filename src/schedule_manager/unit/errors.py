from schedule_manager.core.errors import ForbiddenError, NotFoundError


class UnitForbiddenError(ForbiddenError):
    pass


class UnitNotFoundError(NotFoundError):
    pass
