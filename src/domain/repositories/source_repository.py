from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.source import Source


class SourceRepository(ABC):

    @abstractmethod
    async def create(self, source: Source) -> Source:
        pass

    @abstractmethod
    async def get_by_id(self, source_id: UUID) -> Optional[Source]:
        pass

    @abstractmethod
    async def get_by_nombre(self, nombre: str) -> Optional[Source]:
        pass

    @abstractmethod
    async def get_by_dominio(self, dominio: str) -> Optional[Source]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Source]:
        pass

    @abstractmethod
    async def get_active_sources(self, skip: int = 0, limit: int = 100) -> List[Source]:
        pass

    @abstractmethod
    async def update(self, source: Source) -> Source:
        pass

    @abstractmethod
    async def delete(self, source_id: UUID) -> bool:
        pass
