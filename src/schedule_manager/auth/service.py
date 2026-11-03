import secrets
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.constants import SESSION_TTL
from schedule_manager.auth.errors import (
    AuthenticationInvalidCredentialsError,
    AuthenticationSessionInvalidError,
)
from schedule_manager.auth.model import Authentication
from schedule_manager.auth.model import Session as AuthSession
from schedule_manager.auth.password_hasher import hash_password, verify_password
from schedule_manager.auth.repository import (
    AuthenticationRepository,
    AuthSessionRepository,
)
from schedule_manager.auth.schema_translator import AuthenticationSchemaTranslator
from schedule_manager.auth.schemas import AuthenticationCreate
from schedule_manager.auth.token_hasher import hash_token


class AuthenticationService:
    @staticmethod
    async def create(
        session: AsyncSession,
        authentication: AuthenticationCreate,
    ) -> Authentication | None:
        """Hash the password before persistence; never store the raw password."""
        password_hash = hash_password(authentication.password)
        authentication_model = AuthenticationSchemaTranslator.to_model(
            authentication,
            password_hash,
        )
        return await AuthenticationRepository.create(
            session,
            authentication_model,
        )

    @staticmethod
    async def validate_credentials(
        session: AsyncSession,
        email: str,
        password: str,
    ) -> Authentication:
        authentication = await AuthenticationRepository.get(session, email)
        if authentication is None or not verify_password(
            authentication.password_hash,
            password,
        ):
            raise AuthenticationInvalidCredentialsError(
                "Email or password is invalid."
            )
        return authentication

    @staticmethod
    async def delete(
        session: AsyncSession,
        email: str,
        password: str,
    ) -> bool:
        """Only delete an authentication after validating its credentials."""
        authentication = await AuthenticationService.validate_credentials(
            session,
            email,
            password,
        )
        return await AuthenticationRepository.delete(
            session,
            authentication.user_id,
        )

    @staticmethod
    async def change_password(
        session: AsyncSession,
        email: str,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Verify the current password before hashing and persisting its replacement."""
        authentication = await AuthenticationService.validate_credentials(
            session,
            email,
            current_password,
        )
        password_hash = hash_password(new_password)
        return await AuthenticationRepository.change_password(
            session,
            authentication.user_id,
            password_hash,
        )


class AuthSessionService:
    @staticmethod
    async def login(
        session: AsyncSession,
        email: str,
        password: str,
    ) -> str:
        """Return a raw token but persist only its hash, expiring six hours after login."""
        authentication = await AuthenticationService.validate_credentials(
            session,
            email,
            password,
        )
        token = secrets.token_urlsafe(32)
        auth_session = AuthSession(
            user_id=authentication.user_id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + SESSION_TTL,
        )
        await AuthSessionRepository.create(session, auth_session)
        return token

    @staticmethod
    async def validate_session(
        session: AsyncSession,
        token: str,
    ) -> AuthSession:
        auth_session = await AuthSessionRepository.get(
            session,
            hash_token(token),
        )
        if (
            auth_session is None
            or auth_session.expires_at <= datetime.now(UTC)
        ):
            raise AuthenticationSessionInvalidError(
                "Authentication session is invalid or expired."
            )
        return auth_session
