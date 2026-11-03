from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.business.model import Business, BusinessOwner


class BusinessRepository:
    @staticmethod
    async def get(
        session: AsyncSession,
        business_id: UUID,
    ) -> Business | None:
        return await session.scalar(
            select(Business).where(Business.id == business_id)
        )

    @staticmethod
    async def create(
        session: AsyncSession,
        business: Business,
    ) -> Business:
        session.add(business)
        await session.flush()
        return business

    @staticmethod
    async def assign_owner(
        session: AsyncSession,
        business_id: UUID,
        owner_id: UUID,
    ) -> bool:
        statement = (
            insert(BusinessOwner)
            .values(business_id=business_id, owner_id=owner_id)
            .on_conflict_do_nothing(
                index_elements=[
                    BusinessOwner.business_id,
                    BusinessOwner.owner_id,
                ]
            )
            .returning(BusinessOwner.business_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_owner(
        session: AsyncSession,
        business_id: UUID,
        owner_id: UUID,
    ) -> bool:
        owner_business_id = await session.scalar(
            select(BusinessOwner.business_id).where(
                BusinessOwner.business_id == business_id,
                BusinessOwner.owner_id == owner_id,
            )
        )
        return owner_business_id is not None

    @staticmethod
    async def remove_owner(
        session: AsyncSession,
        business_id: UUID,
        owner_id: UUID,
    ) -> bool:
        statement = (
            delete(BusinessOwner)
            .where(
                BusinessOwner.business_id == business_id,
                BusinessOwner.owner_id == owner_id,
            )
            .returning(BusinessOwner.business_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def delete_business(
        session: AsyncSession,
        business_id: UUID,
    ) -> bool:
        statement = (
            delete(Business)
            .where(Business.id == business_id)
            .returning(Business.id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None
