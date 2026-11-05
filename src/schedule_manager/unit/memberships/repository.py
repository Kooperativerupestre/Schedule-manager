from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.unit.memberships.model import UnitMember


class UnitMembershipRepository:
    @staticmethod
    async def add(
        session: AsyncSession,
        unit_id: UUID,
        user_id: UUID,
    ) -> bool:
        statement = (
            insert(UnitMember)
            .values(unit_id=unit_id, user_id=user_id)
            .on_conflict_do_nothing(
                index_elements=[UnitMember.user_id, UnitMember.unit_id]
            )
            .returning(UnitMember.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def remove(
        session: AsyncSession,
        unit_id: UUID,
        user_id: UUID,
    ) -> bool:
        membership = await session.scalar(
            select(UnitMember)
            .where(
                UnitMember.unit_id == unit_id,
                UnitMember.user_id == user_id,
            )
            .with_for_update()
        )
        if membership is None:
            return False

        statement = (
            delete(UnitMember)
            .where(
                UnitMember.unit_id == unit_id,
                UnitMember.user_id == user_id,
            )
            .returning(UnitMember.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get(
        session: AsyncSession,
        unit_id: UUID,
        user_id: UUID,
    ) -> UnitMember | None:
        return await session.scalar(
            select(UnitMember).where(
                UnitMember.unit_id == unit_id,
                UnitMember.user_id == user_id,
            )
        )

    @staticmethod
    async def get_for_update(
        session: AsyncSession,
        unit_id: UUID,
        user_id: UUID,
    ) -> UnitMember | None:
        return await session.scalar(
            select(UnitMember)
            .where(
                UnitMember.unit_id == unit_id,
                UnitMember.user_id == user_id,
            )
            .with_for_update()
        )
