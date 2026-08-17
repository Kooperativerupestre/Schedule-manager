from argon2 import PasswordHasher
from schedule_manager.auth.repository import AuthenticationRepository
from schedule_manager.auth.models import AuthenticationModelsConstructor, Providers
from argon2.exceptions import VerificationError, VerifyMismatchError
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from uuid import UUID
from schedule_manager.utils.namespace import namespace
from schedule_manager.auth.errors import InvalidCredentialsError
from schedule_manager.utils.service_logging import log_service_errors
import logging

logger = logging.getLogger(__name__)


@log_service_errors
@namespace
class AuthenticationService:
    @staticmethod
    async def local_login(
        conn: AsyncConnection[DictRow], person_id: UUID, password: str
    ) -> UUID:
        r = await AuthenticationRepository.get_from_person_with_provider(
            conn, person_id, Providers.LOCAL
        )
        ph = PasswordHasher()

        if r is None:
            raise InvalidCredentialsError

        stored_hash: str = r.credentials["hash"]  # type: ignore

        try:
            ph.verify(stored_hash, password)
        except (VerifyMismatchError, VerificationError):
            raise InvalidCredentialsError
        logger.info(
            "authentication.login_succeeded",
            extra={
                "person_id": str(person_id),
                "authentication_id": str(r.authentication_id),
                "provider": Providers.LOCAL.name,
            },
        )
        return r.authentication_id

    @staticmethod
    async def add_local_login(
        conn: AsyncConnection[DictRow], person_id: UUID, password: str
    ) -> None:
        await AuthenticationRepository.add(
            conn,
            person_id,
            AuthenticationModelsConstructor.gen_local_authentication(
                password, person_id
            ),
        )
        logger.info(
            "authentication.local_login_added",
            extra={"person_id": str(person_id), "provider": Providers.LOCAL.name},
        )

    @staticmethod
    async def delete(conn: AsyncConnection[DictRow], person_id: UUID) -> bool:
        deleted = await AuthenticationRepository.delete(person_id, conn)
        if deleted:
            logger.info(
                "authentication.deleted",
                extra={"person_id": str(person_id), "provider": Providers.LOCAL.name},
            )
        return deleted
