from datetime import datetime, UTC
from psycopg.types.range import Range as DB_Range
from dataclasses import dataclass
from abc import ABC, abstractmethod
from schedule_manager.core.ranges.constants import (
    _DB_Begin,
    _NeverEnd,
    NEVER_END,
    DB_BEGIN,
)


@dataclass(frozen=True)
class BaseRange(ABC):
    @property
    @abstractmethod
    def to_db_range(self) -> DB_Range: ...

    @property
    @abstractmethod
    def is_valid_now(self) -> bool: ...


@dataclass(frozen=True)
class StrictRange(BaseRange):
    begin_date: datetime | _DB_Begin
    end_date: datetime

    def __post_init__(self):
        if isinstance(self.begin_date, datetime) and self.end_date <= self.begin_date:
            raise ValueError("end_date must be after begin_date")

    @property
    def to_db_range(self) -> DB_Range:
        return DB_Range(self.begin_date, self.end_date, "[)")

    @property
    def is_valid_now(self) -> bool:
        now = datetime.now(UTC)

        if isinstance(self.begin_date, datetime):
            return self.begin_date <= now < self.end_date

        return now < self.end_date


@dataclass(frozen=True)
class NormalRange(BaseRange):
    begin_date: datetime | _DB_Begin
    end_date: datetime | _NeverEnd

    def __post_init__(self):
        if (
            isinstance(self.begin_date, datetime)
            and isinstance(self.end_date, datetime)
            and self.end_date <= self.begin_date
        ):
            raise ValueError("end_date must be after begin_date")

    @property
    def to_db_range(self) -> DB_Range:
        return DB_Range(self.begin_date, self.end_date, "[)")

    @property
    def is_valid_now(self) -> bool:
        now = datetime.now(UTC)

        if isinstance(self.begin_date, datetime) and now < self.begin_date:
            return False

        if isinstance(self.end_date, datetime) and now >= self.end_date:
            return False

        return True


def create_normal_range(
    begin_date: datetime | _DB_Begin, end_date: datetime | _NeverEnd
) -> NormalRange:
    return NormalRange(begin_date, end_date)


def create_db_range(
    begin_date: datetime | _DB_Begin, end_date: datetime | _NeverEnd
) -> DB_Range:
    if (
        begin_date is not DB_BEGIN
        and begin_date.tzinfo is None
        or (end_date is not NEVER_END and end_date.tzinfo is None)
    ):
        raise ValueError("datetime must have timezone")

    new_begin_date = None if begin_date is DB_BEGIN else begin_date
    new_end_date = None if end_date is NEVER_END else end_date
    return DB_Range(new_begin_date, new_end_date, "[)")
