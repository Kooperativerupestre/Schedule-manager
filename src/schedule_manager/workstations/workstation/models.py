from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from schedule_manager.common.missing import _Missing, MISSING


@dataclass(frozen=True)
class WorkstationRow:
    id: UUID
    unit_id: UUID
    name: str
    description: str | None
    created_at: datetime


@dataclass(frozen=True)
class Workstation:
    unit_id: UUID
    name: str
    description: str | None


@dataclass(frozen=True)
class WorkstationChanges:
    name: str | _Missing = MISSING
    description: str | None | _Missing = MISSING
    unit_id: UUID | _Missing = MISSING


@dataclass(frozen=True)
class WorkstationAddOutput:
    id: UUID
    created_at: datetime


@dataclass(frozen=True)
class WorkstationGetOutput:
    id: UUID
    unit_id: UUID
    name: str
    description: str | None
    created_at: datetime
