from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.workstation.workers.model import Worker


class WorkerRepository:
    @staticmethod
    async def get(
        session: AsyncSession,
        workstation_id: UUID,
        worker_id: UUID,
    ) -> Worker | None:
        return await session.scalar(
            select(Worker).where(
                Worker.id == worker_id,
                Worker.workstation_id == workstation_id,
            )
        )

    @staticmethod
    async def hire(
        session: AsyncSession,
        workstation_id: UUID,
        user_id: UUID,
    ) -> Worker | None:
        statement = (
            insert(Worker)
            .values(workstation_id=workstation_id, user_id=user_id)
            .on_conflict_do_nothing(
                index_elements=[Worker.user_id, Worker.workstation_id]
            )
            .returning(Worker.id)
        )
        result = await session.execute(statement)
        worker_id = result.scalar_one_or_none()
        if worker_id is None:
            return None
        return await WorkerRepository.get(session, workstation_id, worker_id)

    @staticmethod
    async def dismiss(
        session: AsyncSession,
        workstation_id: UUID,
        worker_id: UUID,
    ) -> bool:
        statement = (
            delete(Worker)
            .where(
                Worker.id == worker_id,
                Worker.workstation_id == workstation_id,
            )
            .returning(Worker.id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None
