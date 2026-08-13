from schedule_manager.utils.namespace import namespace
from schedule_manager.units.models import Unit, UnitRow, UnitAddOutput, UnitGetOutput, UnitChanges
from psycopg import AsyncConnection
from psycopg.rows import DictRow, class_row
from uuid import UUID
from schedule_manager.core.errors import UnexpectedStateError
from schedule_manager.common.missing import MISSING
from psycopg import errors as psycopg_errors
from schedule_manager.utils.service_logging import log_repository_error

@namespace
class UnitRepository:
    @staticmethod
    async def add(unit:Unit, conn:AsyncConnection[DictRow]) -> UnitAddOutput:
        query = """
INSERT INTO units (name, business_id, description, phone_number) VALUES (%s, %s, %s, %s) RETURNING
id, created_at, business_id, phone_number, description, name;
"""
        values = (unit.name, unit.business_id, unit.description, unit.phone_number)

        try:
            async with conn.cursor(row_factory=class_row(UnitRow)) as cur:
                await cur.execute(query, values)
                r = await cur.fetchone()
            if r is None:
                raise UnexpectedStateError
        except psycopg_errors.ForeignKeyViolation as error:
            log_repository_error(UnitRepository, "add", error, {"business_id": str(unit.business_id)})
            raise ValueError(f"Business with id {unit.business_id} does not exist")
        return UnitAddOutput(
            id=r.id,
            created_at=r.created_at
        )
    @staticmethod
    async def delete(id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        query = """
DELETE FROM units WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        return row_count > 0
    @staticmethod
    async def update(id:UUID, changes:UnitChanges, conn:AsyncConnection[DictRow]) -> bool:
        updates = []
        values = []
        
        if changes.name is not MISSING:
            updates.append("name = %s")
            values.append(changes.name)
        if changes.description is not MISSING:
            updates.append("description = %s")
            values.append(changes.description)
        if changes.phone_number is not MISSING:
            updates.append("phone_number = %s")
            values.append(changes.phone_number)
        if changes.business_id is not MISSING:
            updates.append("business_id = %s")
            values.append(changes.business_id)

        if len(values) == 0:
            return False

        query = f"""
UPDATE units SET {', '.join(updates)} WHERE id = %s;
"""
        values.append(id)

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        return row_count > 0
    @staticmethod
    async def get(id:UUID, conn:AsyncConnection[DictRow]) -> UnitGetOutput | None:
        query = """
SELECT * FROM units WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor(row_factory=class_row(UnitRow)) as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()
        if r is None:
            return None
        
        return UnitGetOutput(
            id=r.id,
            business_id=r.business_id,
            name=r.name,
            description=r.description,
            phone_number=r.phone_number,
            created_at=r.created_at
        )
