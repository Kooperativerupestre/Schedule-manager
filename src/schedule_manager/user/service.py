from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.user.errors import UserForbiddenError, UserNotFoundError
from schedule_manager.user.repository import UserRepository
from schedule_manager.user.schema_translator import UserSchemaTranslator
from schedule_manager.user.schemas import UserAdd, UserResponse


class UserService:
    @staticmethod
    async def get(
        session: AsyncSession,
        user_id: UUID,
        requester_id: UUID,
    ) -> UserResponse:
        """A user may view only their own profile."""
        if requester_id != user_id:
            raise UserForbiddenError("Users can only view their own profile.")

        user = await UserRepository.get(session, user_id)
        if user is None:
            raise UserNotFoundError("User not found.")
        return UserResponse.model_validate(user)

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
