from dataclasses import dataclass
from uuid import UUID
from abc import ABC
from psycopg import AsyncConnection
from psycopg.rows import class_row, DictRow
import psycopg.errors as psycopg_errors
from schedule_manager.common.missing import _Missing, MISSING
from schedule_manager.common.update_result import UpdateOutputs
from schedule_manager.core.errors import NullDataError, OverlappingSchedulesError
from psycopg import sql
from schedule_manager.core.ranges import db_range_to_strict_range
from schedule_manager.utils.namespace import namespace
from schedule_manager.holidays.models import Holiday, HolidayChanges, HolidayRow
from schedule_manager.core.errors import UnexpectedStateError


class HolidayRepositoryContext(ABC):
    table_name: sql.Identifier
    owner_column: sql.Identifier

    foreign_key_error: type[Exception]



@namespace
class HolidayRepository:
    @staticmethod
    async def add(
        config: type[HolidayRepositoryContext],
        owner_id: UUID,
        holiday: Holiday,
        conn: AsyncConnection[DictRow],
    ) -> UUID:
        query = sql.SQL("""
INSERT INTO {table}
({owner_column}, name, description, holiday_range)
VALUES (%s, %s, %s, %s)
RETURNING id;
""").format(
            table=config.table_name,
            owner_column=config.owner_column,
        )

        values = (
            owner_id,
            holiday.name,
            holiday.description,
            holiday.range.to_db_range,
        )

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                row = await cur.fetchone()

            if row is None:
                raise UnexpectedStateError

            return row["id"]

        except psycopg_errors.ForeignKeyViolation:
            raise config.foreign_key_error()

        except psycopg_errors.ExclusionViolation:
            raise OverlappingSchedulesError

        except psycopg_errors.NotNullViolation:
            raise NullDataError
    @staticmethod
    async def delete(
        config: type[HolidayRepositoryContext],
        holiday_id: UUID,
        conn: AsyncConnection[DictRow],
    ) -> bool:
        query = sql.SQL("""
        DELETE FROM {table}
        WHERE id = %s;
        """).format(
            table=config.table_name,
        )
        async with conn.cursor() as cur:
            await cur.execute(query, (holiday_id,))
            return cur.rowcount != 0
    @staticmethod
    async def update(
        config: type[HolidayRepositoryContext],
        holiday_id: UUID,
        changes: HolidayChanges,
        conn: AsyncConnection[DictRow],
    ) -> UpdateOutputs:

        updates: list[sql.Composed] = []
        values: list[object] = []

        if changes.name is not MISSING:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("name")))
            values.append(changes.name)

        if changes.description is not MISSING:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("description")))
            values.append(changes.description)
    

        if changes.range is not MISSING:
            updates.append(sql.SQL("{} = %s").format(sql.Identifier("holiday_range")))
            values.append(changes.range.to_db_range) # type: ignore

        if not updates:
            return UpdateOutputs.ZERO_CHANGES

        values.append(holiday_id)

        query = sql.SQL("""
UPDATE {table}
SET {updates}
WHERE id = %s;
""").format(
            table=config.table_name,
            updates=sql.SQL(", ").join(updates),
        )

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)

                if cur.rowcount == 0:
                    return UpdateOutputs.NOT_EXECUTED

            return UpdateOutputs.OK

        except psycopg_errors.ExclusionViolation:
            raise OverlappingSchedulesError
    @staticmethod
    async def get(
        config: type[HolidayRepositoryContext],
        holiday_id: UUID,
        conn: AsyncConnection[DictRow],
    ) -> Holiday | None:

        query = sql.SQL("""
SELECT
    {owner_column} AS owner_id,
    name,
    description,
    holiday_range
FROM {table}
WHERE id = %s;
""").format(
            owner_column=config.owner_column,
            table=config.table_name,
        )

        async with conn.cursor(row_factory=class_row(HolidayRow)) as cur:
            await cur.execute(query, (holiday_id,))
            row = await cur.fetchone()

        if row is None:
            return None

        return Holiday(
            name=row.name,
            description=row.description,
            range=db_range_to_strict_range(row.holiday_range),
        )