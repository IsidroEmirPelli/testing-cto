from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CreateNewsArticleDTO:
    titulo: str
    contenido: str
    fuente: str
    fecha_publicacion: datetime
    url: str
    categoria: Optional[str] = None


@dataclass
class UpdateNewsArticleDTO:
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    categoria: Optional[str] = None


@dataclass
class NewsArticleDTO:
    id: UUID
    titulo: str
    contenido: str
    fuente: str
    fecha_publicacion: datetime
    url: str
    categoria: Optional[str]
    procesado: bool
    created_at: datetime
    updated_at: Optional[datetime]
