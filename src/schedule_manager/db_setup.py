import psycopg
from psycopg.rows import DictRow
from psycopg import sql
from schedule_manager.config import settings
import asyncio

async def create_database(conn: psycopg.AsyncConnection[DictRow], dbname: str) -> None:
    await conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    
async def database_exists(conn: psycopg.AsyncConnection[DictRow], dbname: str) -> bool:
    result = await conn.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
    )
    row = await result.fetchone()
    return row is not None

async def setup_database(admin_url:str, dbname:str) -> None:
    async with await psycopg.AsyncConnection.connect(admin_url) as conn:
        exists = await database_exists(conn, dbname)
        if not exists:
            await create_database(conn, dbname)
            await conn.commit()

if __name__ == "__main__":
    admin_url = settings.get_admin_url(settings.database_url)
    asyncio.run(setup_database(admin_url, "schedule_db"))
