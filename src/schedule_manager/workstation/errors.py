from schedule_manager.core.errors import ForbiddenError, NotFoundError


class WorkstationForbiddenError(ForbiddenError):
    pass


class WorkstationNotFoundError(NotFoundError):
    pass
