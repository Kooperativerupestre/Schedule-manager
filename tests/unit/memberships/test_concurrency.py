import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from schedule_manager.base_model import Base
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.settings import settings
from schedule_manager.unit.memberships.repository import (
    UnitMembershipRepository,
)
from schedule_manager.unit.schemas import UnitAdd
from schedule_manager.unit.service import UnitService
from schedule_manager.user.model import User


@dataclass
class ConcurrentUnitMembershipContext:
    engine: AsyncEngine
    sessions: async_sessionmaker[AsyncSession]
    unit_id: UUID
    creator_id: UUID
    member_id: UUID


@pytest.fixture
async def concurrent_unit_membership_context() -> AsyncIterator[
    ConcurrentUnitMembershipContext
]:
    engine = create_async_engine(
        settings.database_url.set(database=settings.postgres_test_db),
        pool_size=2,
    )
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    context: ConcurrentUnitMembershipContext | None = None

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        async with sessions.begin() as session:
            creator = User(name="Unit concurrency creator")
            member = User(name="Unit concurrency member")
            session.add_all([creator, member])
            await session.flush()
            business_id = await BusinessService.create(
                session,
                BusinessAdd(name="Unit concurrency business"),
                creator.id,
            )
            unit_id = await UnitService.create(
                session,
                UnitAdd(name="Concurrency unit", business_id=business_id),
                creator.id,
            )
            context = ConcurrentUnitMembershipContext(
                engine=engine,
                sessions=sessions,
                unit_id=unit_id,
                creator_id=creator.id,
                member_id=member.id,
            )

        yield context
    finally:
        if context is not None:
            async with sessions.begin() as session:
                await UnitService.delete(
                    session,
                    context.unit_id,
                    context.creator_id,
                )
                await session.execute(
                    delete(User).where(
                        User.id.in_([context.creator_id, context.member_id])
                    )
                )
        await engine.dispose()


async def _run_concurrently(
    context: ConcurrentUnitMembershipContext,
    action: Callable[[AsyncSession, UUID, UUID], Awaitable[bool]],
) -> list[tuple[bool, int]]:
    barrier = asyncio.Barrier(3)

    async def run_action() -> tuple[bool, int]:
        async with context.sessions() as session:
            await barrier.wait()
            backend_pid = await session.scalar(select(func.pg_backend_pid()))
            if backend_pid is None:
                raise RuntimeError("PostgreSQL did not return a backend PID.")
            outcome = await action(session, context.unit_id, context.member_id)
            await session.commit()
            return outcome, backend_pid

    tasks = [asyncio.create_task(run_action()) for _ in range(2)]
    await barrier.wait()
    return await asyncio.gather(*tasks)


@pytest.mark.anyio
async def test_concurrent_add_adds_membership_exactly_once(
    concurrent_unit_membership_context: ConcurrentUnitMembershipContext,
) -> None:
    results = await _run_concurrently(
        concurrent_unit_membership_context,
        UnitMembershipRepository.add,
    )

    assert sorted(added for added, _ in results) == [False, True]
    assert len({pid for _, pid in results}) == 2


@pytest.mark.anyio
async def test_concurrent_remove_removes_membership_exactly_once(
    concurrent_unit_membership_context: ConcurrentUnitMembershipContext,
) -> None:
    async with concurrent_unit_membership_context.sessions.begin() as session:
        await UnitMembershipRepository.add(
            session,
            concurrent_unit_membership_context.unit_id,
            concurrent_unit_membership_context.member_id,
        )

    results = await _run_concurrently(
        concurrent_unit_membership_context,
        UnitMembershipRepository.remove,
    )

    assert sorted(removed for removed, _ in results) == [False, True]
    assert len({pid for _, pid in results}) == 2
