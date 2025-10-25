from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CreateScrapingJobDTO:
    fuente: str


@dataclass
class ScrapingJobDTO:
    id: UUID
    fuente: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    status: str
    total_articulos: int
    created_at: datetime
    updated_at: Optional[datetime]
