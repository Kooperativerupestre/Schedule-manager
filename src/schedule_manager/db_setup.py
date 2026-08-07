import psycopg
from psycopg.rows import DictRow
from psycopg import sql
from schedule_manager.db.connection import get_transaction
import asyncio

async def create_database(conn: psycopg.AsyncConnection[DictRow], dbname: str) -> None:
    await conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    
async def database_exists(conn: psycopg.AsyncConnection[DictRow], dbname: str) -> bool:
    result = await conn.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
    )
    row = await result.fetchone()
    return row is not None

async def setup_database(dbname:str) -> None:
    async for conn in get_transaction():
        exists = await database_exists(conn, dbname)
        if not exists:
            await create_database(conn, dbname)

if __name__ == "__main__":
    asyncio.run(setup_database("schedule_db"))
