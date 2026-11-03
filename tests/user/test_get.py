from collections.abc import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.user.errors import UserForbiddenError
from schedule_manager.user.model import User
from schedule_manager.user.service import UserService


@pytest.mark.anyio
async def test_user_cannot_get_another_users_profile(
    test_session: AsyncSession,
    create_user: Callable[[AsyncSession, str], Awaitable[User]],
) -> None:
    profile_owner = await create_user(test_session, "Profile owner")
    requester = await create_user(test_session, "Different requester")

    with pytest.raises(UserForbiddenError):
        await UserService.get(
            test_session,
            profile_owner.id,
            requester.id,
        )
