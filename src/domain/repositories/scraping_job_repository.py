from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.scraping_job import ScrapingJob


class ScrapingJobRepository(ABC):

    @abstractmethod
    async def create(self, job: ScrapingJob) -> ScrapingJob:
        pass

    @abstractmethod
    async def get_by_id(self, job_id: UUID) -> Optional[ScrapingJob]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ScrapingJob]:
        pass

    @abstractmethod
    async def get_by_fuente(
        self, fuente: str, skip: int = 0, limit: int = 100
    ) -> List[ScrapingJob]:
        pass

    @abstractmethod
    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[ScrapingJob]:
        pass

    @abstractmethod
    async def update(self, job: ScrapingJob) -> ScrapingJob:
        pass

    @abstractmethod
    async def delete(self, job_id: UUID) -> bool:
        pass
