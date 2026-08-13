from dataclasses import dataclass
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import class_row, DictRow
import psycopg.errors as psycopg_errors
from schedule_manager.common.missing import MISSING
from schedule_manager.common.update_result import UpdateOutputs
from schedule_manager.core.errors import NullDataError, OverlappingSchedulesError
from psycopg import sql
from schedule_manager.utils.namespace import namespace
from schedule_manager.holidays.models import Holiday, HolidayChanges, HolidayRange, HolidayRow, db_range_to_holiday_range, holiday_range_to_db
from schedule_manager.core.errors import UnexpectedStateError
from schedule_manager.utils.service_logging import log_repository_error


@dataclass(frozen=True)
class HolidayRepositoryContext:
    table_name: sql.Identifier
    owner_column: sql.Identifier

    foreign_key_error: type[Exception]

@namespace
class HolidayRepository:
    @staticmethod
    async def add(
        config: HolidayRepositoryContext,
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
            holiday_range_to_db(holiday.range),

        )

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                row = await cur.fetchone()

            if row is None:
                raise UnexpectedStateError

            return row["id"]

        except psycopg_errors.ForeignKeyViolation as error:
            log_repository_error(HolidayRepository, "add", error, {"owner_id": str(owner_id), "table": config.table_name.as_string(conn)})
            raise config.foreign_key_error()

        except psycopg_errors.ExclusionViolation as error:
            log_repository_error(HolidayRepository, "add", error, {"owner_id": str(owner_id), "table": config.table_name.as_string(conn)})
            raise OverlappingSchedulesError

        except psycopg_errors.NotNullViolation as error:
            log_repository_error(HolidayRepository, "add", error, {"owner_id": str(owner_id), "table": config.table_name.as_string(conn)})
            raise NullDataError
    @staticmethod
    async def delete(
        config: HolidayRepositoryContext,
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
        config: HolidayRepositoryContext,
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

        except psycopg_errors.ExclusionViolation as error:
            log_repository_error(HolidayRepository, "update", error, {"holiday_id": str(holiday_id), "table": config.table_name.as_string(conn)})
            raise OverlappingSchedulesError
    @staticmethod
    async def get(
        config: HolidayRepositoryContext,
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
            range=db_range_to_holiday_range(row.holiday_range),
        )
    @staticmethod
    async def has_overlapping_interval(
        config: HolidayRepositoryContext,
        owner_id: UUID,
        interval: HolidayRange,
        conn: AsyncConnection[DictRow],
    ) -> bool:
        query = sql.SQL("""
    SELECT EXISTS (
        SELECT 1
        FROM {table}
        WHERE {owner_column} = %s
        AND holiday_range && %s::TSTZRANGE
    );
    """).format(
            table=config.table_name,
            owner_column=config.owner_column,
        )

        values = (
            owner_id,
            holiday_range_to_db(interval),
        )

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row = await cur.fetchone()

        if row is None:
            raise UnexpectedStateError

        return row["exists"]
