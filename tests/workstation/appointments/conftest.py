from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_manager.workstation.workers.service import WorkerService

from ..conftest import WorkstationContext


@pytest.fixture
async def appointment_worker_id(
    test_session: AsyncSession,
    unit_context: WorkstationContext,
    workstation_id: UUID,
) -> UUID:
    worker_id = await WorkerService.hire(
        test_session,
        workstation_id,
        unit_context.invitee.id,
        unit_context.creator.id,
    )
    assert worker_id is not None
    return worker_id
