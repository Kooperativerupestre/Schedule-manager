from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.user.model import User


class UserRepository:
    @staticmethod
    async def create(session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.flush()
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: UUID) -> bool:
        statement = delete(User).where(User.id == user_id).returning(User.id)

        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None
