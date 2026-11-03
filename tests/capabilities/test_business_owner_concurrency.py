import asyncio
from uuid import UUID

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from schedule_manager.business.model import Business
from schedule_manager.business.repository import BusinessRepository
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.settings import settings
from schedule_manager.user.model import User


@pytest.mark.anyio
async def test_concurrent_assignments_only_add_owner_once() -> None:
    engine = create_async_engine(
        settings.database_url.set(database=settings.postgres_test_db),
        pool_size=2,
    )
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    business_id: UUID | None = None
    creator_id: UUID | None = None
    target_id: UUID | None = None

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Business.metadata.create_all)
            await connection.run_sync(User.metadata.create_all)

        async with sessions.begin() as setup_session:
            creator = User(name="Concurrency creator")
            target = User(name="Concurrency target")
            setup_session.add_all([creator, target])
            await setup_session.flush()
            business_id = await BusinessService.create(
                setup_session,
                BusinessAdd(name="Concurrency business"),
                creator.id,
            )
            target_id = target.id
            creator_id = creator.id

        barrier = asyncio.Barrier(3)

        async def assign_owner() -> tuple[bool, int]:
            async with sessions() as session:
                await barrier.wait()
                backend_pid = await session.scalar(
                    select(func.pg_backend_pid())
                )
                if backend_pid is None:
                    raise RuntimeError("PostgreSQL did not return a backend PID.")
                assigned = await BusinessRepository.assign_owner(
                    session,
                    business_id,
                    target_id,
                )
                await session.commit()
                return assigned, backend_pid

        tasks = [asyncio.create_task(assign_owner()) for _ in range(2)]
        await barrier.wait()
        results = await asyncio.gather(*tasks)

        assert sorted(assigned for assigned, _ in results) == [False, True]
        assert len({backend_pid for _, backend_pid in results}) == 2
    finally:
        if creator_id is not None and target_id is not None:
            async with sessions.begin() as cleanup_session:
                if business_id is not None:
                    await BusinessRepository.delete_business(
                        cleanup_session,
                        business_id,
                    )
                await cleanup_session.execute(
                    delete(User).where(User.id.in_([creator_id, target_id]))
                )
        await engine.dispose()
