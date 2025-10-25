from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class NewsArticle:
    id: UUID
    titulo: str
    contenido: str
    fuente: str
    fecha_publicacion: datetime
    url: str
    categoria: Optional[str]
    procesado: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        titulo: str,
        contenido: str,
        fuente: str,
        fecha_publicacion: datetime,
        url: str,
        categoria: Optional[str] = None,
    ) -> "NewsArticle":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            titulo=titulo,
            contenido=contenido,
            fuente=fuente,
            fecha_publicacion=fecha_publicacion,
            url=url,
            categoria=categoria,
            procesado=False,
            created_at=now,
            updated_at=None,
        )

    def mark_as_processed(self) -> None:
        self.procesado = True
        self.updated_at = datetime.now(timezone.utc)

    def update_content(self, titulo: str, contenido: str) -> None:
        self.titulo = titulo
        self.contenido = contenido
        self.updated_at = datetime.now(timezone.utc)

    def update_category(self, categoria: str) -> None:
        self.categoria = categoria
        self.updated_at = datetime.now(timezone.utc)
