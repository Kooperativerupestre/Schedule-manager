from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from schedule_manager.common.missing import _Missing, MISSING

@dataclass(frozen=True)
class UnitRow:
    id:UUID
    business_id:UUID
    name:str
    description:str | None
    phone_number:str
    created_at:datetime

@dataclass(frozen=True)
class Unit:
    business_id:UUID
    name:str
    description:str | None
    phone_number: str


@dataclass(frozen=True)
class UnitAddOutput:
    id:UUID
    created_at:datetime
@dataclass(frozen=True)
class UnitGetOutput:
    id:UUID
    business_id:UUID
    name:str
    description:str | None
    phone_number:str
    created_at:datetime
@dataclass(frozen=True)
class UnitChanges:
    name:str | _Missing = MISSING
    description: str | None | _Missing = MISSING
    phone_number: str | _Missing = MISSING
    business_id:UUID | _Missing = MISSING
