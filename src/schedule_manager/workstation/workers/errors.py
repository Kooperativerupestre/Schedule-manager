from schedule_manager.core.errors import ForbiddenError, NotFoundError


class WorkerForbiddenError(ForbiddenError):
    pass


class WorkerNotFoundError(NotFoundError):
    pass
