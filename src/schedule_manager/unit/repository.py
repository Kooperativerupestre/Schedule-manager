from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.model import Unit, UnitOwner


class UnitRepository:
    @staticmethod
    async def get(session: AsyncSession, unit_id: UUID) -> Unit | None:
        return await session.scalar(select(Unit).where(Unit.id == unit_id))

    @staticmethod
    async def create(session: AsyncSession, unit: Unit) -> Unit:
        session.add(unit)
        await session.flush()
        return unit

    @staticmethod
    async def delete_unit(session: AsyncSession, unit_id: UUID) -> bool:
        statement = delete(Unit).where(Unit.id == unit_id).returning(Unit.id)
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def assign_owner(
        session: AsyncSession,
        unit_id: UUID,
        owner_id: UUID,
    ) -> bool:
        statement = (
            insert(UnitOwner)
            .values(unit_id=unit_id, user_id=owner_id)
            .on_conflict_do_nothing(
                index_elements=[UnitOwner.user_id, UnitOwner.unit_id]
            )
            .returning(UnitOwner.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_owner(
        session: AsyncSession,
        unit_id: UUID,
        owner_id: UUID,
    ) -> bool:
        owner_user_id = await session.scalar(
            select(UnitOwner.user_id).where(
                UnitOwner.unit_id == unit_id,
                UnitOwner.user_id == owner_id,
            )
        )
        return owner_user_id is not None

    @staticmethod
    async def remove_owner(
        session: AsyncSession,
        unit_id: UUID,
        owner_id: UUID,
    ) -> bool:
        statement = (
            delete(UnitOwner)
            .where(
                UnitOwner.unit_id == unit_id,
                UnitOwner.user_id == owner_id,
            )
            .returning(UnitOwner.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None
