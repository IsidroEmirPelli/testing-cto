import logging
from typing import List

from src.domain.dto.article_dto import ArticleDTO
from src.domain.entities.news_article import NewsArticle
from src.domain.ports.scraper_port import ScraperPort
from src.domain.repositories.news_article_repository import NewsArticleRepository

logger = logging.getLogger(__name__)


class ScrapeAndPersistArticlesUseCase:
    """
    Caso de uso para scrapear artículos y persistirlos en la base de datos.

    Este caso de uso orquesta el proceso completo:
    1. Ejecuta el scraper para obtener artículos
    2. Verifica duplicados por URL
    3. Persiste los artículos nuevos en la base de datos
    4. Retorna estadísticas del proceso
    """

    def __init__(self, scraper: ScraperPort, article_repository: NewsArticleRepository):
        self._scraper = scraper
        self._article_repository = article_repository

    async def execute(self) -> dict:
        """
        Ejecuta el proceso completo de scraping y persistencia.

        Returns:
            dict: Diccionario con estadísticas del proceso:
                - total_scraped: Total de artículos scrapeados
                - total_new: Total de artículos nuevos insertados
                - total_duplicates: Total de artículos duplicados (ya existían)
                - articles: Lista de NewsArticle insertados
        """
        logger.info("Iniciando caso de uso ScrapeAndPersistArticles")

        try:
            # Fase 1: Scrapear artículos
            logger.info("Fase 1: Extrayendo artículos del scraper")
            article_dtos: List[ArticleDTO] = self._scraper.scrape()
            total_scraped = len(article_dtos)
            logger.info(f"Artículos scrapeados: {total_scraped}")

            if not article_dtos:
                logger.warning("No se obtuvieron artículos del scraper")
                return {
                    "total_scraped": 0,
                    "total_new": 0,
                    "total_duplicates": 0,
                    "articles": [],
                }

            # Fase 2: Filtrar duplicados y persistir
            logger.info("Fase 2: Verificando duplicados y persistiendo artículos")
            new_articles = []
            duplicate_count = 0

            for dto in article_dtos:
                try:
                    # Verificar si ya existe un artículo con esta URL
                    existing_article = await self._article_repository.get_by_url(
                        dto.url
                    )

                    if existing_article:
                        logger.info(f"Artículo duplicado (ya existe): {dto.url}")
                        duplicate_count += 1
                        continue

                    # Crear nueva entidad NewsArticle
                    article = NewsArticle.create(
                        titulo=dto.titulo,
                        contenido=dto.contenido or "",
                        fuente=dto.fuente,
                        fecha_publicacion=dto.fecha_publicacion,
                        url=dto.url,
                        categoria=None,  # La categoría podría extraerse del DTO si se implementa
                    )

                    # Persistir en la base de datos
                    saved_article = await self._article_repository.create(article)
                    new_articles.append(saved_article)
                    logger.info(
                        f"Artículo guardado exitosamente: {saved_article.titulo[:60]}..."
                    )

                except Exception as e:
                    logger.error(
                        f"Error procesando artículo {dto.url}: {e}", exc_info=True
                    )
                    continue

            total_new = len(new_articles)

            logger.info("=" * 80)
            logger.info("RESUMEN DEL SCRAPING Y PERSISTENCIA")
            logger.info("=" * 80)
            logger.info(f"Total scrapeados: {total_scraped}")
            logger.info(f"Artículos nuevos insertados: {total_new}")
            logger.info(f"Artículos duplicados (omitidos): {duplicate_count}")
            logger.info("=" * 80)

            return {
                "total_scraped": total_scraped,
                "total_new": total_new,
                "total_duplicates": duplicate_count,
                "articles": new_articles,
            }

        except Exception as e:
            logger.error(
                f"Error en caso de uso ScrapeAndPersistArticles: {e}", exc_info=True
            )
            raise
