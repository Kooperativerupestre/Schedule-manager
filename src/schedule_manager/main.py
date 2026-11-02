from fastapi import FastAPI

from schedule_manager.user.router import router as user_router

app = FastAPI(title="Schedule Manager")

app.include_router(user_router)


@app.get("/")
def read_root():
    return {"message": "Schedule Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
