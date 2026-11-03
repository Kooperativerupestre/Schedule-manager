from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.model import Authentication
from schedule_manager.auth.model import Session as AuthSession


class AuthenticationRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        authentication: Authentication,
    ) -> Authentication | None:
        statement = (
            insert(Authentication)
            .values(
                user_id=authentication.user_id,
                email=authentication.email,
                password_hash=authentication.password_hash,
            )
            .on_conflict_do_nothing()
            .returning(Authentication)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(session: AsyncSession, user_id: UUID) -> bool:
        statement = (
            delete(Authentication)
            .where(Authentication.user_id == user_id)
            .returning(Authentication.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get(
        session: AsyncSession,
        email: str,
    ) -> Authentication | None:
        return await session.scalar(
            select(Authentication).where(Authentication.email == email)
        )

    @staticmethod
    async def change_password(
        session: AsyncSession,
        user_id: UUID,
        password_hash: str,
    ) -> bool:
        statement = (
            update(Authentication)
            .where(Authentication.user_id == user_id)
            .values(
                password_hash=password_hash,
                updated_at=func.now(),
            )
            .returning(Authentication.user_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None


class AuthSessionRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        auth_session: AuthSession,
    ) -> AuthSession:
        session.add(auth_session)
        await session.flush()
        return auth_session

    @staticmethod
    async def delete(session: AsyncSession, token_hash: str) -> bool:
        statement = (
            delete(AuthSession)
            .where(AuthSession.token_hash == token_hash)
            .returning(AuthSession.id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get(
        session: AsyncSession,
        token_hash: str,
    ) -> AuthSession | None:
        return await session.scalar(
            select(AuthSession).where(AuthSession.token_hash == token_hash)
        )