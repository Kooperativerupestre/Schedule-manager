from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MembershipAddRequest(BaseModel):
    member_id: UUID


class MembershipCreateResponse(BaseModel):
    created: bool


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    business_id: UUID
    begin_at: datetime
