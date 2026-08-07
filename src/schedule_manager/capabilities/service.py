from schedule_manager.capabilities.repository import (
    CapabilitiesRepository, 
    CapabilityInput, 
    Capability, 
    CapabilityAssignment
)
from schedule_manager.capabilities.capabilities import Resource
from schedule_manager.utils.namespace import namespace
from uuid import UUID
from psycopg import AsyncConnection
from schedule_manager.capabilities.schemas import CapabilityAddRequest, CapabilityEndRequest, CapabilityGetRequest
from psycopg.rows import DictRow
from schedule_manager.capabilities.validator import CapabilitiesValidator
from schedule_manager.business.memberships.validator import MembershipValidator
from schedule_manager.capabilities.errors import CapabilityNotFoundError

@namespace
class RequestTranslator:
    @staticmethod
    def capability_end_request_to_capability(entry:CapabilityEndRequest) -> Capability:
        return Capability(
            resource=entry.resource,
            action=entry.action
        )
    @staticmethod
    def capability_add_request_to_input(entry:CapabilityAddRequest) -> CapabilityInput:
        return CapabilityInput(
            resource=entry.resource,
            action=entry.action,
            end_at=entry.end_at
        )
    @staticmethod
    def capability_get_request_to_capability(entry:CapabilityGetRequest) -> Capability:
        return Capability(
            resource=entry.resource,
            action=entry.action
        )



@namespace
class CapabilitiesService:
    @staticmethod
    async def has(person_id:UUID, target_person_id:UUID, request:CapabilityGetRequest, conn:AsyncConnection[DictRow]) -> bool:
        await CapabilitiesValidator.validate_read_capability(person_id, request.resource, request.target_id, conn)
        return await CapabilitiesRepository.has(target_person_id, request.target_id,
                                                RequestTranslator.capability_get_request_to_capability(request), conn)
    @staticmethod
    async def add(person_id:UUID, target_person_id:UUID, request:CapabilityAddRequest, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, request.resource, request.target_id, conn)
        await MembershipValidator.validate_membership(target_person_id, request.target_id, conn)
        await CapabilitiesRepository.add(target_person_id, request.target_id, RequestTranslator.capability_add_request_to_input(request), conn)
    @staticmethod
    async def end_all(person_id:UUID, target_person_id:UUID, request:CapabilityEndRequest, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, request.resource, request.target_id, conn)

        r = await CapabilitiesRepository.end_all_from_target(target_person_id, request.target_id, RequestTranslator.capability_end_request_to_capability(request), conn)
        if not r:
            raise CapabilityNotFoundError
    @staticmethod
    async def end(person_id:UUID, id:UUID, resource:Resource, target_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await CapabilitiesValidator.validate_manage_capability(person_id, resource, target_id, conn)
        r = await CapabilitiesRepository.end(id, conn)
        if not r:
            raise CapabilityNotFoundError

    @staticmethod
    async def get_all(person_id:UUID, target_person_id:UUID, request:CapabilityGetRequest, conn:AsyncConnection[DictRow]) -> list[CapabilityAssignment]:
        if person_id != target_person_id:
            await CapabilitiesValidator.validate_manage_capability(person_id, request.resource , target_person_id, conn)
        return await CapabilitiesRepository.get_all_from_person(person_id, request.target_id,
                                                                RequestTranslator.capability_get_request_to_capability(request), conn)
    @staticmethod
    async def get_last(person_id:UUID, target_person_id:UUID, request:CapabilityGetRequest, conn:AsyncConnection[DictRow], k:int = 1) -> list[CapabilityAssignment]:
        if person_id != target_person_id:
            await CapabilitiesValidator.validate_manage_capability(person_id, request.resource, target_person_id, conn)
        return await CapabilitiesRepository.get_last(person_id, target_person_id,
                                                    RequestTranslator.capability_get_request_to_capability(request), conn, k)
    
