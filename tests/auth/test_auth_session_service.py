from datetime import UTC, datetime, timedelta
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.constants import SESSION_TTL
from schedule_manager.auth.errors import (
    AuthenticationInvalidCredentialsError,
    AuthenticationSessionInvalidError,
)
from schedule_manager.auth.model import Authentication
from schedule_manager.auth.model import Session as AuthSession
from schedule_manager.auth.repository import AuthSessionRepository
from schedule_manager.auth.service import (
    AuthenticationService,
    AuthSessionService,
)
from schedule_manager.auth.token_hasher import hash_token, verify_token


@pytest.mark.anyio
async def test_login_persists_hashed_token_with_configured_expiry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = cast(AsyncSession, AsyncMock(spec=AsyncSession))
    authentication = Authentication(
        user_id=uuid4(),
        email="auth@example.com",
        password_hash="password-hash",
    )
    validate_credentials = AsyncMock(return_value=authentication)
    create_session = AsyncMock()
    monkeypatch.setattr(
        AuthenticationService,
        "validate_credentials",
        validate_credentials,
    )
    monkeypatch.setattr(AuthSessionRepository, "create", create_session)
    started_at = datetime.now(UTC)

    token = await AuthSessionService.login(
        session,
        authentication.email,
        "password",
    )

    finished_at = datetime.now(UTC)
    validate_credentials.assert_awaited_once_with(
        session,
        authentication.email,
        "password",
    )
    create_session.assert_awaited_once()
    create_call = create_session.await_args
    assert create_call is not None
    saved_session = create_call.args[1]
    assert saved_session.user_id == authentication.user_id
    assert saved_session.token_hash == hash_token(token)
    assert saved_session.token_hash != token
    assert started_at + SESSION_TTL <= saved_session.expires_at
    assert saved_session.expires_at <= finished_at + SESSION_TTL


@pytest.mark.anyio
async def test_login_does_not_create_session_when_credentials_are_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = cast(AsyncSession, AsyncMock(spec=AsyncSession))
    invalid_credentials = AuthenticationInvalidCredentialsError(
        "Email or password is invalid."
    )
    validate_credentials = AsyncMock(side_effect=invalid_credentials)
    create_session = AsyncMock()
    monkeypatch.setattr(
        AuthenticationService,
        "validate_credentials",
        validate_credentials,
    )
    monkeypatch.setattr(AuthSessionRepository, "create", create_session)

    with pytest.raises(AuthenticationInvalidCredentialsError):
        await AuthSessionService.login(
            session,
            "auth@example.com",
            "wrong password",
        )

    validate_credentials.assert_awaited_once_with(
        session,
        "auth@example.com",
        "wrong password",
    )
    create_session.assert_not_awaited()


@pytest.mark.anyio
async def test_validate_session_looks_up_hash_and_rejects_expired_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = cast(AsyncSession, AsyncMock(spec=AsyncSession))
    token = "random-browser-token"
    auth_session = AuthSession(
        user_id=uuid4(),
        token_hash=hash_token(token),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    get_session = AsyncMock(return_value=auth_session)
    monkeypatch.setattr(AuthSessionRepository, "get", get_session)

    validated = await AuthSessionService.validate_session(session, token)

    assert validated is auth_session
    get_session.assert_awaited_once_with(session, hash_token(token))
    assert verify_token(auth_session.token_hash, token)

    expired = AuthSession(
        user_id=uuid4(),
        token_hash=hash_token(token),
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    get_session.return_value = expired

    with pytest.raises(AuthenticationSessionInvalidError):
        await AuthSessionService.validate_session(session, token)
