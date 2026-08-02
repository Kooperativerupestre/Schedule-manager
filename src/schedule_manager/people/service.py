from uuid import UUID
from psycopg import AsyncConnection
from schedule_manager.people.repository import PeopleRepository
from schedule_manager.people.models import (
    GetPerson,
    AddPersonInput,
    AddPersonOutput,
    UpdatePerson
)
from schedule_manager.people.errors import PersonNotFoundError
from schedule_manager.people.schemas import LocalPersonCreateRequest, PersonUpdateRequest
from schedule_manager.auth.service import AuthenticationService
from schedule_manager.utils.namespace import namespace
from psycopg.rows import DictRow


@namespace
class RequestTranslator:
    @staticmethod
    def local_person_create_to_add_person_input(request:LocalPersonCreateRequest) -> AddPersonInput:
        return AddPersonInput(
            request.name, request.phone_number
        )
    @staticmethod

    def person_update_request_to_update_person(request:PersonUpdateRequest) -> UpdatePerson:
        return UpdatePerson(
            request.name, request.phone_number, request.status
        )


@namespace
class PeopleService:
    @staticmethod
    async def create_local(conn:AsyncConnection[DictRow], request:LocalPersonCreateRequest) -> AddPersonOutput:
        try:
            output = await PeopleRepository.add(
                conn, RequestTranslator.local_person_create_to_add_person_input(request)
            )
            await AuthenticationService.add_local_login(conn, output.id, request.password)
        except Exception:
            raise
        return output
    
    @staticmethod
    async def get(conn:AsyncConnection[DictRow], person_id:UUID) -> GetPerson:
        person = await PeopleRepository.get(conn, person_id)

        if person is None:
            raise PersonNotFoundError('Person with id {} was not found'.format(person_id))
        return person
    @staticmethod
    async def delete(conn:AsyncConnection[DictRow], person_id:UUID) -> None:
        person = await PeopleRepository.delete(conn, person_id)

        if person is None:
            raise PersonNotFoundError
    @staticmethod
    async def list_latest(conn: AsyncConnection[DictRow], n: int) -> list[GetPerson]:
        results = await PeopleRepository.get_latest(conn, n)
        return results
    @staticmethod
    async def update(conn:AsyncConnection[DictRow], id_to_update:UUID, update:PersonUpdateRequest):
        update_input = RequestTranslator.person_update_request_to_update_person(update)
        changed = await PeopleRepository.update(conn,
                                                      id_to_update,
                                                      update_input)

        if not changed:
            raise PersonNotFoundError('Person with id {} was not found'.format(id_to_update))

    