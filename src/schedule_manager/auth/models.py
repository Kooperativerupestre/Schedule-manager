from dataclasses import dataclass
from typing import Any
from uuid import UUID
from psycopg.types.json import Jsonb
from argon2 import PasswordHasher
from schedule_manager.utils.namespace import namespace
from enum import Enum, auto


class Providers(Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[Any]
    ) -> str:
        return name

    LOCAL = auto()


def gen_local_hash(password: str) -> str:
    ph = PasswordHasher()

    return ph.hash(password)


@dataclass(frozen=True)
class AuthenticationRow:
    id: UUID
    person_id: UUID
    provider: str
    credentials: dict[str, str | int | float | bool]
    identifier: str | UUID


@dataclass(frozen=True)
class Authentication:
    provider: Providers
    credentials: dict[str, str | int | float | bool]
    identifier: str | UUID

    @property
    def db_credentials(self) -> Jsonb:
        return Jsonb(self.credentials)


@dataclass(frozen=True)
class AuthenticationOutput:
    authentication_id: UUID
    person_id: UUID
    credentials: dict[str, str | int | float | bool]
    identifier: str | UUID


@namespace
class AuthenticationModelsConstructor:
    @staticmethod
    def gen_local_authentication(password: str, person_id: UUID) -> Authentication:
        local_hash = gen_local_hash(password)

        return Authentication(
            provider=Providers.LOCAL,
            credentials={"hash": local_hash},
            identifier=person_id,
        )
