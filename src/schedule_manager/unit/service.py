from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.repository import BusinessRepository
from schedule_manager.unit.errors import UnitForbiddenError, UnitNotFoundError
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.repository import UnitRepository
from schedule_manager.unit.schema_translator import UnitSchemaTranslator
from schedule_manager.unit.schemas import UnitAdd, UnitResponse


class UnitService:
    @staticmethod
    async def get(
        session: AsyncSession,
        unit_id: UUID,
        requester_id: UUID,
    ) -> UnitResponse:
        """Only a unit member may read its details."""
        requester_membership = await UnitMembershipRepository.get(
            session,
            unit_id,
            requester_id,
        )
        if requester_membership is None:
            raise UnitForbiddenError("Only a unit member can view unit details.")

        unit = await UnitRepository.get(session, unit_id)
        if unit is None:
            raise UnitNotFoundError("Unit not found.")
        return UnitResponse.model_validate(unit)

    @staticmethod
    async def create(
        session: AsyncSession,
        unit: UnitAdd,
        creator_id: UUID,
    ) -> UUID:
        """Only a business owner may create a unit; the creator joins it."""
        is_business_owner = await BusinessRepository.is_owner(
            session,
            unit.business_id,
            creator_id,
        )
        if not is_business_owner:
            raise UnitForbiddenError("Only a business owner can create a unit.")

        unit_model = UnitSchemaTranslator.to_model(unit)
        created_unit = await UnitRepository.create(session, unit_model)
        creator_added_as_member = await UnitMembershipRepository.add(
            session,
            created_unit.id,
            creator_id,
        )
        if not creator_added_as_member:
            raise RuntimeError("Could not add unit creator as a member.")
        return created_unit.id

    @staticmethod
    async def delete(
        session: AsyncSession,
        unit_id: UUID,
        assigner_id: UUID,
    ) -> bool:
        unit = await UnitRepository.get(session, unit_id)
        if unit is None:
            raise UnitNotFoundError("Unit not found.")

        is_business_owner = await BusinessRepository.is_owner(
            session,
            unit.business_id,
            assigner_id,
        )
        if not is_business_owner:
            raise UnitForbiddenError("Only a business owner can delete a unit.")

        deleted = await UnitRepository.delete_unit(session, unit_id)
        if not deleted:
            raise UnitNotFoundError("Unit no longer exists.")
        return True

    @staticmethod
    async def assign_owner(
        session: AsyncSession,
        unit_id: UUID,
        owner_id: UUID,
        assigner_id: UUID,
    ) -> bool:
        unit = await UnitRepository.get(session, unit_id)
        if unit is None:
            raise UnitNotFoundError("Unit not found.")

        assigner_is_business_owner = await BusinessRepository.is_owner(
            session,
            unit.business_id,
            assigner_id,
        )
        if not assigner_is_business_owner:
            raise UnitForbiddenError("Only a business owner can manage unit ownership.")

        recipient_membership = await UnitMembershipRepository.get_for_update(
            session,
            unit_id,
            owner_id,
        )
        if recipient_membership is None:
            raise UnitForbiddenError("A unit owner must be a unit member.")

        return await UnitRepository.assign_owner(
            session,
            unit_id,
            owner_id,
        )

    @staticmethod
    async def remove_owner(
        session: AsyncSession,
        unit_id: UUID,
        owner_id: UUID,
        remover_id: UUID,
    ) -> bool:
        unit = await UnitRepository.get(session, unit_id)
        if unit is None:
            raise UnitNotFoundError("Unit not found.")

        remover_is_business_owner = await BusinessRepository.is_owner(
            session,
            unit.business_id,
            remover_id,
        )
        if not remover_is_business_owner:
            raise UnitForbiddenError("Only a business owner can manage unit ownership.")
        return await UnitRepository.remove_owner(
            session,
            unit_id,
            owner_id,
        )
