from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class User:
    id: UUID
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    @classmethod
    def create(cls, email: str, name: str) -> "User":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            email=email,
            name=name,
            created_at=now,
            updated_at=None,
            is_active=True
        )

    def update_name(self, name: str) -> None:
        self.name = name
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
