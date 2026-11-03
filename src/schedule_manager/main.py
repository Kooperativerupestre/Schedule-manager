from fastapi import FastAPI

from schedule_manager.business.memberships.router import (
    router as business_memberships_router,
)
from schedule_manager.business.router import router as business_router
from schedule_manager.user.router import router as user_router

app = FastAPI(title="Schedule Manager")

app.include_router(user_router)
app.include_router(business_router)
app.include_router(business_memberships_router)


@app.get("/")
def read_root():
    return {"message": "Schedule Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
