from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from schedule_manager.core.errors import (
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)


async def handle_unauthorized_error(
    request: Request,
    error: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(error)},
    )


async def handle_forbidden_error(
    request: Request,
    error: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(error)},
    )


async def handle_not_found_error(
    request: Request,
    error: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UnauthorizedError, handle_unauthorized_error)
    app.add_exception_handler(ForbiddenError, handle_forbidden_error)
    app.add_exception_handler(NotFoundError, handle_not_found_error)
