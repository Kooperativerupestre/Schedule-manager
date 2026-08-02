from schedule_manager.auth.models import Authentication, AuthenticationRow, Providers, AuthenticationOutput
from uuid import UUID
from psycopg import AsyncConnection
from psycopg.rows import class_row, DictRow
from psycopg import errors
from schedule_manager.auth.errors import UniquePersonProviderViolatedError, UniqueProviderIdentifierViolatedError
from schedule_manager.utils.namespace import namespace
from schedule_manager.core.errors import UnexpectedStateError


def authentication_row_to_model_authentication(row:AuthenticationRow) -> Authentication:
    return Authentication(
        provider=Providers(row.provider),
        credentials=row.credentials,
        identifier=row.identifier
    )


def authentication_row_to_model_authentication_output(row:AuthenticationRow) -> AuthenticationOutput:
    return AuthenticationOutput(
        authentication_id=row.id,
        person_id=row.person_id,
        credentials=row.credentials,
        identifier=row.identifier
    )


@namespace
class AuthenticationRepository:
    @staticmethod
    async def add(conn:AsyncConnection[DictRow], person_id:UUID, authentication_data:Authentication) -> UUID:
        query = """
INSERT INTO authentication (person_id, provider, identifier, credentials) VALUES (%s, %s, %s, %s) RETURNING id;
"""
        values = (person_id, authentication_data.provider.value, person_id, authentication_data.db_credentials)
        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                r = await cur.fetchone()

            if r is None:
                raise UnexpectedStateError
            return r['id']
        except errors.UniqueViolation as e:
            constraint = e.diag.constraint_name

            if constraint == "authentication_person_id_provider_key":
                raise UniquePersonProviderViolatedError
            elif constraint == "authentication_provider_identifier_key":
                raise UniqueProviderIdentifierViolatedError
            raise
    @staticmethod
    async def delete(id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        query = """
DELETE FROM authentication WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            r = cur.rowcount
        return r > 0
    
    @staticmethod
    async def get_all_from_person(conn:AsyncConnection[DictRow], person_id:UUID) -> list[AuthenticationOutput]:
        async with conn.cursor(row_factory=class_row(AuthenticationRow)) as cur:
            await cur.execute("SELECT person_id, provider, identifier, credentials FROM authentication WHERE person_id = %s", (person_id,))
            result = await cur.fetchall()

            return [authentication_row_to_model_authentication_output(r) for r in result]
    @staticmethod
    async def get_from_person_with_provider(conn:AsyncConnection[DictRow], person_id:UUID, provider:Providers) -> AuthenticationOutput | None:
        query = """
SELECT id, person_id, provider, identifier, credentials FROM authentication WHERE person_id = %s AND provider = %s;
"""
        values = (person_id, provider.value)
        async with conn.cursor(row_factory=class_row(AuthenticationRow)) as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()
        if r is None:
            return None
        return authentication_row_to_model_authentication_output(r)
    
    @staticmethod
    async def get(conn:AsyncConnection[DictRow], id:UUID) -> list[AuthenticationOutput]:
        query = "SELECT id, person_id, provider, identifier, credentials FROM authentication WHERE id = %s;"
        values = (id,)
        async with conn.cursor(row_factory=class_row(AuthenticationRow)) as cur:
            await cur.execute(query, values)
            result = await cur.fetchall()
        return [authentication_row_to_model_authentication_output(r) for r in result]
    