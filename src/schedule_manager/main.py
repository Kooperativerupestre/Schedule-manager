from fastapi import FastAPI

from schedule_manager.auth.router import router as auth_router
from schedule_manager.business.memberships.router import (
    router as business_memberships_router,
)
from schedule_manager.business.router import router as business_router
from schedule_manager.core.exception_handlers import register_exception_handlers
from schedule_manager.unit.memberships.router import (
    router as unit_memberships_router,
)
from schedule_manager.unit.router import router as unit_router
from schedule_manager.user.router import router as user_router
from schedule_manager.workstation.router import router as workstation_router
from schedule_manager.workstation.workers.router import (
    router as workers_router,
)

app = FastAPI(title="Schedule Manager")
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(business_router)
app.include_router(business_memberships_router)
app.include_router(unit_router)
app.include_router(unit_memberships_router)
app.include_router(workstation_router)
app.include_router(workers_router)


@app.get("/")
def read_root():
    return {"message": "Schedule Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
