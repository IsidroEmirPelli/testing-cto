import logging
from typing import Dict, List, Optional

from src.domain.entities.scraping_job import ScrapingJob
from src.domain.repositories.news_article_repository import NewsArticleRepository
from src.domain.repositories.scraping_job_repository import ScrapingJobRepository
from src.domain.repositories.source_repository import SourceRepository
from src.domain.ports.scraper_port import ScraperPort
from src.infrastructure.adapters.scrapers import (
    ClarinScraper,
    Pagina12Scraper,
    LaNacionScraper,
)

logger = logging.getLogger(__name__)


class ScrapeAllSourcesUseCase:
    """
    Caso de uso coordinador para ejecutar scraping de todas las fuentes activas.
    
    Este coordinador actúa como un "job manager" interno que:
    1. Consulta las fuentes activas del repositorio
    2. Ejecuta el scraper correspondiente para cada fuente
    3. Registra cada ejecución en la tabla ScrapingJob
    4. Persiste los artículos extraídos
    5. Genera estadísticas consolidadas del proceso
    
    El coordinador es extensible para integrarse con sistemas de programación
    como cron, APScheduler, Celery, etc.
    """

    def __init__(
        self,
        source_repository: SourceRepository,
        scraping_job_repository: ScrapingJobRepository,
        article_repository: NewsArticleRepository,
    ):
        self._source_repository = source_repository
        self._scraping_job_repository = scraping_job_repository
        self._article_repository = article_repository
        self._scraper_factory = {
            "Clarín": lambda: ClarinScraper(max_articles=15),
            "Página12": lambda: Pagina12Scraper(max_articles=15),
            "La Nación": lambda: LaNacionScraper(max_articles=15),
        }

    async def execute(self) -> Dict:
        """
        Ejecuta el scraping de todas las fuentes activas.
        
        Returns:
            Dict: Estadísticas consolidadas del proceso:
                - total_sources: Total de fuentes procesadas
                - total_jobs_completed: Jobs completados exitosamente
                - total_jobs_failed: Jobs fallidos
                - total_articles_scraped: Total de artículos scrapeados
                - total_articles_persisted: Total de artículos nuevos guardados
                - jobs_details: Lista de detalles por cada job ejecutado
        """
        logger.info("="*80)
        logger.info("INICIANDO COORDINADOR DE SCRAPING - SCRAPE ALL SOURCES")
        logger.info("="*80)
        
        try:
            # Fase 1: Obtener fuentes activas
            logger.info("Fase 1: Consultando fuentes activas")
            active_sources = await self._source_repository.get_active_sources()
            total_sources = len(active_sources)
            
            logger.info(f"Fuentes activas encontradas: {total_sources}")
            for source in active_sources:
                logger.info(f"  - {source.nombre} ({source.dominio})")
            
            if not active_sources:
                logger.warning("No hay fuentes activas para scrapear")
                return self._build_empty_response()
            
            # Fase 2: Ejecutar scraping para cada fuente
            logger.info("="*80)
            logger.info("Fase 2: Ejecutando scraping por fuente")
            logger.info("="*80)
            
            jobs_details = []
            total_jobs_completed = 0
            total_jobs_failed = 0
            total_articles_scraped = 0
            total_articles_persisted = 0
            
            for source in active_sources:
                job_detail = await self._process_source(source)
                jobs_details.append(job_detail)
                
                if job_detail['status'] == 'completed':
                    total_jobs_completed += 1
                    total_articles_scraped += job_detail['articles_scraped']
                    total_articles_persisted += job_detail['articles_persisted']
                else:
                    total_jobs_failed += 1
            
            # Fase 3: Resumen final
            logger.info("="*80)
            logger.info("RESUMEN FINAL DEL COORDINADOR DE SCRAPING")
            logger.info("="*80)
            logger.info(f"Total de fuentes procesadas: {total_sources}")
            logger.info(f"Jobs completados: {total_jobs_completed}")
            logger.info(f"Jobs fallidos: {total_jobs_failed}")
            logger.info(f"Total artículos scrapeados: {total_articles_scraped}")
            logger.info(f"Total artículos nuevos guardados: {total_articles_persisted}")
            logger.info("="*80)
            
            return {
                'total_sources': total_sources,
                'total_jobs_completed': total_jobs_completed,
                'total_jobs_failed': total_jobs_failed,
                'total_articles_scraped': total_articles_scraped,
                'total_articles_persisted': total_articles_persisted,
                'jobs_details': jobs_details,
            }
            
        except Exception as e:
            logger.error(f"Error crítico en coordinador de scraping: {e}", exc_info=True)
            raise

    async def _process_source(self, source) -> Dict:
        """
        Procesa una fuente individual: scrapea, persiste y registra el job.
        
        Args:
            source: Entidad Source a procesar
            
        Returns:
            Dict: Detalle del job ejecutado con estadísticas
        """
        source_name = source.nombre
        logger.info(f"\n{'='*80}")
        logger.info(f"Procesando fuente: {source_name}")
        logger.info(f"{'='*80}")
        
        # Crear registro de ScrapingJob
        scraping_job = ScrapingJob.create(fuente=source_name)
        scraping_job = await self._scraping_job_repository.create(scraping_job)
        logger.info(f"ScrapingJob creado con ID: {scraping_job.id}")
        
        try:
            # Obtener el scraper correspondiente
            scraper = self._get_scraper_for_source(source_name)
            
            if not scraper:
                logger.warning(f"No hay scraper disponible para: {source_name}")
                scraping_job.fail()
                await self._scraping_job_repository.update(scraping_job)
                return self._build_job_detail(scraping_job, 0, 0, "No scraper available")
            
            # Iniciar el job
            scraping_job.start()
            await self._scraping_job_repository.update(scraping_job)
            logger.info(f"ScrapingJob iniciado para {source_name}")
            
            # Ejecutar scraping
            logger.info(f"Ejecutando scraper para {source_name}...")
            article_dtos = scraper.scrape()
            articles_scraped = len(article_dtos)
            logger.info(f"Artículos scrapeados de {source_name}: {articles_scraped}")
            
            # Persistir artículos
            articles_persisted = await self._persist_articles(article_dtos)
            logger.info(f"Artículos nuevos guardados de {source_name}: {articles_persisted}")
            
            # Completar el job
            scraping_job.complete(total_articulos=articles_scraped)
            await self._scraping_job_repository.update(scraping_job)
            logger.info(f"ScrapingJob completado para {source_name}")
            
            return self._build_job_detail(
                scraping_job,
                articles_scraped,
                articles_persisted,
                None
            )
            
        except Exception as e:
            logger.error(f"Error procesando fuente {source_name}: {e}", exc_info=True)
            scraping_job.fail()
            await self._scraping_job_repository.update(scraping_job)
            
            return self._build_job_detail(
                scraping_job,
                0,
                0,
                str(e)
            )

    def _get_scraper_for_source(self, source_name: str) -> Optional[ScraperPort]:
        """
        Obtiene el scraper correspondiente para una fuente.
        
        Args:
            source_name: Nombre de la fuente
            
        Returns:
            Optional[ScraperPort]: Instancia del scraper o None si no existe
        """
        scraper_factory = self._scraper_factory.get(source_name)
        if scraper_factory:
            return scraper_factory()
        return None

    async def _persist_articles(self, article_dtos: List) -> int:
        """
        Persiste los artículos scrapeados evitando duplicados.
        
        Args:
            article_dtos: Lista de ArticleDTO scrapeados
            
        Returns:
            int: Cantidad de artículos nuevos persistidos
        """
        from src.domain.entities.news_article import NewsArticle
        
        new_articles_count = 0
        
        for dto in article_dtos:
            try:
                # Verificar si ya existe
                existing_article = await self._article_repository.get_by_url(dto.url)
                
                if existing_article:
                    logger.debug(f"Artículo duplicado (omitido): {dto.url}")
                    continue
                
                # Crear y persistir nuevo artículo
                article = NewsArticle.create(
                    titulo=dto.titulo,
                    contenido=dto.contenido or "",
                    fuente=dto.fuente,
                    fecha_publicacion=dto.fecha_publicacion,
                    url=dto.url,
                    categoria=None
                )
                
                await self._article_repository.create(article)
                new_articles_count += 1
                logger.debug(f"Artículo guardado: {article.titulo[:60]}...")
                
            except Exception as e:
                logger.error(f"Error persistiendo artículo {dto.url}: {e}")
                continue
        
        return new_articles_count

    def _build_job_detail(
        self,
        scraping_job: ScrapingJob,
        articles_scraped: int,
        articles_persisted: int,
        error: Optional[str]
    ) -> Dict:
        """
        Construye el detalle de un job ejecutado.
        
        Args:
            scraping_job: Entidad ScrapingJob
            articles_scraped: Cantidad de artículos scrapeados
            articles_persisted: Cantidad de artículos nuevos guardados
            error: Mensaje de error si hubo fallo
            
        Returns:
            Dict: Detalle estructurado del job
        """
        return {
            'job_id': str(scraping_job.id),
            'source': scraping_job.fuente,
            'status': scraping_job.status,
            'fecha_inicio': scraping_job.fecha_inicio.isoformat(),
            'fecha_fin': scraping_job.fecha_fin.isoformat() if scraping_job.fecha_fin else None,
            'articles_scraped': articles_scraped,
            'articles_persisted': articles_persisted,
            'duplicates': articles_scraped - articles_persisted,
            'error': error,
        }

    def _build_empty_response(self) -> Dict:
        """Construye una respuesta vacía cuando no hay fuentes activas."""
        return {
            'total_sources': 0,
            'total_jobs_completed': 0,
            'total_jobs_failed': 0,
            'total_articles_scraped': 0,
            'total_articles_persisted': 0,
            'jobs_details': [],
        }
