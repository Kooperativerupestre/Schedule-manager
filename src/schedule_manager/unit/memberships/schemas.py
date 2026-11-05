from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UnitMembershipAddRequest(BaseModel):
    member_id: UUID


class UnitMembershipCreateResponse(BaseModel):
    created: bool


class UnitMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    unit_id: UUID
    begin_at: datetime
