from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.news_article import NewsArticle


class NewsArticleRepository(ABC):

    @abstractmethod
    async def create(self, article: NewsArticle) -> NewsArticle:
        pass

    @abstractmethod
    async def get_by_id(self, article_id: UUID) -> Optional[NewsArticle]:
        pass

    @abstractmethod
    async def get_by_url(self, url: str) -> Optional[NewsArticle]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[NewsArticle]:
        pass

    @abstractmethod
    async def get_by_fuente(
        self, fuente: str, skip: int = 0, limit: int = 100
    ) -> List[NewsArticle]:
        pass

    @abstractmethod
    async def get_by_categoria(
        self, categoria: str, skip: int = 0, limit: int = 100
    ) -> List[NewsArticle]:
        pass

    @abstractmethod
    async def update(self, article: NewsArticle) -> NewsArticle:
        pass

    @abstractmethod
    async def delete(self, article_id: UUID) -> bool:
        pass
