from dataclasses import dataclass
from datetime import datetime
from schedule_manager.common.missing import _Missing
from uuid import UUID

@dataclass(frozen=True)
class AddPersonInput:
    name: str
    phone_number: str

@dataclass(frozen=True)
class AddPersonOutput:
    id: UUID
    created_at: datetime

@dataclass(frozen=True)
class GetPerson:
    name: str
    phone_number: str
    id: UUID
    created_at: datetime
    status: bool
@dataclass(frozen=True)
class UpdatePerson:
    name:str | _Missing
    phone_number:str | _Missing
    status:bool | _Missing
