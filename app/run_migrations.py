from pathlib import Path
import psycopg
from typing import cast, LiteralString
import asyncio
from app.config import Settings

migrations_dir = Path("migrations")
files = sorted(migrations_dir.glob("*.sql"))

async def migration_applied(conn: psycopg.AsyncConnection, filename:str) -> bool:
    try:
        result = await conn.execute(
        "SELECT 1 FROM schema_migrations WHERE filename = %s", (filename,)
        )
        row = await result.fetchone()
        return row is not None
    except psycopg.errors.UndefinedTable:
        await conn.rollback()
        return False

async def apply_migration(conn: psycopg.AsyncConnection, filename:str, sql_content:str) -> None:
    await conn.execute(cast(LiteralString, sql_content))
    await conn.execute(
        "INSERT INTO schema_migrations (filename) VALUES (%s)", (filename,)
    )
    await conn.commit()

async def run(conn: psycopg.AsyncConnection, files:list[Path]) -> None:
    for file_path in files:
        sql_content = file_path.read_text()

        if not await migration_applied(conn, file_path.name):
            try:
                await apply_migration(conn, file_path.name, sql_content)
            except Exception:
                await conn.rollback()
                raise

async def main() -> None:
    settings = Settings() # type: ignore

    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:
        await run(conn, files)

if __name__ == "__main__":
    asyncio.run(main())