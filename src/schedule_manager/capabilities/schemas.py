from pydantic import BaseModel, model_validator
from schedule_manager.capabilities.capabilities import Resource, Action
from uuid import UUID
from datetime import datetime
from schedule_manager.capabilities.errors import InvalidCapabilitiesCombinationError
from schedule_manager.core.ranges.constants import _NeverEnd, NEVER_END

class CapabilityAddRequest(BaseModel):
    resource: Resource
    action: Action
    target_id: UUID
    end_at: datetime | _NeverEnd = NEVER_END

    @model_validator(mode="after")
    def validate_action_for_resource(self):
        if self.action == Action.INVITE and self.resource != Resource.MEMBERS:
            raise InvalidCapabilitiesCombinationError(
                "INVITE action is only allowed for MEMBERS resource"
            )

        return self
class CapabilityGetRequest(BaseModel):
    resource:Resource
    action:Action
    target_id:UUID

class CapabilityEndRequest(BaseModel):
    resource:Resource
    action:Action
    target_id:UUID