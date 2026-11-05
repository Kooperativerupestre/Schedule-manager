from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.errors import UnitForbiddenError
from schedule_manager.unit.memberships.model import UnitMember
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.repository import UnitRepository


class UnitMembershipService:
    @staticmethod
    async def add(
        session: AsyncSession,
        unit_id: UUID,
        member_id: UUID,
        assigner_id: UUID,
    ) -> bool:
        """Only a unit owner can add another member."""
        await UnitMembershipService._require_owner(
            session,
            unit_id,
            assigner_id,
        )
        return await UnitMembershipRepository.add(
            session,
            unit_id,
            member_id,
        )

    @staticmethod
    async def remove(
        session: AsyncSession,
        unit_id: UUID,
        member_id: UUID,
        remover_id: UUID,
    ) -> bool:
        await UnitMembershipService._require_owner(
            session,
            unit_id,
            remover_id,
        )
        membership = await UnitMembershipRepository.get_for_update(
            session,
            unit_id,
            member_id,
        )
        if membership is None:
            return False
        if await UnitRepository.is_owner(session, unit_id, member_id):
            raise UnitForbiddenError(
                "A unit owner's membership cannot be removed until "
                "a business owner revokes the unit ownership."
            )
        return await UnitMembershipRepository.remove(
            session,
            unit_id,
            member_id,
        )

    @staticmethod
    async def get(
        session: AsyncSession,
        unit_id: UUID,
        member_id: UUID,
        requester_id: UUID,
    ) -> UnitMember | None:
        """Only an existing unit member can read unit memberships."""
        await UnitMembershipService._require_member(
            session,
            unit_id,
            requester_id,
        )
        return await UnitMembershipRepository.get(
            session,
            unit_id,
            member_id,
        )

    @staticmethod
    async def _require_member(
        session: AsyncSession,
        unit_id: UUID,
        actor_id: UUID,
    ) -> None:
        """Membership is required to read unit memberships."""
        actor_is_member = await UnitMembershipRepository.get(
            session,
            unit_id,
            actor_id,
        )
        if actor_is_member is None:
            raise UnitForbiddenError("Only a unit member can access unit memberships.")

    @staticmethod
    async def _require_owner(
        session: AsyncSession,
        unit_id: UUID,
        actor_id: UUID,
    ) -> None:
        if not await UnitRepository.is_owner(session, unit_id, actor_id):
            raise UnitForbiddenError("Only a unit owner can manage unit memberships.")
