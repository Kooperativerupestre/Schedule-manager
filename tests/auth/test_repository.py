from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.auth.model import Authentication
from schedule_manager.auth.repository import AuthenticationRepository
from schedule_manager.user.model import User


@pytest.mark.anyio
async def test_change_password_updates_updated_at(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    user = await create_user(test_session, "Authentication user")
    authentication = await AuthenticationRepository.create(
        test_session,
        Authentication(
            user_id=user.id,
            email="auth@example.com",
            password_hash="old-hash",
        ),
    )
    assert authentication is not None

    previous_updated_at = datetime(2000, 1, 1, tzinfo=UTC)
    authentication.updated_at = previous_updated_at
    await test_session.flush()

    changed = await AuthenticationRepository.change_password(
        test_session,
        user.id,
        "new-hash",
    )
    await test_session.refresh(authentication)

    assert changed
    assert authentication.updated_at > previous_updated_at
