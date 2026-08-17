from schedule_manager.utils.namespace import namespace
from schedule_manager.workstations.status import ScheduleTimeStatus
from psycopg import AsyncConnection
from psycopg.rows import DictRow, class_row
from schedule_manager.common.missing import MISSING, _Missing
from schedule_manager.workstations.schedules.ranges import (
    convert_to_db_range,
    convert_to_schedule_range,
)
from schedule_manager.workstations.exceptions.models import (
    WorkstationExceptionAddInput,
    WorkstationExceptionChanges,
    WorkstationExceptionGetOutput,
    WorkstationExceptionRow,
)
from uuid import UUID
from schedule_manager.core.errors import UnexpectedStateError
from schedule_manager.core.errors import OverlappingSchedulesError
from psycopg import errors as psycopg_errors
from schedule_manager.utils.service_logging import log_repository_error
from schedule_manager.workstations.schedules.ranges import ScheduleRange


@namespace
class WorkstationExceptionsRepository:
    @staticmethod
    async def add(
        workstation: WorkstationExceptionAddInput, conn: AsyncConnection[DictRow]
    ) -> UUID:
        query = """
INSERT INTO workstation_exceptions (workstation_id, status, exception_range, description)
VALUES (%s, %s, %s, %s) RETURNING id;
"""
        values = (
            workstation.workstation_id,
            workstation.status.value,
            convert_to_db_range(workstation.range),
            workstation.description,
        )

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                r = await cur.fetchone()
        except psycopg_errors.ExclusionViolation as error:
            log_repository_error(
                WorkstationExceptionsRepository,
                "add",
                error,
                {"workstation_id": str(workstation.workstation_id)},
            )
            raise OverlappingSchedulesError
        if r is None:
            raise UnexpectedStateError
        return r["id"]

    @staticmethod
    async def delete(id: UUID, conn: AsyncConnection[DictRow]) -> bool:
        query = """
DELETE FROM workstation_exceptions WHERE id = %s;
"""
        values = (id,)

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        return row_count > 0

    @staticmethod
    async def get(
        id: UUID, conn: AsyncConnection[DictRow]
    ) -> WorkstationExceptionGetOutput | None:
        query = """
SELECT * FROM workstation_exceptions WHERE id = %s;
"""
        values = (id,)

        async with conn.cursor(row_factory=class_row(WorkstationExceptionRow)) as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()

        if r is None:
            return None
        return WorkstationExceptionGetOutput(
            workstation_id=r.workstation_id,
            status=ScheduleTimeStatus(r.status.upper()),
            description=r.description,
            range=convert_to_schedule_range(r.exception_range),
        )

    @staticmethod
    async def update(
        id: UUID, changes: WorkstationExceptionChanges, conn: AsyncConnection[DictRow]
    ) -> bool:
        updates = []
        values = []

        if changes.status is not MISSING:
            assert not isinstance(changes.status, _Missing)
            updates.append("status = %s")
            values.append(changes.status.value)
        if changes.description is not MISSING:
            updates.append("description = %s")
            values.append(changes.description)
        if changes.range is not MISSING:
            assert not isinstance(changes.range, _Missing)
            updates.append("exception_range = %s")
            values.append(convert_to_db_range(changes.range))

        if len(values) == 0:
            return False

        query = f"""
UPDATE workstation_exceptions SET {", ".join(updates)} WHERE id = %s;
"""
        values.append(id)

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                row_count = cur.rowcount
        except psycopg_errors.ExclusionViolation as error:
            log_repository_error(
                WorkstationExceptionsRepository,
                "update",
                error,
                {"exception_id": str(id)},
            )
            raise OverlappingSchedulesError
        return row_count > 0

    @staticmethod
    async def has_overlapping_interval(
        workstation_id: UUID,
        validity_range: ScheduleRange,
        conn: AsyncConnection[DictRow],
    ) -> bool:
        query = """
    SELECT EXISTS (
        SELECT 1
        FROM workstation_exceptions
        WHERE workstation_id = %s
        AND exception_range && %s::TSTZRANGE
        AND (status IN ('available', 'unavailable'))
    );
    """

        values = (
            workstation_id,
            convert_to_db_range(validity_range),
        )

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()

        if r is None:
            raise UnexpectedStateError

        return r["exists"]
