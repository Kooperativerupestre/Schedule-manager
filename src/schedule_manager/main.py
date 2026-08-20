from contextlib import asynccontextmanager

from fastapi import FastAPI

from schedule_manager.auth.router import router as auth_router
from schedule_manager.business.holidays.router import (
    router as business_holidays_router,
)
from schedule_manager.business.memberships.router import (
    invites_router as membership_invites_router,
    router as memberships_router,
)
from schedule_manager.business.router import router as business_router
from schedule_manager.capabilities.router import router as capabilities_router
from schedule_manager.core.exceptions import global_exception_handler
from schedule_manager.db.connection import close_pool, open_pool, pool
from schedule_manager.infraestructure.redis.redis import lifespan as redis_lifespan
from schedule_manager.people.router import router as people_router
from schedule_manager.units.holidays.router import (
    router as units_holidays_router,
)
from schedule_manager.units.router import router as units_router
from schedule_manager.workstations.exceptions.router import (
    router as workstation_exceptions_router,
)
from schedule_manager.workstations.holidays.router import (
    router as workstation_holidays_router,
)
from schedule_manager.workstations.schedules.router import (
    router as workstation_schedules_router,
)
from schedule_manager.workstations.workstation.router import (
    router as workstations_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_pool(pool)
    async with redis_lifespan(app):
        yield
    await close_pool(pool)


app = FastAPI(lifespan=lifespan)


app.include_router(people_router)
app.include_router(auth_router)
app.include_router(business_holidays_router)
app.include_router(memberships_router)
app.include_router(membership_invites_router)
app.include_router(business_router)
app.include_router(capabilities_router)
app.include_router(units_router)
app.include_router(units_holidays_router)
app.include_router(workstations_router)
app.include_router(workstation_exceptions_router)
app.include_router(workstation_holidays_router)
app.include_router(workstation_schedules_router)
app.add_exception_handler(Exception, global_exception_handler)
