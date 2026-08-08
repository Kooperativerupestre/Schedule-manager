from pathlib import Path
import psycopg
from psycopg.rows import DictRow, dict_row
from typing import cast, LiteralString
import asyncio
import sys
import os
from schedule_manager.core.errors import UnexpectedStateError

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from schedule_manager.db.connection import open_pool, close_pool, get_transaction
from schedule_manager.db.connection import open_test_pool, close_test_pool, get_test_transaction
# Get migrations directory relative to the project root
project_root = Path(__file__).parent.parent
migrations_dir = project_root / "migrations"
files = sorted(migrations_dir.glob("*.sql"))


async def migration_applied(conn: psycopg.AsyncConnection[DictRow], filename:str) -> bool:
    try:
        result = await conn.execute(
        "SELECT 1 FROM schema_migrations WHERE filename = %s", (filename,)
        )
        row = await result.fetchone()
        return row is not None
    except psycopg.errors.UndefinedTable:
        raise
    return False

async def migration_table_exists(
    conn: psycopg.AsyncConnection[DictRow],
) -> bool:
    result = await conn.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'schema_migrations'
        )
        """
    )

    row = await result.fetchone()
    if row is None:
        raise UnexpectedStateError
    return row["exists"]

async def apply_migration(conn: psycopg.AsyncConnection[DictRow], filename:str, sql_content:str) -> None:
    await conn.execute(cast(LiteralString, sql_content))
    await conn.execute(
        "INSERT INTO schema_migrations (filename) VALUES (%s)", (filename,)
    )

async def run(conn: psycopg.AsyncConnection[DictRow], files:list[Path]) -> None:
    count = 0
    for file_path in files:
        sql_content = file_path.read_text()

        if count == 0 and not await migration_table_exists(conn):
            await conn.execute(cast(LiteralString, sql_content))
            await conn.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", (file_path.name,))


        if not await migration_applied(conn, file_path.name):
            try:
                await apply_migration(conn, file_path.name, sql_content)
            except Exception:
                raise

async def main() -> None:
    # run migrations on mainly database
    await open_pool()
    async for conn in get_transaction():
        await run(conn, files)
    await close_pool()

    # run migrations on test database
    await open_test_pool()
    async for conn in get_test_transaction():
        await run(conn, files)
    await close_test_pool()

if __name__ == "__main__":
    asyncio.run(main())