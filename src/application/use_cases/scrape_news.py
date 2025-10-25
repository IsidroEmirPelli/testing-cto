import logging
from typing import List
from src.domain.ports.scraper_port import IScraperPort
from src.application.dto.news_article_dto import NewsArticleDTO

logger = logging.getLogger(__name__)


class ScrapeNewsUseCase:
    def __init__(self, scraper: IScraperPort):
        self._scraper = scraper
    
    def execute(self, sources: List[str]) -> List[NewsArticleDTO]:
        logger.info(f"Ejecutando caso de uso ScrapeNews para fuentes: {sources}")
        
        try:
            articles = self._scraper.scrape_sources(sources)
            
            logger.info(f"Scraping completado. {len(articles)} artículos obtenidos")
            
            dtos = [
                NewsArticleDTO(
                    id=str(article.id),
                    titulo=article.titulo,
                    contenido=article.contenido,
                    fuente=article.fuente,
                    fecha_publicacion=article.fecha_publicacion.isoformat(),
                    url=article.url,
                    categoria=article.categoria,
                    procesado=article.procesado,
                    created_at=article.created_at.isoformat(),
                    updated_at=article.updated_at.isoformat() if article.updated_at else None
                )
                for article in articles
            ]
            
            return dtos
        
        except Exception as e:
            logger.error(f"Error en caso de uso ScrapeNews: {e}", exc_info=True)
            raise
