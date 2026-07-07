from dataclasses import dataclass
from psycopg import AsyncConnection
from psycopg.rows import class_row
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class AddPersonInput:
    name: str
    number_phone: str

@dataclass(frozen=True)
class AddPersonOutput:
    id: UUID
    created_at: datetime

@dataclass(frozen=True)
class GetPerson:
    name: str
    number_phone: str
    id: UUID
    created_at: datetime
    status: bool

class PeopleRepository:
    @staticmethod
    async def add(conn: AsyncConnection, person: AddPersonInput) -> AddPersonOutput | None:
        async with conn.cursor(row_factory=class_row(AddPersonOutput)) as cur:
            await cur.execute(
                "INSERT INTO people (name, number_phone) VALUES (%s, %s) RETURNING id, created_at", 
                (person.name, person.number_phone)
            )
            result = await cur.fetchone()
            return result   

    @staticmethod
    async def get(conn: AsyncConnection, id: UUID) -> GetPerson | None:
        async with conn.cursor(row_factory=class_row(GetPerson)) as cur:
            await cur.execute("SELECT name, number_phone, id, created_at, status FROM people WHERE id = %s", (id,))
            result = await cur.fetchone()
            return result

    @staticmethod
    async def get_latest(conn: AsyncConnection, n: int) -> list[GetPerson]:
        async with conn.cursor(row_factory=class_row(GetPerson)) as cur:
            await cur.execute("SELECT name, number_phone, id, created_at, status FROM people ORDER BY created_at DESC LIMIT %s", (n,))
            return await cur.fetchall()

    @staticmethod
    async def delete(conn: AsyncConnection, id: UUID) -> GetPerson | None:
        async with conn.cursor(row_factory=class_row(GetPerson)) as cur:
            await cur.execute("DELETE FROM people WHERE id = %s RETURNING name, number_phone, id, created_at, status", (id,))
            return await cur.fetchone()