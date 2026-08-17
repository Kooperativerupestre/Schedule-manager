from pydantic import BaseModel
from uuid import UUID


class LocalLoginRequest(BaseModel):
    id: UUID
    password: str
