from psycopg_pool import AsyncConnectionPool
from schedule_manager.config import Settings
from typing import AsyncGenerator
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow


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

async def get_connection() -> AsyncGenerator[AsyncConnection[DictRow], None]:
    async with pool.connection() as conn:
        yield conn
async def get_transaction() -> AsyncGenerator[AsyncConnection[DictRow], None]:
    async with pool.connection() as conn:
        async with conn.transaction():
            yield conn