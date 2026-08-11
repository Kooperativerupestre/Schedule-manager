from psycopg_pool import AsyncConnectionPool
from schedule_manager.config import Settings
from typing import AsyncGenerator
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow
import psycopg

settings = Settings() # type: ignore

pool = AsyncConnectionPool(
    conninfo=settings.database_url,
    open=False,
    kwargs={"row_factory": dict_row}
)

test_pool = AsyncConnectionPool(
    conninfo=settings.test_database_url,
    min_size=1,
    max_size=5,
    timeout=5,
    kwargs={"row_factory": dict_row},
    open=False
)




async def open_pool() -> None:
    await pool.open()

async def close_pool() -> None:
    await pool.close()

async def open_test_pool() -> None:
    await test_pool.open()
async def close_test_pool() -> None:
    await test_pool.close()

async def get_connection() -> AsyncGenerator[AsyncConnection[DictRow], None]:
    async with pool.connection() as conn:
        yield conn
async def get_transaction() -> AsyncGenerator[AsyncConnection[DictRow], None]:
    async with pool.connection() as conn:
        async with conn.transaction():
            yield conn
async def get_test_transaction() -> AsyncGenerator[AsyncConnection[DictRow], None]:
    async with test_pool.connection() as conn:
        async with conn.transaction():
            yield conn

async def get_test_connection():
    async with test_pool.connection() as conn:
        async with conn.transaction() as tx:
            yield conn
            raise psycopg.Rollback(tx)
