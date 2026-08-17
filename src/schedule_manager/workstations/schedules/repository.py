from schedule_manager.utils.namespace import namespace
from psycopg import AsyncConnection
from psycopg.rows import DictRow, class_row
from schedule_manager.workstations.schedules.models import (
    ScheduleAddInput,
    ScheduleGetOutput,
    ScheduleChanges,
    ScheduleRow,
)
from uuid import UUID
from schedule_manager.workstations.schedules.ranges import (
    convert_to_db_range,
    convert_to_schedule_range,
    ScheduleRange,
)
from schedule_manager.common.missing import MISSING, _Missing
from schedule_manager.core.errors import UnexpectedStateError
from schedule_manager.workstations.status import ScheduleStatus
from psycopg import errors as psycopg_errors
from schedule_manager.core.errors import OverlappingSchedulesError
from schedule_manager.utils.service_logging import log_repository_error


@namespace
class ScheduleRepository:
    @staticmethod
    async def add(schedule: ScheduleAddInput, conn: AsyncConnection[DictRow]) -> UUID:
        query = """
INSERT INTO schedules (workstation_id, person_id, schedule_range, status) VALUES (%s, %s, %s, %s) RETURNING id;
"""
        values = (
            schedule.workstation_id,
            schedule.person_id,
            convert_to_db_range(schedule.schedule_range),
            schedule.status.value,
        )
        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                r = await cur.fetchone()
        except psycopg_errors.ExclusionViolation as error:
            log_repository_error(
                ScheduleRepository,
                "add",
                error,
                {
                    "workstation_id": str(schedule.workstation_id),
                    "person_id": str(schedule.person_id),
                },
            )
            raise OverlappingSchedulesError
        if r is None:
            raise UnexpectedStateError
        return r["id"]

    @staticmethod
    async def delete(id: UUID, conn: AsyncConnection[DictRow]) -> bool:
        query = """
DELETE FROM schedules WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        return row_count > 0

    @staticmethod
    async def update(
        id: UUID, changes: ScheduleChanges, conn: AsyncConnection[DictRow]
    ) -> bool:
        updates = []
        values = []

        if changes.person_id is not MISSING:
            updates.append("person_id = %s")
            values.append(changes.person_id)
        if changes.schedule_range is not MISSING:
            assert not isinstance(changes.schedule_range, _Missing)
            updates.append("schedule_range = %s")
            values.append(convert_to_db_range(changes.schedule_range))
        if changes.status is not MISSING:
            assert not isinstance(changes.status, _Missing)
            updates.append("status = %s")
            values.append(changes.status.value)

        if len(values) == 0:
            return False

        query = f"""
UPDATE schedules SET {", ".join(updates)} WHERE id = %s;
"""
        values.append(id)

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                row_count = cur.rowcount
        except psycopg_errors.ExclusionViolation as error:
            log_repository_error(
                ScheduleRepository, "update", error, {"schedule_id": str(id)}
            )
            raise OverlappingSchedulesError
        return row_count > 0

    @staticmethod
    async def get(id: UUID, conn: AsyncConnection[DictRow]) -> ScheduleGetOutput | None:
        query = """
SELECT * FROM schedules WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor(row_factory=class_row(ScheduleRow)) as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()
        if r is None:
            return None
        return ScheduleGetOutput(
            workstation_id=r.workstation_id,
            person_id=r.person_id,
            schedule_range=convert_to_schedule_range(r.schedule_range),
            status=ScheduleStatus(r.status.upper()),
        )

    @staticmethod
    async def has_overlapping_interval(
        workstation_id: UUID,
        schedule_range: ScheduleRange,
        conn: AsyncConnection[DictRow],
    ) -> bool:
        query = """
    SELECT EXISTS (
        SELECT 1
        FROM schedules
        WHERE workstation_id = %s
        AND schedule_range && %s::TSTZRANGE
        AND (status IN ('scheduled', 'completed'))
    );
    """

        values = (
            workstation_id,
            convert_to_db_range(schedule_range),
        )

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()

        if r is None:
            raise UnexpectedStateError

        return r["exists"]
