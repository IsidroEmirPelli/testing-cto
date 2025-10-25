from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from src.domain.enums import NewsSource


@dataclass
class Source:
    id: UUID
    source_type: NewsSource
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @property
    def nombre(self) -> str:
        """Devuelve el nombre de la fuente desde el enum."""
        return self.source_type.nombre

    @property
    def dominio(self) -> str:
        """Devuelve el dominio de la fuente desde el enum."""
        return self.source_type.dominio

    @property
    def pais(self) -> str:
        """Devuelve el país de la fuente desde el enum."""
        return self.source_type.pais

    @classmethod
    def create(cls, source_type: NewsSource) -> "Source":
        """
        Crea una nueva fuente a partir de un NewsSource.

        Args:
            source_type: Tipo de fuente del enum NewsSource

        Returns:
            Nueva instancia de Source
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            source_type=source_type,
            activo=True,
            created_at=now,
            updated_at=None,
        )

    @classmethod
    def create_from_nombre(cls, nombre: str) -> "Source":
        """
        Crea una nueva fuente a partir de su nombre.

        Args:
            nombre: Nombre de la fuente

        Returns:
            Nueva instancia de Source

        Raises:
            ValueError: Si el nombre no corresponde a ninguna fuente
        """
        source_type = NewsSource.from_nombre(nombre)
        return cls.create(source_type)

    def deactivate(self) -> None:
        """Desactiva la fuente."""
        self.activo = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activa la fuente."""
        self.activo = True
        self.updated_at = datetime.now(timezone.utc)
