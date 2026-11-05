from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkerHireRequest(BaseModel):
    user_id: UUID


class WorkerCreateResponse(BaseModel):
    created: bool
    worker_id: UUID | None = None


class WorkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    workstation_id: UUID
