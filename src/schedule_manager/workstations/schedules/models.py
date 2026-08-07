from uuid import UUID
from dataclasses import dataclass
from schedule_manager.workstations.schedules.ranges import ScheduleRange
from psycopg.types.range import Range as DB_Range
from schedule_manager.workstations.status import ScheduleStatus
from schedule_manager.common.missing import _Missing, MISSING

@dataclass(frozen=True)
class ScheduleRow:
    id:UUID
    workstation_id:UUID
    person_id:UUID
    schedule_range:DB_Range
    status:str
@dataclass(frozen=True)
class ScheduleAddInput:
    workstation_id:UUID
    person_id:UUID
    schedule_range:ScheduleRange
    status:ScheduleStatus = ScheduleStatus.SCHEDULED

@dataclass(frozen=True)
class ScheduleGetOutput:
    workstation_id:UUID
    person_id:UUID
    schedule_range:ScheduleRange
    status:ScheduleStatus
@dataclass(frozen=True)
class ScheduleChanges:
    person_id:UUID | _Missing = MISSING
    schedule_range: ScheduleRange | _Missing = MISSING
    status:ScheduleStatus | _Missing = MISSING
