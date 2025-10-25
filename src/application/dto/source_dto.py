from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CreateSourceDTO:
    nombre: str
    dominio: str
    pais: str


@dataclass
class UpdateSourceDTO:
    nombre: Optional[str] = None
    dominio: Optional[str] = None
    pais: Optional[str] = None


@dataclass
class SourceDTO:
    id: UUID
    nombre: str
    dominio: str
    pais: str
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime]
