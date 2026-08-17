from schedule_manager.capabilities.capabilities import (
    Capability,
    Scope,
    COLUMN_BY_SCOPE,
    Resource,
    Action,
)
from uuid import UUID
from psycopg import AsyncConnection
from psycopg import errors as psycopg_errors
from psycopg import sql
from psycopg.rows import class_row, DictRow
import schedule_manager.capabilities.errors as schedule_errors
from enum import Enum, auto
from schedule_manager.utils.namespace import namespace
from schedule_manager.core.ranges.models import create_db_range
from schedule_manager.capabilities.models import (
    CapabilityAssignment,
    CapabilityInput,
    CapabilityRow,
    capability_row_to_assignment,
)
from schedule_manager.people.errors import PersonNotFoundError
from schedule_manager.core.errors import OverlappingSchedulesError, UnexpectedStateError
from schedule_manager.core.ranges.constants import DB_BEGIN, NEVER_END
from schedule_manager.utils.service_logging import log_repository_error


class Constraints(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    PERSON_CAPABILITIES_PERSON_ID_FKEY = auto()
    PERSON_CAPABILITIES_BUSINESS_ID_FKEY = auto()
    PERSON_CAPABILITIES_WORKSTATION_ID_FKEY = auto()
    PERSON_CAPABILITIES_UNIT_ID_FKEY = auto()
    PERSON_CAPABILITIES_CAPABILITY_ID_FKEY = auto()


@namespace
class CapabilitiesRepository:
    @staticmethod
    async def has(
        person_id: UUID,
        target_id: UUID,
        capability: Capability,
        conn: AsyncConnection[DictRow],
    ) -> bool:
        values = (person_id, capability.name, target_id)

        column_name = capability.column_name

        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1
                FROM person_capabilities pc
                JOIN capabilities c 
                    ON pc.capability_id = c.id
                WHERE pc.person_id = %s
                  AND c.capability = %s
                  AND pc.{} = %s
                  AND pc.validity_range @> now()
            );
        """).format(sql.Identifier(column_name))

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()

        return r["exists"] if r else False

    @staticmethod
    async def add(
        person_id: UUID,
        target_id: UUID,
        capability: CapabilityInput,
        conn: AsyncConnection[DictRow],
    ) -> UUID:
        begin_at = DB_BEGIN

        validity_range = create_db_range(begin_at, capability.end_at)

        values = (person_id, capability.name, target_id, validity_range)

        column_name = capability.column_name

        query = sql.SQL("""
            INSERT INTO person_capabilities (
                person_id,
                capability_id,
                {},
                validity_range
            )
            VALUES (
                %s,
                (
                    SELECT id 
                    FROM capabilities 
                    WHERE capability = %s
                ),
                %s,
                %s
            )
            RETURNING id;
        """).format(sql.Identifier(column_name))

        async with conn.cursor() as cur:
            try:
                await cur.execute(query, values)
                r = await cur.fetchone()

            except psycopg_errors.ExclusionViolation as error:
                log_repository_error(
                    CapabilitiesRepository,
                    "add",
                    error,
                    {
                        "person_id": str(person_id),
                        "target_id": str(target_id),
                        "capability": capability.name,
                    },
                )
                raise OverlappingSchedulesError

            except psycopg_errors.NotNullViolation as error:
                log_repository_error(
                    CapabilitiesRepository,
                    "add",
                    error,
                    {
                        "person_id": str(person_id),
                        "target_id": str(target_id),
                        "capability": capability.name,
                    },
                )
                raise schedule_errors.NullCapabilityError

            except psycopg_errors.ForeignKeyViolation as e:
                log_repository_error(
                    CapabilitiesRepository,
                    "add",
                    e,
                    {
                        "person_id": str(person_id),
                        "target_id": str(target_id),
                        "capability": capability.name,
                    },
                )

                c_name = e.diag.constraint_name

                if c_name in [
                    Constraints.PERSON_CAPABILITIES_BUSINESS_ID_FKEY.value,
                    Constraints.PERSON_CAPABILITIES_UNIT_ID_FKEY.value,
                    Constraints.PERSON_CAPABILITIES_WORKSTATION_ID_FKEY.value,
                ]:
                    raise schedule_errors.TargetNotFoundError

                elif c_name == Constraints.PERSON_CAPABILITIES_PERSON_ID_FKEY.value:
                    raise PersonNotFoundError

                elif c_name == Constraints.PERSON_CAPABILITIES_CAPABILITY_ID_FKEY.value:
                    raise schedule_errors.CapabilityNameError

                raise

        if r is None:
            raise UnexpectedStateError
        return r["id"]

    @staticmethod
    async def end_all(
        person_id: UUID,
        target_id: UUID,
        capability: Capability,
        conn: AsyncConnection[DictRow],
    ) -> bool:
        values = (person_id, capability.name, target_id)

        column_name = capability.column_name

        query = sql.SQL("""
            UPDATE person_capabilities
            SET validity_range =
                tstzrange(lower(validity_range), now(), '[)')
            WHERE person_id = %s
              AND capability_id = (
                  SELECT id
                  FROM capabilities
                  WHERE capability = %s
              )
              AND {} = %s
              AND validity_range @> now();
        """).format(sql.Identifier(column_name))

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            return cur.rowcount > 0

    @staticmethod
    async def end(id: UUID, conn: AsyncConnection[DictRow]) -> bool:
        query = """
