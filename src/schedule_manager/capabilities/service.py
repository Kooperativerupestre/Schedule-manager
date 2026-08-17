from schedule_manager.capabilities.repository import (
    CapabilitiesRepository, 
    CapabilityInput, 
    Capability, 
    CapabilityAssignment
)
from schedule_manager.capabilities.capabilities import Resource, Action
from schedule_manager.utils.namespace import namespace
from uuid import UUID
from psycopg import AsyncConnection
from schedule_manager.capabilities.schemas import CapabilityAddRequest, CapabilityEndRequest, CapabilityGetRequest
from psycopg.rows import DictRow
from schedule_manager.capabilities.validator import CapabilitiesValidator
from schedule_manager.business.memberships.validator import MembershipValidator
from schedule_manager.capabilities.errors import CapabilityNotFoundError
from schedule_manager.core.ranges.constants import NEVER_END
from schedule_manager.utils.service_logging import log_service_errors
import logging

logger = logging.getLogger(__name__)

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



@log_service_errors
@namespace
class CapabilitiesService:
    @staticmethod
    async def has(person_id:UUID, target_person_id:UUID, business_id:UUID, request:CapabilityGetRequest, conn:AsyncConnection[DictRow]) -> bool:
        await CapabilitiesValidator.validate_read_capability(person_id, Resource.CAPABILITIES, business_id, conn)
        return await CapabilitiesRepository.has(target_person_id, request.target_id,
                                                RequestTranslator.capability_get_request_to_capability(request), conn)
    @staticmethod
    async def add(
        person_id: UUID,
        target_person_id: UUID,
        business_id: UUID,
        request: CapabilityAddRequest,
        conn: AsyncConnection[DictRow],
    ) -> UUID:
        await CapabilitiesValidator.validate_manage_capability(
            person_id,
            Resource.CAPABILITIES,
            business_id,
            conn,
        )
        await MembershipValidator.validate_membership(
            target_person_id,
            business_id,
            conn,
        )

        capability_id = await CapabilitiesRepository.add(
            target_person_id,
            request.target_id,
            RequestTranslator.capability_add_request_to_input(request),
            conn,
        )

        logger.info(
            "capability.granted",
            extra={
                "actor_id": str(person_id),
                "target_person_id": str(target_person_id),
                "business_id": str(business_id),
                "resource": request.resource.name,
                "action": request.action.name,
                "target_id": str(request.target_id),
                "end_at": request.end_at.isoformat() if request.end_at is not NEVER_END else NEVER_END,
                "capability_id": str(capability_id),
            },
        )

        return capability_id


    @staticmethod
    async def add_without_verifying(
        person_id: UUID,
        target_person_id: UUID,
        request: CapabilityAddRequest,
        conn: AsyncConnection[DictRow],
    ) -> UUID:
        capability_id = await CapabilitiesRepository.add(
            target_person_id,
            request.target_id,
            RequestTranslator.capability_add_request_to_input(request),
            conn,
        )

        logger.info(
            "capability.granted_without_verification",
            extra={
                "actor_id": str(person_id),
                "target_person_id": str(target_person_id),
                "resource": request.resource.name,
                "action": request.action.name,
                "target_id": str(request.target_id),
                "end_at": request.end_at.isoformat() if request.end_at is not NEVER_END else NEVER_END,
                "capability_id": str(capability_id),
            },
        )

        return capability_id


    @staticmethod
    async def end_all(
        person_id: UUID,
        target_person_id: UUID,
        business_id: UUID,
        request: CapabilityEndRequest,
        conn: AsyncConnection[DictRow],
    ) -> None:
        await CapabilitiesValidator.validate_manage_capability(
            person_id,
            Resource.CAPABILITIES,
            business_id,
            conn,
        )

        capability = RequestTranslator.capability_end_request_to_capability(request)

        result = await CapabilitiesRepository.end_all(
            target_person_id,
            request.target_id,
            capability,
            conn,
        )

        if not result:
            logger.warning(
                "capability.not_found",
                extra={
                    "actor_id": str(person_id),
                    "target_person_id": str(target_person_id),
                    "business_id": str(business_id),
                    "resource": capability.resource.name,
                    "action": capability.action.name,
                    "target_id": str(request.target_id),
                },
            )
            raise CapabilityNotFoundError

        logger.info(
            "capability.revoked",
            extra={
                "actor_id": str(person_id),
                "target_person_id": str(target_person_id),
                "business_id": str(business_id),
                "resource": capability.resource.name,
                "action": capability.action.name,
                "target_id": str(request.target_id),
            },
        )


    @staticmethod
    async def end(
        person_id: UUID,
        id: UUID,
        target_id: UUID,
        conn: AsyncConnection[DictRow],
    ) -> None:
        await CapabilitiesValidator.validate_manage_capability(
            person_id,
            Resource.CAPABILITIES,
            target_id,
            conn,
        )

        result = await CapabilitiesRepository.end(id, conn)

        if not result:
            logger.warning(
                "capability.not_found",
                extra={
                    "actor_id": str(person_id),
                    "capability_id": str(id),
                    "target_id": str(target_id),
                    "resource": Resource.CAPABILITIES.name,
                    "action": Action.MANAGE.name,
                },
            )
            raise CapabilityNotFoundError

        logger.info(
            "capability.revoked",
            extra={
                "actor_id": str(person_id),
                "capability_id": str(id),
                "target_id": str(target_id),
                "resource": Resource.CAPABILITIES.name,
                "action": Action.MANAGE.name,
            },
        )

    @staticmethod
    async def get_all(person_id:UUID, target_person_id:UUID, business_id:UUID, request:CapabilityGetRequest, conn:AsyncConnection[DictRow]) -> list[CapabilityAssignment]:
        if person_id != target_person_id:
            await CapabilitiesValidator.validate_manage_capability(person_id, Resource.CAPABILITIES , business_id, conn)
        return await CapabilitiesRepository.get_all_from_person(person_id, request.target_id,
                                                                RequestTranslator.capability_get_request_to_capability(request), conn)
    @staticmethod
    async def get_last(person_id:UUID, target_person_id:UUID, business_id:UUID, request:CapabilityGetRequest, conn:AsyncConnection[DictRow], k:int = 1) -> list[CapabilityAssignment]:
        if person_id != target_person_id:
            await CapabilitiesValidator.validate_manage_capability(person_id, Resource.CAPABILITIES, business_id, conn)
        return await CapabilitiesRepository.get_last(person_id, target_person_id,
                                                    RequestTranslator.capability_get_request_to_capability(request), conn, k)
    
