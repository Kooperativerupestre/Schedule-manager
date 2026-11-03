from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.errors import AuthenticationInvalidCredentialsError
from schedule_manager.auth.model import Authentication
from schedule_manager.auth.password_hasher import hash_password, verify_password
from schedule_manager.auth.repository import AuthenticationRepository
from schedule_manager.auth.service import AuthenticationService


def create_authentication(password: str) -> Authentication:
    return Authentication(
        user_id=uuid4(),
        email="auth@example.com",
        password_hash=hash_password(password),
    )


@pytest.mark.anyio
async def test_delete_raises_and_does_not_delete_with_invalid_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = cast(AsyncSession, AsyncMock(spec=AsyncSession))
    authentication = create_authentication("correct password")
    get_authentication = AsyncMock(return_value=authentication)
    delete_authentication = AsyncMock(return_value=True)
    monkeypatch.setattr(
        AuthenticationRepository,
        "get",
        get_authentication,
    )
    monkeypatch.setattr(
        AuthenticationRepository,
        "delete",
        delete_authentication,
    )

    with pytest.raises(AuthenticationInvalidCredentialsError):
        await AuthenticationService.delete(
            session,
            authentication.email,
            "wrong password",
        )

    delete_authentication.assert_not_awaited()


@pytest.mark.anyio
async def test_delete_removes_authentication_after_validating_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = cast(AsyncSession, AsyncMock(spec=AsyncSession))
    authentication = create_authentication("correct password")
    get_authentication = AsyncMock(return_value=authentication)
    delete_authentication = AsyncMock(return_value=True)
    monkeypatch.setattr(
        AuthenticationRepository,
        "get",
        get_authentication,
    )
    monkeypatch.setattr(
        AuthenticationRepository,
        "delete",
        delete_authentication,
    )

    deleted = await AuthenticationService.delete(
        session,
        authentication.email,
        "correct password",
    )

    assert deleted
    delete_authentication.assert_awaited_once_with(
        session,
        authentication.user_id,
    )


@pytest.mark.anyio
async def test_change_password_raises_and_does_not_update_with_invalid_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = cast(AsyncSession, AsyncMock(spec=AsyncSession))
    authentication = create_authentication("correct password")
    get_authentication = AsyncMock(return_value=authentication)
    change_authentication_password = AsyncMock(return_value=True)
    monkeypatch.setattr(
        AuthenticationRepository,
        "get",
        get_authentication,
    )
    monkeypatch.setattr(
        AuthenticationRepository,
        "change_password",
        change_authentication_password,
    )

    with pytest.raises(AuthenticationInvalidCredentialsError):
        await AuthenticationService.change_password(
            session,
            authentication.email,
            "wrong password",
            "new password",
        )

    change_authentication_password.assert_not_awaited()


@pytest.mark.anyio
async def test_change_password_hashes_new_password_after_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = cast(AsyncSession, AsyncMock(spec=AsyncSession))
    current_password = "correct password"
    new_password = "new password"
    authentication = create_authentication(current_password)
    get_authentication = AsyncMock(return_value=authentication)
    change_authentication_password = AsyncMock(return_value=True)
    monkeypatch.setattr(
        AuthenticationRepository,
        "get",
        get_authentication,
    )
    monkeypatch.setattr(
        AuthenticationRepository,
        "change_password",
        change_authentication_password,
    )

    changed = await AuthenticationService.change_password(
        session,
        authentication.email,
        current_password,
        new_password,
    )

    assert changed
    call = change_authentication_password.await_args
    assert call is not None
    user_id, new_password_hash = call.args[1:]
    assert user_id == authentication.user_id
    assert new_password_hash != new_password
    assert verify_password(new_password_hash, new_password)
