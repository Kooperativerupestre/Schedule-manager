from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.memberships.model import BusinessMember


class MembershipRepository:
    @staticmethod
    async def add(
        session: AsyncSession,
        business_id: UUID,
        user_id: UUID,
    ) -> bool:
        statement = (
            insert(BusinessMember)
            .values(business_id=business_id, user_id=user_id)
            .on_conflict_do_nothing(
                index_elements=[
                    BusinessMember.user_id,
                    BusinessMember.business_id,
                ]
            )
            .returning(BusinessMember.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def remove(
        session: AsyncSession,
        business_id: UUID,
        user_id: UUID,
    ) -> bool:
        statement = (
            delete(BusinessMember)
            .where(
                BusinessMember.business_id == business_id,
                BusinessMember.user_id == user_id,
            )
            .returning(BusinessMember.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get(
        session: AsyncSession,
        business_id: UUID,
        user_id: UUID,
    ) -> BusinessMember | None:
        return await session.scalar(
            select(BusinessMember).where(
                BusinessMember.business_id == business_id,
                BusinessMember.user_id == user_id,
            )
        )
