from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.enums import NewsSource


@dataclass
class CreateSourceDTO:
    source_type: NewsSource


@dataclass
class UpdateSourceDTO:
    activo: Optional[bool] = None


@dataclass
class SourceDTO:
    id: UUID
    source_type: NewsSource
    nombre: str
    dominio: str
    pais: str
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime]
