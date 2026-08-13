from schedule_manager.utils.namespace import namespace
from schedule_manager.business.memberships.schemas import EmailRequest
from schedule_manager.business.memberships.repository import MembershipRepository, MembershipInvitesRepository
from uuid import UUID
from schedule_manager.business.memberships.status import MembershipStatus
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business.memberships.errors import NotBusinessMembershipError, MembershipInviteNotFoundError
from schedule_manager.business.memberships.validator import MembershipValidator
from schedule_manager.capabilities.capabilities import Action, Scope
from schedule_manager.business.memberships.models import BusinessMembership, BusinessMembershipInvite
from schedule_manager.capabilities.repository import CapabilitiesRepository
from schedule_manager.utils.service_logging import log_service_errors, model_context
import logging

logger = logging.getLogger(__name__)

@log_service_errors
@namespace
class MembershipService:
    @staticmethod
    async def add(person_id:UUID, target_person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.MANAGE, conn)
        try:
            await MembershipRepository.add(target_person_id, business_id, conn)
        except Exception:
            raise
        logger.info("membership.added", extra={"actor_id": str(person_id), "person_id": str(target_person_id), "business_id": str(business_id)})
    @staticmethod
    async def end(person_id:UUID, target_person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.MANAGE, conn)
        r = await MembershipRepository.end(target_person_id, business_id, conn)
        
        if not r:
            raise NotBusinessMembershipError
        logger.info("membership.ended", extra={"actor_id": str(person_id), "person_id": str(target_person_id), "business_id": str(business_id)})
    
    @staticmethod
    async def has(person_id:UUID, target_person_id:UUID, business_id:UUID, status:MembershipStatus | None, conn:AsyncConnection[DictRow]) -> bool:
        if person_id == target_person_id:
            return await MembershipRepository.has(target_person_id, business_id, conn, status)

        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.READ, conn)
        return await MembershipRepository.has(target_person_id, business_id, conn, status)
    @staticmethod
    async def get(person_id:UUID, target_person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow], status:MembershipStatus | None = None) -> list[BusinessMembership]:
        if person_id == target_person_id:
            return await MembershipRepository.get(target_person_id, business_id, conn, status)
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.READ, conn)
        return await MembershipRepository.get(target_person_id, business_id, conn, status)

@log_service_errors
@namespace
class MembershipInviteService:
    @staticmethod
    async def add(person_id:UUID, email:EmailRequest, business_id:UUID, conn:AsyncConnection[DictRow]) -> UUID:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.INVITE, conn)
        id = await MembershipInvitesRepository.add(business_id, email.email, conn)
        logger.info("membership_invite.created", extra={"actor_id": str(person_id), "business_id": str(business_id), "invite_id": str(id), "request": model_context(email)})
        return id
    @staticmethod
    async def end(person_id:UUID, invite_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.MANAGE, conn)
        await CapabilitiesRepository.end_all_from_target(person_id, invite_id, Scope.BUSINESS, conn)
        r = await MembershipInvitesRepository.end(invite_id, conn)
        if not r:
            raise MembershipInviteNotFoundError
        logger.info("membership_invite.ended", extra={"actor_id": str(person_id), "business_id": str(business_id), "invite_id": str(invite_id)})
    @staticmethod
    async def get(person_id:UUID, invite_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> BusinessMembershipInvite | None:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.READ, conn)
        return await MembershipInvitesRepository.get(invite_id, conn)
    @staticmethod
    async def has_ended(person_id:UUID, invite_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.READ, conn)
        return await MembershipInvitesRepository.has_ended(invite_id, conn)
    @staticmethod
    async def has_expired(person_id:UUID, invite_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> bool:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.READ, conn)
        return await MembershipInvitesRepository.has_expired(invite_id, conn)
