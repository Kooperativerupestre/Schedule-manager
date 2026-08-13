from schedule_manager.business.repository import BusinessRepository
from schedule_manager.business.models import Business, BusinessChanges, BusinessOutput
from schedule_manager.utils.namespace import namespace
from schedule_manager.business.schemas import BusinessAddRequest, BusinessUpdateRequest
from psycopg import AsyncConnection
from uuid import UUID
from schedule_manager.business.errors import BusinessNotFoundError
from schedule_manager.common.missing import MISSING
from schedule_manager.business.memberships.repository import MembershipRepository
from schedule_manager.business.validator import BusinessValidator
from schedule_manager.capabilities.repository import CapabilitiesRepository
from schedule_manager.capabilities.capabilities import Resource, Action
from schedule_manager.capabilities.models import CapabilityInput
from psycopg.rows import DictRow
from schedule_manager.core.ranges.constants import NEVER_END
from schedule_manager.utils.service_logging import log_service_errors, model_context
import logging

logger = logging.getLogger(__name__)

@namespace
class RequestTranslator:
    @staticmethod
    def add_request_to_business(request:BusinessAddRequest) -> Business:
        return Business(
            request.name,
            request.description,
            request.phone_number
        )
    @staticmethod
    def update_request_to_business(request: BusinessUpdateRequest) -> BusinessChanges:
        fields = request.model_fields_set
        return BusinessChanges(
            name=request.name if "name" in fields else MISSING,
            description=request.description if "description" in fields else MISSING,
            phone_number=request.phone_number if "phone_number" in fields else MISSING,
        )


        
@log_service_errors
@namespace
class BusinessService:
    @staticmethod
    async def add(person_id:UUID, request:BusinessAddRequest, conn:AsyncConnection[DictRow]) -> UUID:
        business_id = await BusinessRepository.add(RequestTranslator.add_request_to_business(request), conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.BUSINESS, Action.MANAGE, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.BUSINESS, Action.READ, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.MEMBERS, Action.MANAGE, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.MEMBERS, Action.READ, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.MEMBERS, Action.INVITE, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.UNIT_LIFECYCLE, Action.MANAGE, NEVER_END), conn)
        await MembershipRepository.add(person_id, business_id, conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.CAPABILITIES, Action.READ, NEVER_END), conn)
        await CapabilitiesRepository.add(person_id, business_id, CapabilityInput(Resource.CAPABILITIES, Action.MANAGE, NEVER_END), conn)
        logger.info("business.created", extra={"actor_id": str(person_id), "business_id": str(business_id), "request": model_context(request)})
        return business_id
        
    @staticmethod
    async def delete(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await BusinessValidator.validate_manage_business_capability(person_id, business_id, conn)
        r = await BusinessRepository.delete(business_id, conn)
        if not r:
            raise BusinessNotFoundError
        logger.info("business.deleted", extra={"actor_id": str(person_id), "business_id": str(business_id)})
    @staticmethod
    async def get(person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> BusinessOutput | None:
        await BusinessValidator.validate_read_business_capability(person_id, business_id, conn)
        business = await BusinessRepository.get(business_id, conn)
        return business
    @staticmethod
    async def update(person_id:UUID, business_id:UUID, request:BusinessUpdateRequest, conn:AsyncConnection[DictRow]) -> None:
        await BusinessValidator.validate_manage_business_capability(person_id, business_id, conn)
        r = await BusinessRepository.update(business_id, RequestTranslator.update_request_to_business(request), conn)
        if r == 0:
            raise BusinessNotFoundError
        logger.info("business.updated", extra={"actor_id": str(person_id), "business_id": str(business_id), "request": model_context(request)})
