from schedule_manager.utils.namespace import namespace
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business.memberships.repository import MembershipRepository
from schedule_manager.business.memberships.status import MembershipStatus
from schedule_manager.business.memberships.errors import NotBusinessMembershipError
from schedule_manager.capabilities.errors import ForbiddenError
from schedule_manager.capabilities.capabilities import Action, Capability, Resource
from schedule_manager.capabilities.repository import CapabilitiesRepository


@namespace
class MembershipValidator:
    @staticmethod
    async def validate_membership(
        person_id: UUID, business_id: UUID, conn: AsyncConnection[DictRow]
    ) -> None:
        membership = await MembershipRepository.get(
            person_id, business_id, conn, MembershipStatus.ACTIVE
        )
        if not membership:
            raise NotBusinessMembershipError

    @staticmethod
    async def validate_capability_membership(
        person_id: UUID,
        business_id: UUID,
        action: Action,
        conn: AsyncConnection[DictRow],
    ) -> None:
        has = await CapabilitiesRepository.has(
            person_id, business_id, Capability(Resource.MEMBERS, action), conn
        )

        if not has:
            raise ForbiddenError
