from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.capabilities.capabilities import Capability, Resource, Action
from schedule_manager.capabilities.schemas import CapabilityAddRequest
from schedule_manager.capabilities.errors import InvalidCapabilitiesCombinationError
import pytest
from uuid import UUID, uuid4
from schedule_manager.core.ranges.constants import NEVER_END

async def test_schema_invalid_capabilities_combination() -> None:
    with pytest.raises(InvalidCapabilitiesCombinationError):
        r = CapabilityAddRequest(resource=Resource.BUSINESS, action=Action.INVITE, target_id=uuid4(), end_at=NEVER_END)

async def test_model_capability_invalid_capabilities_combination() -> None:
    with pytest.raises(InvalidCapabilitiesCombinationError):
        r = CapabilityAddRequest(resource=Resource.BUSINESS, action=Action.INVITE, target_id=uuid4(), end_at = NEVER_END)