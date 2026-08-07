from schedule_manager.utils.namespace import namespace
from uuid import UUID
from psycopg import AsyncConnection
from psycopg import errors as psycopg_errors
from schedule_manager.business import errors as schedule_errors_business
from psycopg.rows import class_row, DictRow
from schedule_manager.people.errors import PersonNotFoundError
from schedule_manager.business.memberships.errors import (
    InviteAlreadyExistsError,
    CannotCreateBusinessMembershipInviteError,
    CannotAddMembershipError
)
from schedule_manager.business.memberships.models import (
    BusinessMembership,
    BusinessMembershipRow, 
    ModelTranslator,
    BusinessMembershipInvite,
    BusinessMembershipInviteRow,
)

from schedule_manager.business.memberships.status import (
    MembershipStatus
)

from schedule_manager.core.errors import EmailAlreadyExistsError

@namespace
class MembershipRepository:
    @staticmethod
    async def add(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> UUID:
        query = """
        INSERT INTO business_memberships (person_id, business_id) VALUES (%s, %s) RETURNING id;
        """
        values = (person_id, business_id)

        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                row = await cur.fetchone()
                if not row:
                    raise CannotAddMembershipError
                id = row["id"]
                return id
        except psycopg_errors.ForeignKeyViolation as e:
            match e.diag.constraint_name:
                case "business_memberships_business_id_fkey":
                    raise schedule_errors_business.BusinessNotFoundError
                case "business_memberships_person_id_fkey":
                    raise PersonNotFoundError
                case _:
                    raise
    @staticmethod
    async def has(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow], state:MembershipStatus | None) -> bool:
        if state is None:
            query = """
SELECT EXISTS (
    SELECT 1
    FROM business_memberships
    WHERE person_id = %s
      AND business_id = %s
);
"""
        elif state == MembershipStatus.ACTIVE:
            query = """
SELECT EXISTS (
    SELECT 1
    FROM business_memberships
    WHERE person_id = %s
      AND business_id = %s
      AND upper(validity_range) IS NULL
);"""
        elif state == MembershipStatus.ENDED:
            query = """
SELECT EXISTS (
    SELECT 1
    FROM business_memberships
    WHERE person_id = %s
      AND business_id = %s
      AND upper(validity_range) IS NOT NULL 
);"""
        else:
            raise ValueError(f"Unexpected membership status: {state!r}")
        values = (person_id, business_id)

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()
        assert r is not None
        return r["exists"]
    @staticmethod
    async def get(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow], state:MembershipStatus | None) -> list[BusinessMembership]:
        if state is None:
            query = """
SELECT validity_range, person_id, business_id, id FROM business_memberships WHERE person_id = %s AND business_id = %s;
"""
        elif state == MembershipStatus.ACTIVE:
            query = """
SELECT validity_range, person_id, business_id, id FROM business_memberships WHERE person_id = %s AND business_id = %s AND upper(validity_range) IS NULL;
"""
        elif state == MembershipStatus.ENDED:
            query = """
SELECT validity_range, person_id, business_id, id FROM business_memberships WHERE person_id = %s AND business_id = %s AND upper(end_at) IS NOT NULL;
"""
        else:
            raise ValueError(f"Unexpected membership status: {state!r}")
        values = (person_id, business_id)
        async with conn.cursor(row_factory=class_row(BusinessMembershipRow)) as cur:
            await cur.execute(query, values)
            r = await cur.fetchall()
        return [ModelTranslator.membership_row_to_mode(row) for row in r]

    @staticmethod
    async def end(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        query = """
UPDATE business_memberships
SET validity_range = tstzrange(
    lower(validity_range),
    now(),
    '[)'
)
WHERE person_id = %s AND business_id = %s AND upper(validity_range) IS NULL;
"""
        values = (person_id, business_id)
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        if row_count == 0:
            return False
        return True

    
@namespace
class MembershipInvitesRepository:
    @staticmethod
    async def add(business_id:UUID, email:str, conn:AsyncConnection[DictRow]) -> UUID:
        query = """
INSERT INTO business_membership_invites (business_id, email) VALUES (%s, %s) RETURNING id;
"""
        values = (business_id, email)
        try:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                r = await cur.fetchone()
                if not r:
                    raise CannotCreateBusinessMembershipInviteError
                return r["id"]
        except psycopg_errors.ForeignKeyViolation as e:
            match e.diag.constraint_name:
                case "business_membership_invites_business_id_fkey":
                    raise schedule_errors_business.BusinessNotFoundError
                case _:
                    raise
        except psycopg_errors.UniqueViolation as e:
            match e.diag.constraint_name:
                case "business_membership_invites_email_key":
                    raise EmailAlreadyExistsError
                case "business_membership_invites_unique":
                    raise InviteAlreadyExistsError
                case _:
                    raise
    @staticmethod
    async def end(id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        query = """
UPDATE business_membership_invites
SET validity_range = tstzrange(
    lower(validity_range),
    now(),
    '[)'
)
WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            row_count = cur.rowcount
        if row_count == 0:
            return False
        return True
    @staticmethod
    async def get(id:UUID, conn:AsyncConnection[DictRow]) -> BusinessMembershipInvite | None:
        query = """
SELECT id, created_at, expires_at, accepted_at FROM
business_membership_invites WHERE id = %s;
"""
        values = (id,)
        async with conn.cursor(row_factory=class_row(BusinessMembershipInviteRow)) as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()
        if r is None:
            return None
        return ModelTranslator.membership_invite_row_to_model(r)
    @staticmethod
    async def has_ended(id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        query = """
SELECT EXISTS (
    SELECT 1 FROM business_membership_invites
    WHERE id = %s AND upper(validity_range) IS NULL
) AS is_open;
"""
        values = (id,)

        async with conn.cursor() as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()
        if r is None:
            raise RuntimeError
        return r["is_open"]
    @staticmethod
    async def has_expired(id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        query = """
SELECT EXISTS (
    SELECT 1 FROM business_membership_invites
    WHERE id = %s AND expires_at > NOW()
) AS is_expired
""" 
        values = (id,)
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            r = await cur.fetchone()
        if r is None:
            raise RuntimeError
        return r["is_expired"]
    
        