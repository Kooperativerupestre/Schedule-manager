from pydantic import BaseModel
from uuid import UUID

from schedule_manager.common.missing import _Missing, MISSING


class WorkstationAddRequest(BaseModel):
    unit_id: UUID
    name: str
    description: str | None


class WorkstationUpdateRequest(BaseModel):
    name: str | _Missing = MISSING
    description: str | None | _Missing = MISSING
