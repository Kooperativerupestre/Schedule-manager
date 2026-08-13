from __future__ import annotations
from psycopg import AsyncConnection, errors
from psycopg.rows import class_row, DictRow
from uuid import UUID
from schedule_manager.people.models import UpdatePerson, AddPersonInput, AddPersonOutput, GetPerson
from schedule_manager.common.missing import MISSING
from schedule_manager.core.errors import PhoneNumberAlreadyExistsError, UnexpectedStateError
from schedule_manager.utils.service_logging import log_repository_error





class PeopleRepository:
    @staticmethod
    async def add(conn: AsyncConnection[DictRow], person: AddPersonInput) -> AddPersonOutput:
        try:
            async with conn.cursor(row_factory=class_row(AddPersonOutput)) as cur:
                await cur.execute(
                    "INSERT INTO people (name, phone_number) VALUES (%s, %s) RETURNING id, created_at", 
                    (person.name, person.phone_number)
                )
                result = await cur.fetchone()
                if result is None:
                    raise UnexpectedStateError
                return result
        except errors.UniqueViolation as error:
            log_repository_error(PeopleRepository, "add", error, {"phone_number": person.phone_number})
            raise PhoneNumberAlreadyExistsError('Phone number {} already exists'.format(person.phone_number))
        

    @staticmethod
    async def get(conn: AsyncConnection[DictRow], id: UUID) -> GetPerson | None:
        async with conn.cursor(row_factory=class_row(GetPerson)) as cur:
            await cur.execute("SELECT name, phone_number, id, created_at, status FROM people WHERE id = %s", (id,))
            result = await cur.fetchone()
            return result

    @staticmethod
    async def get_latest(conn: AsyncConnection[DictRow], n: int) -> list[GetPerson]:
        async with conn.cursor(row_factory=class_row(GetPerson)) as cur:
            await cur.execute("SELECT name, phone_number, id, created_at, status FROM people ORDER BY created_at DESC LIMIT %s", (n,))
            return await cur.fetchall()

    @staticmethod
    async def delete(conn: AsyncConnection[DictRow], id: UUID) -> GetPerson | None:
        async with conn.cursor(row_factory=class_row(GetPerson)) as cur:
            await cur.execute("DELETE FROM people WHERE id = %s RETURNING name, phone_number, id, created_at, status", (id,))
            return await cur.fetchone()
    @staticmethod
    async def update(conn: AsyncConnection[DictRow], id: UUID, update: UpdatePerson) -> bool:
        updates = []
        values: list[bool | str | UUID | None] = []

        if update.name is not MISSING:
            updates.append("name = %s")
            values.append(update.name)

        if update.phone_number is not MISSING:
            updates.append("phone_number = %s")
            values.append(update.phone_number)

        if update.status is not MISSING:
            updates.append("status = %s")
            values.append(update.status)

        if len(updates) == 0:
            return False

        updates.append("last_update = now()")

        query = f"""
        UPDATE people
        SET {", ".join(updates)}
        WHERE id = %s
        """

        values.append(id)

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                row_count = cur.rowcount
                return row_count > 0

        except errors.UniqueViolation as error:
            log_repository_error(PeopleRepository, "update", error, {"person_id": str(id)})
            raise PhoneNumberAlreadyExistsError(
                f"Phone number {update.phone_number} already exists"
            )
