from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BusinessAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class BusinessOwnerAssign(BaseModel):
    owner_id: UUID


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
