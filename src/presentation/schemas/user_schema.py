from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool


class ErrorResponseSchema(BaseModel):
    detail: str
