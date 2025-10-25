from abc import ABC, abstractmethod
from typing import List, Protocol

from src.domain.dto.article_dto import ArticleDTO
from src.domain.entities.news_article import NewsArticle


class IScraperPort(ABC):
    """
    Puerto (interfaz) abstracta para scrapers (legacy).
    Esta interfaz se mantiene por compatibilidad con código existente.
    """

    @abstractmethod
    def scrape_sources(self, sources: List[str]) -> List[NewsArticle]:
        pass


class ScraperPort(Protocol):
    """
    Puerto (interfaz) basada en Protocol para scrapers.
    
    Esta interfaz define el contrato que debe cumplir cualquier implementación de scraper,
    independientemente de la fuente de noticias (Clarín, Página 12, La Nación, etc.).
    
    El uso de Protocol permite un tipado estructural (duck typing) más flexible,
    donde cualquier clase que implemente el método scrape() con la firma correcta
    será considerada compatible con este puerto, sin necesidad de heredar explícitamente.
    
    Example:
        >>> class ClarinScraper:
        ...     def scrape(self) -> list[ArticleDTO]:
        ...         # Implementación específica para Clarín
        ...         return [ArticleDTO(...), ...]
        >>> 
        >>> # ClarinScraper es automáticamente compatible con ScraperPort
        >>> scraper: ScraperPort = ClarinScraper()
    """

    def scrape(self) -> list[ArticleDTO]:
        """
        Extrae artículos de una fuente de noticias.
        
        Returns:
            list[ArticleDTO]: Lista de artículos extraídos en formato estandarizado
            
        Raises:
            Exception: Si ocurre un error durante el proceso de scraping
        """
        ...
