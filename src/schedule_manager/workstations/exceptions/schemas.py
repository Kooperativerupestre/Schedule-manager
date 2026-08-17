from pydantic import BaseModel
from schedule_manager.workstations.schedules.schemas import ScheduleRangeRequest
from uuid import UUID
from schedule_manager.common.missing import _Missing, MISSING
from schedule_manager.workstations.status import ScheduleTimeStatus


class WorkstationExceptionAddRequest(BaseModel):
    workstation_id: UUID
    range: ScheduleRangeRequest
    description: str | None
    status: ScheduleTimeStatus


class WorkstationExceptionUpdateRequest(BaseModel):
    range: ScheduleRangeRequest | _Missing = MISSING
    description: str | None | _Missing = MISSING
    status: ScheduleTimeStatus
