from schedule_manager.utils.namespace import namespace
from dataclasses import dataclass
from datetime import datetime
from schedule_manager.core.ranges import NormalRange, db_range_to_normal_range
from uuid import UUID
from psycopg.types.range import Range

# Membership
@dataclass(frozen=True)
class BusinessMembershipRow:
    id:UUID
    business_id:UUID
    validity_range:Range
    person_id:UUID
    


@dataclass(frozen=True)
class BusinessMembership:
    validity_range:NormalRange
    business_id:UUID
    person_id:UUID


def row_to_model(row:BusinessMembershipRow) -> BusinessMembership:
    return BusinessMembership(
        validity_range=db_range_to_normal_range(row.validity_range),
        person_id=row.person_id,
        business_id=row.business_id
    )


# Invite

@dataclass(frozen=True)
class BusinessMembershipInviteRow:
    id:UUID
    created_at:datetime
    expires_at:datetime
    accepted_at:datetime | None

@dataclass(frozen=True)
class BusinessMembershipInvite:
    id:UUID
    created_at:datetime
    expires_at:datetime
    accepted_at:datetime | None

# Translator

@namespace
class ModelTranslator:
    @staticmethod
    def membership_row_to_mode(row:BusinessMembershipRow) -> BusinessMembership:
        return BusinessMembership(
        validity_range=db_range_to_normal_range(row.validity_range),
        person_id=row.person_id,
        business_id=row.business_id
    )

    @staticmethod
    def membership_invite_row_to_model(row:BusinessMembershipInviteRow) -> BusinessMembershipInvite:
        return BusinessMembershipInvite(
            id=row.id,
            created_at=row.created_at,
            expires_at=row.expires_at,
            accepted_at=row.accepted_at
        )
