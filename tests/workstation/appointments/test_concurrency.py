import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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
from schedule_manager.business.model import Business
from schedule_manager.business.schemas import BusinessAdd
from schedule_manager.business.service import BusinessService
from schedule_manager.settings import settings
from schedule_manager.unit.schemas import UnitAdd
from schedule_manager.unit.service import UnitService
from schedule_manager.user.model import User
from schedule_manager.workstation.appointments.model import Appointment
from schedule_manager.workstation.appointments.schemas import (
    AppointmentActionResult,
    AppointmentAdd,
)
from schedule_manager.workstation.appointments.service import AppointmentService
from schedule_manager.workstation.schemas import WorkstationAdd
from schedule_manager.workstation.service import WorkstationService
from schedule_manager.workstation.workers.service import WorkerService

CONCURRENT_REQUESTS = 24


@dataclass
class AppointmentConcurrencyContext:
    engine: AsyncEngine
    sessions: async_sessionmaker[AsyncSession]
    business_id: UUID
    workstation_id: UUID
    maker_id: UUID
    worker_id: UUID


@pytest.fixture
async def appointment_concurrency_context() -> AsyncIterator[
    AppointmentConcurrencyContext
]:
    engine = create_async_engine(
        settings.database_url.set(database=settings.postgres_test_db),
        pool_size=CONCURRENT_REQUESTS,
        max_overflow=0,
    )
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    context: AppointmentConcurrencyContext | None = None

    try:
        async with engine.begin() as connection:
            await connection.exec_driver_sql(
                "CREATE EXTENSION IF NOT EXISTS btree_gist"
            )
            await connection.run_sync(Base.metadata.create_all)

        async with sessions.begin() as session:
            maker = User(name="Appointment concurrency owner")
            session.add(maker)
            await session.flush()
            business_id = await BusinessService.create(
                session,
                BusinessAdd(name="Appointment concurrency business"),
                maker.id,
            )
            unit_id = await UnitService.create(
                session,
                UnitAdd(name="Appointment concurrency unit", business_id=business_id),
                maker.id,
            )
            assert await UnitService.assign_owner(
                session,
                unit_id,
                maker.id,
                maker.id,
            )
            workstation_id = await WorkstationService.create(
                session,
                WorkstationAdd(
                    name="Appointment concurrency workstation", unit_id=unit_id
                ),
                maker.id,
            )
            worker_id = await WorkerService.hire(
                session,
                workstation_id,
                maker.id,
                maker.id,
            )
            assert worker_id is not None
            context = AppointmentConcurrencyContext(
                engine=engine,
                sessions=sessions,
                business_id=business_id,
                workstation_id=workstation_id,
                maker_id=maker.id,
                worker_id=worker_id,
            )

        yield context
    finally:
        if context is not None:
            async with sessions.begin() as session:
                await session.execute(
                    delete(Business).where(Business.id == context.business_id)
                )
                await session.execute(delete(User).where(User.id == context.maker_id))
        await engine.dispose()


@pytest.mark.anyio
async def test_simultaneous_overlapping_requests_create_only_one_appointment(
    appointment_concurrency_context: AppointmentConcurrencyContext,
) -> None:
    context = appointment_concurrency_context
    begin_at = datetime(2030, 1, 1, 9, tzinfo=UTC)
    barrier = asyncio.Barrier(CONCURRENT_REQUESTS + 1)

    async def create_simultaneously() -> tuple[bool, int]:
        async with context.sessions() as session:
            await barrier.wait()
            backend_pid = await session.scalar(select(func.pg_backend_pid()))
            if backend_pid is None:
                raise RuntimeError("PostgreSQL did not return a backend PID.")
            created = await AppointmentService.create(
                session,
                AppointmentAdd(
                    workstation_id=context.workstation_id,
                    worker_id=context.worker_id,
                    maker_id=context.maker_id,
                    begin_at=begin_at,
                    end_at=begin_at + timedelta(hours=1),
                ),
            )
            await session.commit()
            return created, backend_pid

    tasks = [
        asyncio.create_task(create_simultaneously()) for _ in range(CONCURRENT_REQUESTS)
    ]
    await barrier.wait()
    outcomes = await asyncio.gather(*tasks)

    assert sum(created for created, _ in outcomes) == 1
    assert len({pid for _, pid in outcomes}) > 1

    async with context.sessions() as session:
        appointments = await AppointmentService.get_in_range(
            session,
            context.workstation_id,
            begin_at,
            begin_at + timedelta(hours=1),
        )
    assert len(appointments) == 1


@pytest.mark.anyio
async def test_simultaneous_cancel_and_complete_allow_only_one_pending_transition(
    appointment_concurrency_context: AppointmentConcurrencyContext,
) -> None:
    context = appointment_concurrency_context
    begin_at = datetime(2030, 1, 2, 9, tzinfo=UTC)
    async with context.sessions.begin() as session:
        assert await AppointmentService.create(
            session,
            AppointmentAdd(
                workstation_id=context.workstation_id,
                worker_id=context.worker_id,
                maker_id=context.maker_id,
                begin_at=begin_at,
                end_at=begin_at + timedelta(hours=1),
            ),
        )
        appointment = await session.scalar(select(Appointment))
        if appointment is None:
            raise RuntimeError("Appointment was not persisted.")
        appointment_id = appointment.id

    barrier = asyncio.Barrier(3)

    async def cancel() -> tuple[AppointmentActionResult, int]:
        async with context.sessions() as session:
            await barrier.wait()
            pid = await session.scalar(select(func.pg_backend_pid()))
            if pid is None:
                raise RuntimeError("PostgreSQL did not return a backend PID.")
            result = await AppointmentService.cancel(
                session,
                appointment_id,
                context.maker_id,
            )
            await session.commit()
            return result, pid

    async def complete() -> tuple[AppointmentActionResult, int]:
        async with context.sessions() as session:
            await barrier.wait()
            pid = await session.scalar(select(func.pg_backend_pid()))
            if pid is None:
                raise RuntimeError("PostgreSQL did not return a backend PID.")
            result = await AppointmentService.complete(
                session,
                appointment_id,
                context.maker_id,
            )
            await session.commit()
            return result, pid

    cancel_task = asyncio.create_task(cancel())
    complete_task = asyncio.create_task(complete())
    await barrier.wait()
    cancel_result, complete_result = await asyncio.gather(cancel_task, complete_task)

    assert cancel_result[0] in {
        AppointmentActionResult.CANCELLED,
        AppointmentActionResult.ALREADY_COMPLETED,
    }
    assert complete_result[0] in {
        AppointmentActionResult.COMPLETED,
        AppointmentActionResult.ALREADY_CANCELLED,
    }
    assert len({cancel_result[1], complete_result[1]}) == 2
    assert (cancel_result[0] == AppointmentActionResult.CANCELLED) != (
        complete_result[0] == AppointmentActionResult.COMPLETED
    )
