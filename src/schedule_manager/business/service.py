from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.errors import (
    BusinessForbiddenError,
    BusinessNotFoundError,
)
from schedule_manager.business.memberships.repository import (
    MembershipRepository,
)
from schedule_manager.business.repository import BusinessRepository
from schedule_manager.business.schema_translator import BusinessSchemaTranslator
from schedule_manager.business.schemas import BusinessAdd, BusinessResponse


class BusinessService:
    @staticmethod
    async def get(
        session: AsyncSession,
        business_id: UUID,
        requester_id: UUID,
    ) -> BusinessResponse:
        """Only a member of the business may read its details."""
        requester_membership = await MembershipRepository.get(
            session,
            business_id,
            requester_id,
        )
        if requester_membership is None:
            raise BusinessForbiddenError(
                "Only a business member can view business details."
            )

        business = await BusinessRepository.get(session, business_id)
        if business is None:
            raise BusinessNotFoundError("Business not found.")
        return BusinessResponse.model_validate(business)

    @staticmethod
    async def create(
        session: AsyncSession,
        business: BusinessAdd,
        creator_id: UUID,
    ) -> UUID:
        business_model = BusinessSchemaTranslator.to_model(business)
        created_business = await BusinessRepository.create(
            session,
            business_model,
        )
        creator_assigned_as_owner = await BusinessRepository.assign_owner(
            session,
            created_business.id,
            creator_id,
        )
        if not creator_assigned_as_owner:
            raise RuntimeError("Could not assign business creator as owner.")

        creator_added_as_member = await MembershipRepository.add(
            session,
            created_business.id,
            creator_id,
        )
        if not creator_added_as_member:
            raise RuntimeError("Could not add business creator as member.")
        return created_business.id

    @staticmethod
    async def assign_owner(
        session: AsyncSession,
        business_id: UUID,
        owner_id: UUID,
        assigner_id: UUID,
    ) -> bool:
        await BusinessService._require_owner(session, business_id, assigner_id)
        recipient_is_member = await MembershipRepository.get(
            session,
            business_id,
            owner_id,
        )
        if recipient_is_member is None:
            raise BusinessForbiddenError(
                "Only a business member can become a business owner."
            )
        return await BusinessRepository.assign_owner(
            session,
            business_id,
            owner_id,
        )

    @staticmethod
    async def remove_owner(
        session: AsyncSession,
        business_id: UUID,
        owner_id: UUID,
        assigner_id: UUID,
    ) -> bool:
        await BusinessService._require_owner(session, business_id, assigner_id)
        return await BusinessRepository.remove_owner(
            session,
            business_id,
            owner_id,
        )

    @staticmethod
    async def delete(
        session: AsyncSession,
        business_id: UUID,
        assigner_id: UUID,
    ) -> bool:
        await BusinessService._require_owner(session, business_id, assigner_id)
        deleted = await BusinessRepository.delete_business(session, business_id)
        if not deleted:
            raise BusinessNotFoundError("Business no longer exists.")
        return True

    @staticmethod
    async def _require_owner(
        session: AsyncSession,
        business_id: UUID,
        assigner_id: UUID,
    ) -> None:
        assigner_is_owner = await BusinessRepository.is_owner(
            session,
            business_id,
            assigner_id,
        )
        if not assigner_is_owner:
            raise BusinessForbiddenError(
                "Only a business owner can manage business ownership."
            )
