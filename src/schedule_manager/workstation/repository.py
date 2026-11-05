from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.workstation.model import Workstation


class WorkstationRepository:
    @staticmethod
    async def get(
        session: AsyncSession,
        workstation_id: UUID,
    ) -> Workstation | None:
        return await session.scalar(
            select(Workstation).where(Workstation.id == workstation_id)
        )

    @staticmethod
    async def create(
        session: AsyncSession,
        workstation: Workstation,
    ) -> Workstation:
        session.add(workstation)
        await session.flush()
        return workstation

    @staticmethod
    async def update_name(
        session: AsyncSession,
        workstation: Workstation,
        name: str,
    ) -> Workstation:
        workstation.name = name
        await session.flush()
        return workstation

    @staticmethod
    async def delete(
        session: AsyncSession,
        workstation_id: UUID,
    ) -> bool:
        statement = (
            delete(Workstation)
            .where(Workstation.id == workstation_id)
            .returning(Workstation.id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None
