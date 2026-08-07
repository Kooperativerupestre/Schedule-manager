from uuid import UUID

from psycopg import AsyncConnection, errors as psycopg_errors
from psycopg.rows import DictRow, class_row

from schedule_manager.common.missing import MISSING
from schedule_manager.core.errors import UnexpectedStateError
from schedule_manager.workstations.workstation.errors import WorkstationNotFoundError
from schedule_manager.utils.namespace import namespace
from schedule_manager.workstations.workstation.models import (
    Workstation,
    WorkstationAddOutput,
    WorkstationChanges,
    WorkstationGetOutput,
    WorkstationRow,
)


@namespace
class WorkstationRepository:
    @staticmethod
    async def add(workstation: Workstation, conn: AsyncConnection[DictRow]) -> WorkstationAddOutput:
        query = """
INSERT INTO workstations (unit_id, name, description) VALUES (%s, %s, %s) RETURNING id, created_at;
"""
        values = (workstation.unit_id, workstation.name, workstation.description)

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                r = await cur.fetchone()
            if r is None:
                raise UnexpectedStateError
        except psycopg_errors.ForeignKeyViolation:
            raise WorkstationNotFoundError
        return WorkstationAddOutput(id=r["id"], created_at=r["created_at"])

    @staticmethod
    async def delete(id: UUID, conn: AsyncConnection[DictRow]) -> bool:
        query = """
DELETE FROM workstations WHERE id = %s;
"""
        async with conn.cursor() as cur:
            await cur.execute(query, (id,))
            row_count = cur.rowcount
        return row_count > 0

    @staticmethod
    async def update(id: UUID, changes: WorkstationChanges, conn: AsyncConnection[DictRow]) -> bool:
        updates = []
        values = []

        if changes.name is not MISSING:
            updates.append("name = %s")
            values.append(changes.name)
        if changes.description is not MISSING:
            updates.append("description = %s")
            values.append(changes.description)
        if changes.unit_id is not MISSING:
            updates.append("unit_id = %s")
            values.append(changes.unit_id)

        if len(values) == 0:
            return False

        query = f"""
UPDATE workstations SET {', '.join(updates)} WHERE id = %s;
"""
        values.append(id)

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        return row_count > 0

    @staticmethod
    async def get(id: UUID, conn: AsyncConnection[DictRow]) -> WorkstationGetOutput | None:
        query = """
SELECT * FROM workstations WHERE id = %s;
"""
        async with conn.cursor(row_factory=class_row(WorkstationRow)) as cur:
            await cur.execute(query, (id,))
            r = await cur.fetchone()
        if r is None:
            return None

        return WorkstationGetOutput(
            id=r.id,
            unit_id=r.unit_id,
            name=r.name,
            description=r.description,
            created_at=r.created_at,
        )
