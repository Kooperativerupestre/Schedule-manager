from dataclasses import dataclass
from schedule_manager.capabilities.capabilities import Capability, capability_from_name
from uuid import UUID
from datetime import datetime
from schedule_manager.core.ranges.models import NormalRange
from psycopg.types.range import Range
from schedule_manager.core.ranges.constants import _NeverEnd
from schedule_manager.core.ranges.convertions import RangeConverts


@dataclass(frozen=True)
class CapabilityInput(Capability):
    end_at: datetime | _NeverEnd


@dataclass(frozen=True)
class CapabilityAssignment(Capability):
    validity_range: NormalRange


@dataclass
class CapabilityRow:
    capability: str
    business_id: UUID | None
    unit_id: UUID | None
    workstation_id: UUID | None
    validity_range: Range


def capability_row_to_assignment(capability_row: CapabilityRow) -> CapabilityAssignment:
    capability = capability_from_name(capability_row.capability)

    return CapabilityAssignment(
        resource=capability.resource,
        action=capability.action,
        validity_range=RangeConverts.db_range_to_normal_range(
            capability_row.validity_range
        ),
    )
