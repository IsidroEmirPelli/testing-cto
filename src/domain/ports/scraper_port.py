from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.news_article import NewsArticle


class IScraperPort(ABC):
    @abstractmethod
    def scrape_sources(self, sources: List[str]) -> List[NewsArticle]:
        pass
