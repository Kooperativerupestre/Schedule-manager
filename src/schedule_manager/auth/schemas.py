from uuid import UUID

from pydantic import BaseModel, EmailStr


class AuthenticationCreate(BaseModel):
    user_id: UUID
    email: EmailStr
    password: str


class AuthenticationLogin(BaseModel):
    email: EmailStr
    password: str
