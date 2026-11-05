from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.errors import UnitNotFoundError
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.repository import UnitRepository
from schedule_manager.workstation.appointments.service import AppointmentService
from schedule_manager.workstation.errors import (
    WorkstationForbiddenError,
    WorkstationNotFoundError,
)
from schedule_manager.workstation.repository import WorkstationRepository
from schedule_manager.workstation.schema_translator import (
    WorkstationSchemaTranslator,
)
from schedule_manager.workstation.schemas import (
    WorkstationAdd,
    WorkstationResponse,
)


class WorkstationService:
    @staticmethod
    async def can_schedule(
        session: AsyncSession,
        workstation_id: UUID,
        begin_at: datetime,
        end_at: datetime,
    ) -> bool:
        return await AppointmentService.can_schedule(
            session,
            workstation_id,
            begin_at,
            end_at,
        )

    @staticmethod
    async def create(
        session: AsyncSession,
        workstation: WorkstationAdd,
        creator_id: UUID,
    ) -> UUID:
        unit = await UnitRepository.get(session, workstation.unit_id)
        if unit is None:
            raise UnitNotFoundError("Unit not found.")
        if not await UnitRepository.is_owner(
            session,
            workstation.unit_id,
            creator_id,
        ):
            raise WorkstationForbiddenError(
                "Only a unit owner can create a workstation."
            )

        model = WorkstationSchemaTranslator.to_model(workstation)
        created = await WorkstationRepository.create(session, model)
        return created.id

    @staticmethod
    async def get(
        session: AsyncSession,
        workstation_id: UUID,
        requester_id: UUID,
    ) -> WorkstationResponse:
        workstation = await WorkstationRepository.get(session, workstation_id)
        if workstation is None:
            raise WorkstationNotFoundError("Workstation not found.")
        if (
            await UnitMembershipRepository.get(
                session,
                workstation.unit_id,
                requester_id,
            )
            is None
        ):
            raise WorkstationForbiddenError(
                "Only a unit member can view a workstation."
            )
        return WorkstationResponse.model_validate(workstation)

    @staticmethod
    async def update(
        session: AsyncSession,
        workstation_id: UUID,
        name: str,
        updater_id: UUID,
    ) -> WorkstationResponse:
        workstation = await WorkstationRepository.get(session, workstation_id)
        if workstation is None:
            raise WorkstationNotFoundError("Workstation not found.")
        await WorkstationService._require_owner(
            session,
            workstation.unit_id,
            updater_id,
        )
        updated = await WorkstationRepository.update_name(
            session,
            workstation,
            name,
        )
        return WorkstationResponse.model_validate(updated)

    @staticmethod
    async def delete(
        session: AsyncSession,
        workstation_id: UUID,
        deleter_id: UUID,
    ) -> bool:
        workstation = await WorkstationRepository.get(session, workstation_id)
        if workstation is None:
            raise WorkstationNotFoundError("Workstation not found.")
        await WorkstationService._require_owner(
            session,
            workstation.unit_id,
            deleter_id,
        )
        deleted = await WorkstationRepository.delete(session, workstation_id)
        if not deleted:
            raise WorkstationNotFoundError("Workstation no longer exists.")
        return True

    @staticmethod
    async def _require_owner(
        session: AsyncSession,
        unit_id: UUID,
        actor_id: UUID,
    ) -> None:
        if not await UnitRepository.is_owner(session, unit_id, actor_id):
            raise WorkstationForbiddenError(
                "Only a unit owner can manage workstations."
            )
