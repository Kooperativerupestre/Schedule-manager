from datetime import datetime, UTC
from pydantic import GetCoreSchemaHandler
from typing import Any
from pydantic_core import core_schema


class _DB_Begin:
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.is_instance_schema(cls)


class _NeverEnd:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)


DB_BEGIN = _DB_Begin()
NEVER_END = _NeverEnd()


STANDARD_YEAR = 2000
STANDARD_MONTH = 1
STANDARD_DTT_YEAR_MONTH = datetime(STANDARD_YEAR, STANDARD_MONTH, 1, tzinfo=UTC)
