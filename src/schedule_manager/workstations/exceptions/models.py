from schedule_manager.workstations.schedules.ranges import ScheduleRange
from dataclasses import dataclass
from uuid import UUID
from psycopg.types.range import Range as DB_Range
from schedule_manager.workstations.status import ScheduleTimeStatus
from schedule_manager.common.missing import _Missing, MISSING


@dataclass(frozen=True)
class WorkstationExceptionRow:
    id: UUID
    workstation_id: UUID
    status: str
    exception_range: DB_Range
    description: str | None


@dataclass(frozen=True)
class WorkstationExceptionGetOutput:
    workstation_id: UUID
    status: ScheduleTimeStatus
    description: str | None
    range: ScheduleRange


@dataclass(frozen=True)
class WorkstationExceptionAddInput:
    workstation_id: UUID
    status: ScheduleTimeStatus
    description: str | None
    range: ScheduleRange


@dataclass(frozen=True)
class WorkstationExceptionAddOutput:
    id: UUID


@dataclass(frozen=True)
class WorkstationExceptionChanges:
    status: ScheduleTimeStatus | _Missing = MISSING
    description: str | None | _Missing = MISSING
    range: ScheduleRange | _Missing = MISSING
