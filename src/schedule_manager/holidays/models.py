from dataclasses import dataclass
from uuid import UUID
from schedule_manager.common.missing import _Missing
from schedule_manager.core.ranges import StrictRange, DB_Range
@dataclass(frozen=True)
class Holiday:
    name: str
    description: str | None
    range: StrictRange


@dataclass(frozen=True)
class HolidayChanges:
    name: str | _Missing
    description: str | None | _Missing
    range: StrictRange | _Missing


@dataclass(frozen=True)
class HolidayRow:
    owner_id: UUID
    name: str
    description: str | None
    holiday_range: DB_Range
