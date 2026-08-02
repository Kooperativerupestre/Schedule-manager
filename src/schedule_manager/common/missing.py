
from typing import Any
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import TypeVar, NoReturn

class _Missing:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "MISSING"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)

MISSING = _Missing()


class MissingValueError(Exception):
    pass

T = TypeVar("T")

def raise_missing() -> NoReturn:
    raise MissingValueError

def resolve_optional(value:T | None | _Missing) -> T | None:
    if value is MISSING:
        raise_missing()
    return value