UPDATE person_capabilities SET validity_range = tstzrange(lower(validity_range), now(), '[)')
WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            return cur.rowcount > 0

    @staticmethod
    async def get_all_from_person(
        person_id: UUID,
        target_id: UUID,
        capability: Capability,
        conn: AsyncConnection[DictRow],
    ) -> list[CapabilityAssignment]:
        column_name = capability.column_name

        query = sql.SQL("""
            SELECT 
                c.capability,
                pc.business_id,
                pc.unit_id,
                pc.workstation_id,
                pc.validity_range
            FROM person_capabilities pc
            JOIN capabilities c 
                ON pc.capability_id = c.id
            WHERE pc.person_id = %s
              AND c.capability = %s
              AND {} = %s;
        """).format(sql.Identifier(column_name))

        values = (person_id, capability.name, target_id)

        async with conn.cursor(row_factory=class_row(CapabilityRow)) as cur:
            await cur.execute(query, values)
            rows = await cur.fetchall()

        return [capability_row_to_assignment(row) for row in rows]

    @staticmethod
    async def get_last(
        person_id: UUID,
        target_id: UUID,
        capability: Capability,
        conn: AsyncConnection[DictRow],
        k: int = 1,
    ) -> list[CapabilityAssignment]:
        if k <= 0:
            raise ValueError(f"k {k} must be > 0")

        column_name = capability.column_name

        query = sql.SQL("""
            SELECT 
                c.capability,
                pc.business_id,
                pc.unit_id,
                pc.workstation_id,
                pc.validity_range
            FROM person_capabilities pc
            JOIN capabilities c 
                ON pc.capability_id = c.id
            WHERE pc.person_id = %s
              AND c.capability = %s
              AND {} = %s
            ORDER BY lower(pc.validity_range) DESC
            LIMIT %s;
        """).format(sql.Identifier(column_name))

        values = (person_id, capability.name, target_id, k)

        async with conn.cursor(row_factory=class_row(CapabilityRow)) as cur:
            await cur.execute(query, values)
            rows = await cur.fetchall()

        return [capability_row_to_assignment(row) for row in rows]

    @staticmethod
    async def make_admin(person_id: UUID, conn: AsyncConnection[DictRow]) -> None:
        query = """
            INSERT INTO admins (person_id)
            VALUES (%s);
        """

        async with conn.cursor() as cur:
            await cur.execute(query, (person_id,))

    @staticmethod
    async def end_all_from_target(
        person_id: UUID, target_id: UUID, scope: Scope, conn: AsyncConnection[DictRow]
    ) -> bool:
        query = sql.SQL("""
            DELETE FROM person_capabilities
            WHERE person_id = %s
              AND {} = %s
        """).format(COLUMN_BY_SCOPE[scope])

        values = (person_id, target_id)

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            return cur.rowcount > 0

    @staticmethod
    async def add_capability_resource(
        person_id: UUID, target_person_id: UUID, conn: AsyncConnection[DictRow]
    ) -> None:
        await CapabilitiesRepository.add(
            target_person_id,
            person_id,
            CapabilityInput(Resource.CAPABILITIES, Action.READ, NEVER_END),
            conn,
        )
        await CapabilitiesRepository.add(
            target_person_id,
            person_id,
            CapabilityInput(Resource.CAPABILITIES, Action.MANAGE, NEVER_END),
            conn,
        )
