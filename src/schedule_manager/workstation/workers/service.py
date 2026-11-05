from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.repository import UnitRepository
from schedule_manager.user.errors import UserNotFoundError
from schedule_manager.user.repository import UserRepository
from schedule_manager.workstation.errors import (
    WorkstationForbiddenError,
    WorkstationNotFoundError,
)
from schedule_manager.workstation.repository import WorkstationRepository
from schedule_manager.workstation.workers.errors import (
    WorkerForbiddenError,
    WorkerNotFoundError,
)
from schedule_manager.workstation.workers.repository import WorkerRepository
from schedule_manager.workstation.workers.schemas import WorkerResponse


class WorkerService:
    @staticmethod
    async def hire(
        session: AsyncSession,
        workstation_id: UUID,
        user_id: UUID,
        hirer_id: UUID,
    ) -> UUID | None:
        workstation = await WorkstationRepository.get(session, workstation_id)
        if workstation is None:
            raise WorkstationNotFoundError("Workstation not found.")
        if not await UnitRepository.is_owner(
            session,
            workstation.unit_id,
            hirer_id,
        ):
            raise WorkstationForbiddenError(
                "Only a unit owner can hire a worker."
            )
        if await UserRepository.get(session, user_id) is None:
            raise UserNotFoundError("User not found.")

        worker = await WorkerRepository.hire(session, workstation_id, user_id)
        return worker.id if worker is not None else None

    @staticmethod
    async def get(
        session: AsyncSession,
        workstation_id: UUID,
        worker_id: UUID,
        requester_id: UUID,
    ) -> WorkerResponse:
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
            raise WorkerForbiddenError(
                "Only a member of the workstation's unit can view workers."
            )

        worker = await WorkerRepository.get(session, workstation_id, worker_id)
        if worker is None:
            raise WorkerNotFoundError("Worker not found.")
        return WorkerResponse.model_validate(worker)

    @staticmethod
    async def dismiss(
        session: AsyncSession,
        workstation_id: UUID,
        worker_id: UUID,
        requester_id: UUID,
    ) -> bool:
        worker = await WorkerRepository.get(session, workstation_id, worker_id)
        if worker is None:
            raise WorkerNotFoundError("Worker not found.")
        if worker.user_id != requester_id:
            raise WorkerForbiddenError("Only a worker can dismiss themselves.")
        dismissed = await WorkerRepository.dismiss(session, workstation_id, worker_id)
        if not dismissed:
            raise WorkerNotFoundError("Worker no longer exists.")
        return True
