from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class ScrapingJob:
    id: UUID
    fuente: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    status: str
    total_articulos: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def create(cls, fuente: str) -> "ScrapingJob":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            fuente=fuente,
            fecha_inicio=now,
            fecha_fin=None,
            status="pending",
            total_articulos=0,
            created_at=now,
            updated_at=None,
        )

    def start(self) -> None:
        self.status = "running"
        self.fecha_inicio = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def complete(self, total_articulos: int) -> None:
        self.status = "completed"
        self.fecha_fin = datetime.now(timezone.utc)
        self.total_articulos = total_articulos
        self.updated_at = datetime.now(timezone.utc)

    def fail(self) -> None:
        self.status = "failed"
        self.fecha_fin = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def increment_articles(self) -> None:
        self.total_articulos += 1
        self.updated_at = datetime.now(timezone.utc)
