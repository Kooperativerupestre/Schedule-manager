import psycopg
from psycopg import sql
from app.config import Settings
import asyncio

async def create_database(conn: psycopg.AsyncConnection, dbname: str) -> None:
    await conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    
async def database_exists(conn: psycopg.AsyncConnection, dbname: str) -> bool:
    result = await conn.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
    )
    row = await result.fetchone()
    return row is not None

async def setup_database(admin_url:str, dbname:str) -> None:
    async with await psycopg.AsyncConnection.connect(admin_url) as conn:
        await conn.set_autocommit(True)
        exists = await database_exists(conn, dbname)
        if not exists:
            await create_database(conn, dbname)

if __name__ == "__main__":
    settings = Settings() # type: ignore
    admin_url = settings.get_admin_url(settings.database_url)
    asyncio.run(setup_database(admin_url, "schedule_db"))
