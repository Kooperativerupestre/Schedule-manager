from enum import Enum, auto
from typing import Any

class ScheduleTimeStatus(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()
    AVAILABLE = auto()
    UNAVAILABLE = auto()

class ScheduleStatus(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return name.lower()
    SCHEDULED = auto()
    CANCELLED = auto()
    COMPLETED = auto()
