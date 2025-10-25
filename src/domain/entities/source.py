from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Source:
    id: UUID
    nombre: str
    dominio: str
    pais: str
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        nombre: str,
        dominio: str,
        pais: str,
    ) -> "Source":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            nombre=nombre,
            dominio=dominio,
            pais=pais,
            activo=True,
            created_at=now,
            updated_at=None,
        )

    def deactivate(self) -> None:
        self.activo = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        self.activo = True
        self.updated_at = datetime.now(timezone.utc)

    def update_info(self, nombre: str, dominio: str, pais: str) -> None:
        self.nombre = nombre
        self.dominio = dominio
        self.pais = pais
        self.updated_at = datetime.now(timezone.utc)
