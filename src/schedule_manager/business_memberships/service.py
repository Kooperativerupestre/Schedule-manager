from schedule_manager.utils.namespace import namespace
from schedule_manager.business_memberships.schemas import EmailRequest
from schedule_manager.business_memberships.repository import MembershipRepository, MembershipInvitesRepository
from uuid import UUID
from schedule_manager.business_memberships.status import MembershipStatus
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from schedule_manager.business_memberships.errors import NotBusinessMembershipError, MembershipInviteNotFoundError
from schedule_manager.business_memberships.validator import MembershipValidator
from schedule_manager.capabilities.capabilities import Action, Scope
from schedule_manager.business_memberships.models import BusinessMembership, BusinessMembershipInvite
from schedule_manager.capabilities.repository import CapabilitiesRepository

@namespace
class MembershipService:
    @staticmethod
    async def add(person_id:UUID, target_person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.MANAGE, conn)
        try:
            await MembershipRepository.add(target_person_id, business_id, conn)
        except Exception:
            raise
    @staticmethod
    async def end(person_id:UUID, target_person_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.MANAGE, conn)
        r = await MembershipRepository.end(target_person_id, business_id, conn)
        
        if not r:
            raise NotBusinessMembershipError
    
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

@namespace
class MembershipInviteService:
    @staticmethod
    async def add(person_id:UUID, email:EmailRequest, business_id:UUID, conn:AsyncConnection[DictRow]) -> UUID:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.INVITE, conn)
        id = await MembershipInvitesRepository.add(business_id, email.email, conn)
        return id
    @staticmethod
    async def end(person_id:UUID, invite_id:UUID, business_id:UUID, conn:AsyncConnection[DictRow]) -> None:
        await MembershipValidator.validate_capability_membership(person_id, business_id, Action.MANAGE, conn)
        await CapabilitiesRepository.end_all_from_target(person_id, invite_id, Scope.BUSINESS, conn)
        r = await MembershipInvitesRepository.end(invite_id, conn)
        if not r:
            raise MembershipInviteNotFoundError
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
