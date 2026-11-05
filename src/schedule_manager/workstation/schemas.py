from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkstationAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    unit_id: UUID


class WorkstationUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class WorkstationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    unit_id: UUID
