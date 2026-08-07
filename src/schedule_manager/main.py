from fastapi import FastAPI
from schedule_manager.people.router import router as people_router
from schedule_manager.db.connection import open_pool, close_pool
from contextlib import asynccontextmanager
from schedule_manager.auth.router import router as auth_router
from schedule_manager.core.exceptions import global_exception_handler
from schedule_manager.business.holidays.router import router as business_holidays_router
from schedule_manager.business.router import router as business_router
from schedule_manager.capabilities.router import router as capabilities_router
from schedule_manager.units.router import router as units_router
from schedule_manager.workstations.workstation.router import router as workstations_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_pool()

    yield

    await close_pool()

app = FastAPI(lifespan=lifespan)


app.include_router(people_router)
app.include_router(auth_router)
app.include_router(business_holidays_router)
app.include_router(business_router)
app.include_router(capabilities_router)
app.include_router(units_router)
app.include_router(workstations_router)
app.add_exception_handler(Exception, global_exception_handler)
