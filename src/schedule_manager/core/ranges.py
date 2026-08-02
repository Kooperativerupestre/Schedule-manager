from datetime import datetime, UTC
from psycopg.types.range import Range as DB_Range
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class BaseRange(ABC):
    @property
    @abstractmethod
    def to_db_range(self) -> DB_Range:
        ...

    @property
    @abstractmethod
    def is_valid_now(self) -> bool:
        ...


@dataclass(frozen=True)
class StrictRange(BaseRange):
    begin_date: datetime
    end_date: datetime

    def __post_init__(self):
        if self.end_date <= self.begin_date:
            raise ValueError("end_date must be after begin_date")

    @property
    def to_db_range(self) -> DB_Range:
        return DB_Range(self.begin_date, self.end_date, '[)')

    @property
    def is_valid_now(self) -> bool:
        now = datetime.now(UTC)
        return self.begin_date <= now < self.end_date


@dataclass(frozen=True)
class NormalRange(BaseRange):
    begin_date: datetime
    end_date: datetime | None

    def __post_init__(self):
        if self.end_date is not None and self.end_date <= self.begin_date:
            raise ValueError("end_date must be after begin_date")

    @property
    def to_db_range(self) -> DB_Range:
        return DB_Range(self.begin_date, self.end_date, '[)')

    @property
    def is_valid_now(self) -> bool:
        now = datetime.now(UTC)
        return self.begin_date <= now and (
            self.end_date is None or now < self.end_date
        )


def create_normal_range(
    begin_date: datetime | None,
    end_date: datetime | None
) -> NormalRange:
    if begin_date is None:
        begin_date = datetime.now(UTC)

    return NormalRange(begin_date, end_date)
def create_db_range(
    begin_date:datetime | None,
    end_date: datetime | None
) -> DB_Range:
    
    if begin_date is not None and begin_date.tzinfo is None or (end_date is not None and end_date.tzinfo is None):
        raise ValueError("datetime must have timezone")

    return DB_Range(begin_date, end_date, '[)')
def db_range_to_normal_range(range:DB_Range) -> NormalRange:
    return NormalRange(range.lower, range.upper) # type: ignore

def db_range_to_strict_range(range:DB_Range) -> StrictRange:
    if range.upper is None or range.lower is None:
        raise ValueError('range value(s) cannot be None')
    return StrictRange(range.lower, range.upper)

