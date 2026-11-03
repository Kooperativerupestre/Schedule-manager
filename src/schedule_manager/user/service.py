from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.user.errors import UserNotFoundError
from schedule_manager.user.repository import UserRepository
from schedule_manager.user.schema_translator import UserSchemaTranslator
from schedule_manager.user.schemas import UserAdd


class UserService:
    @staticmethod
    async def create(session: AsyncSession, user: UserAdd) -> UUID:
        user_model = UserSchemaTranslator.to_model(user)
        created_user = await UserRepository.create(session, user_model)
        return created_user.id

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: UUID) -> None:
        deleted = await UserRepository.delete_user(session, user_id)
        if not deleted:
            raise UserNotFoundError("User not found.")
