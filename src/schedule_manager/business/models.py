from dataclasses import dataclass
from schedule_manager.common.missing import _Missing, MISSING
from datetime import datetime


@dataclass(frozen=True)
class Business:
    name: str
    description: str | None
    phone_number: str | None


@dataclass(frozen=True)
class BusinessChanges:
    name: str | None | _Missing = MISSING
    description: str | None | _Missing = MISSING
    phone_number: str | None | _Missing = MISSING


@dataclass(frozen=True)
class BusinessRow:
    name: str
    description: str | None
    phone_number: str | None
    created_at: datetime


@dataclass(frozen=True)
class BusinessOutput:
    name: str
    description: str | None
    phone_number: str | None
    created_at: datetime
