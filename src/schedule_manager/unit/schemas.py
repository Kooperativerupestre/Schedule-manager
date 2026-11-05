from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UnitAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    business_id: UUID


class UnitOwnerAssign(BaseModel):
    owner_id: UUID


class UnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    business_id: UUID
