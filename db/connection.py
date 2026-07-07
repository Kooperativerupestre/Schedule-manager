from psycopg_pool import AsyncConnectionPool
from app.config import Settings
from typing import AsyncGenerator
from psycopg import AsyncConnection
from psycopg.rows import dict_row

settings = Settings() # type: ignore

pool = AsyncConnectionPool(
    conninfo=settings.database_url,
    open=False,
    kwargs={"row_factory": dict_row}
)

async def open_pool() -> None:
    await pool.open()

async def close_pool() -> None:
    await pool.close()

async def get_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with pool.connection() as conn:
        yield conn