from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.errors import BusinessForbiddenError
from schedule_manager.business.memberships.model import BusinessMember
from schedule_manager.business.memberships.repository import MembershipRepository


class MembershipService:
    @staticmethod
    async def add(
        session: AsyncSession,
        business_id: UUID,
        member_id: UUID,
        assigner_id: UUID,
    ) -> bool:
        """Only an existing business member can add another member."""
        await MembershipService._require_member(
            session,
            business_id,
            assigner_id,
        )
        return await MembershipRepository.add(
            session,
            business_id,
            member_id,
        )

    @staticmethod
    async def remove(
        session: AsyncSession,
        business_id: UUID,
        member_id: UUID,
        remover_id: UUID,
    ) -> bool:
        await MembershipService._require_member(
            session,
            business_id,
            remover_id,
        )
        return await MembershipRepository.remove(
            session,
            business_id,
            member_id,
        )

    @staticmethod
    async def get(
        session: AsyncSession,
        business_id: UUID,
        member_id: UUID,
        requester_id: UUID,
    ) -> BusinessMember | None:
        """Only an existing business member can read its memberships."""
        await MembershipService._require_member(
            session,
            business_id,
            requester_id,
        )
        return await MembershipRepository.get(
            session,
            business_id,
            member_id,
        )

    @staticmethod
    async def _require_member(
        session: AsyncSession,
        business_id: UUID,
        actor_id: UUID,
    ) -> None:
        """Membership is required to read or change business memberships."""
        actor_is_member = await MembershipRepository.get(
            session,
            business_id,
            actor_id,
        )
        if actor_is_member is None:
            raise BusinessForbiddenError(
                "Only a business member can access business memberships."
            )
