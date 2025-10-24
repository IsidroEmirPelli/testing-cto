from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CreateUserDTO:
    email: str
    name: str


@dataclass
class UpdateUserDTO:
    name: Optional[str] = None


@dataclass
class UserDTO:
    id: UUID
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
