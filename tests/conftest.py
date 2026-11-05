from collections.abc import AsyncIterator, Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from schedule_manager.base_model import Base
from schedule_manager.business.memberships.model import (
    BusinessMember,
)
from schedule_manager.settings import settings
from schedule_manager.user.model import User

CreateUser = Callable[[AsyncSession, str], Awaitable[User]]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def test_session(anyio_backend: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        settings.database_url.set(database=settings.postgres_test_db)
    )
    try:
        assert (
            Base.metadata.tables[BusinessMember.__tablename__]
            is BusinessMember.__table__
        )
        async with engine.begin() as connection:
            await connection.exec_driver_sql(
                "CREATE EXTENSION IF NOT EXISTS btree_gist"
            )
            await connection.run_sync(Base.metadata.create_all)

        async with engine.connect() as connection:
            transaction = await connection.begin()
            session = AsyncSession(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )
            try:
                yield session
            finally:
                await session.close()
                await transaction.rollback()
    finally:
        await engine.dispose()


@pytest.fixture
def create_user() -> CreateUser:
    async def create(session: AsyncSession, name: str) -> User:
        user = User(name=name)
        session.add(user)
        await session.flush()
        return user

    return create
