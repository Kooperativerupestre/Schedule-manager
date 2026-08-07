from fastapi import Request
from fastapi.responses import JSONResponse

from schedule_manager.capabilities.errors import *
from schedule_manager.people.errors import *
from schedule_manager.business.errors import *
from schedule_manager.core.errors import *
from schedule_manager.auth.errors import *
from schedule_manager.business_memberships.errors import *
from schedule_manager.units.errors import *
from schedule_manager.workstations.workstation.errors import *
from schedule_manager.workstations.schedules.errors import *
from schedule_manager.workstations.exceptions.errors import *
GLOBAL_ERROR_MAPPING = {
    ForbiddenError: (403, "Forbidden"),
    DuplicateCapabilityError: (409, "Capability already exists"),
    NullCapabilityError: (409, "Capability was not found"),
    TargetNotFoundError: (404, "Target id was not found"),
    PersonNotFoundError: (404, "Person id was not found"),
    CapabilityNameError: (404, "Capability name was not found"),

    CapabilityNotFoundError: (404, "Capability was not found"),
    InvalidCapabilitiesCombinationError: (400, "Invalid capability combination"),
    InvalidCredentialsError: (401, "Invalid credentials"),
    UniquePersonProviderViolatedError: (409, "Person already has this provider"),
    UniqueProviderIdentifierViolatedError: (409, "Identifier already in use"),
    PersonUpdateForbiddenError: (403, "Cannot update person"),
    BusinessNotFoundError: (404, "Business not found"),
    InviteAlreadyExistsError: (409, "Invite already exists"),
    CannotCreateBusinessMembershipInviteError: (400, "Cannot create membership invite"),
    CannotAddMembershipError: (400, "Cannot add membership"),
    NotBusinessMembershipError: (403, "Not a business membership"),
    MembershipInviteNotFoundError: (404, "Membership invite not found"),
    NullDataError: (400, "Null data provided"),
    OverlappingSchedulesError: (409, "Schedules overlap"),
    InvalidPhoneNumberError: (400, "Invalid phone number"),
    EmailAlreadyExistsError: (409, "Email already exists"),
    InvalidEmailError: (400, "Invalid email"),
    NotFoundError: (404, "Resource not found"),
    PhoneNumberAlreadyExistsError: (409, "Phone number already exists"),
    UnexpectedStateError: (500, "Unexpected state"),
    UnitNotFoundError: (404, "Unit not found"),
    WorkstationNotFoundError: (404, "Workstation not found"),
    WorkstationExceptionNotFoundError: (404, "Workstation exception not found"),
    ScheduleNotFoundError: (404, "Schedule not found"),
}
async def global_exception_handler(request: Request, exc: Exception):
    exc_type = type(exc)
    
    if exc_type in GLOBAL_ERROR_MAPPING:
        status_code, detail = GLOBAL_ERROR_MAPPING[exc_type]
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail}
        )
    
    raise exc