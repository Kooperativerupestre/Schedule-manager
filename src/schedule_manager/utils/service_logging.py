import functools
import inspect
import logging
from enum import Enum
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar


T = TypeVar("T")


def _log_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (Enum,)):
        return value.name
    if hasattr(value, "model_dump"):
        return {
            key: _log_value(item)
            for key, item in value.model_dump(mode="json").items()
            if key not in {"password", "credentials"}
        }
    return str(value)


def model_context(model: Any) -> dict[str, Any]:
    """Return structured, non-sensitive request data suitable for log extras."""
    return {
        key: _log_value(value)
        for key, value in model.model_dump().items()
        if key not in {"password", "credentials"}
    }


def log_repository_error(repository: type[Any], operation: str, error: Exception, context: dict[str, Any]) -> None:
    """Log a repository failure using the same structured contract as services."""
    logger = logging.getLogger(repository.__module__)
    logger.exception(
        "repository.operation_failed",
        extra={
            "repository": repository.__name__,
            "operation": operation,
            "context": context,
            "error_type": type(error).__name__,
            "error": str(error),
        },
    )


def operation_context(func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    bound = inspect.signature(func).bind_partial(*args, **kwargs)
    return {
        key: _log_value(value)
        for key, value in bound.arguments.items()
        if key not in {"conn", "password"}
    }


def log_service_errors(cls: type[T]) -> type[T]:
    """Ensure every public service operation logs failures before re-raising."""
    logger = logging.getLogger(cls.__module__)

    for name, value in vars(cls).items():
        if name.startswith("_") or not isinstance(value, staticmethod):
            continue

        func = value.__func__
        if not callable(func):
            continue

        @functools.wraps(func)
        async def logged(
            *args: Any,
            __func: Callable[..., Awaitable[Any]] = func,
            __operation: str = name,
            **kwargs: Any,
        ) -> Any:
            try:
                return await __func(*args, **kwargs)
            except Exception as error:
                try:
                    context = operation_context(__func, args, kwargs)
                except Exception:
                    context = {"context_error": "failed_to_serialize_operation_context"}
                logger.exception(
                    "service.operation_failed",
                    extra={
                        "service": cls.__name__,
                        "operation": __operation,
                        "context": context,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    },
                )
                raise

        setattr(cls, name, staticmethod(logged))

    return cls
