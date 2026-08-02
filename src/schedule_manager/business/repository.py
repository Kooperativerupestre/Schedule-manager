from schedule_manager.utils.namespace import namespace
from uuid import UUID
from psycopg import AsyncConnection
from psycopg import errors as psycopg_errors
from schedule_manager.business import errors as schedule_errors_business
from schedule_manager.common.update_result import UpdateOutputs
from schedule_manager.common.missing import MISSING
from psycopg.rows import class_row, DictRow
from schedule_manager.business.models import Business, BusinessChanges, BusinessRow, BusinessOutput
from schedule_manager.core.errors import UnexpectedStateError


@namespace
class BusinessRepository:
    @staticmethod
    async def add(business:Business, conn:AsyncConnection[DictRow]) -> UUID:
        query = """
INSERT INTO businesses (name, description, phone_number) 
VALUES (%s, %s, %s) RETURNING id;
"""     
        values = (business.name, business.description, business.phone_number)
        
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row = await cur.fetchone()
        if not row:
            raise UnexpectedStateError
        return row["id"]

    @staticmethod
    async def delete(business_id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        query = """
DELETE FROM businesses WHERE id = %s;
"""
        values = (business_id,)

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        return row_count > 0 
    @staticmethod
    async def update(business_id:UUID, changes:BusinessChanges, conn:AsyncConnection[DictRow]) -> UpdateOutputs:
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
        if len(values) == 0:
            return UpdateOutputs.ZERO_CHANGES

        query = f"""
        UPDATE businesses
        SET {", ".join(updates)}
        WHERE id = %s;
        """
        values.append(business_id)  

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        if row_count == 0:
            return UpdateOutputs.NOT_EXECUTED
        return UpdateOutputs.OK
    @staticmethod
    async def get(business_id:UUID, conn:AsyncConnection[DictRow]) -> BusinessOutput | None:
        query = """
SELECT name, description, phone_number, created_at FROM businesses WHERE id = %s;
"""
        async with conn.cursor(row_factory=class_row(BusinessRow)) as cur:
            await cur.execute(query, (business_id,))
            r = await cur.fetchone()
        if r is None:
            return None
        return BusinessOutput(
            r.name,
            r.description,
            r.phone_number,
            r.created_at
        )
