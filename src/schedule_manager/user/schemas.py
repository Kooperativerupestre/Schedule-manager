from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserAdd(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
