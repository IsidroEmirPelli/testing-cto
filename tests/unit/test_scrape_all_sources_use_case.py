import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from src.application.use_cases.scrape_all_sources import ScrapeAllSourcesUseCase
from src.domain.entities.source import Source
from src.domain.entities.scraping_job import ScrapingJob
from src.domain.entities.news_article import NewsArticle
from src.domain.dto.article_dto import ArticleDTO


class TestScrapeAllSourcesUseCase:
    """Tests para el caso de uso ScrapeAllSourcesUseCase."""

    @pytest.fixture
    def mock_source_repository(self):
        """Mock del repositorio de fuentes."""
        mock = AsyncMock()
        return mock

    @pytest.fixture
    def mock_scraping_job_repository(self):
        """Mock del repositorio de scraping jobs."""
        mock = AsyncMock()
        return mock

    @pytest.fixture
    def mock_article_repository(self):
        """Mock del repositorio de artículos."""
        mock = AsyncMock()
        return mock

    @pytest.fixture
    def use_case(
        self,
        mock_source_repository,
        mock_scraping_job_repository,
        mock_article_repository
    ):
        """Instancia del caso de uso con mocks."""
        return ScrapeAllSourcesUseCase(
            source_repository=mock_source_repository,
            scraping_job_repository=mock_scraping_job_repository,
            article_repository=mock_article_repository,
        )

    @pytest.fixture
    def sample_sources(self):
        """Fuentes de ejemplo."""
        return [
            Source.create(nombre="Clarín", dominio="clarin.com", pais="Argentina"),
            Source.create(nombre="Página12", dominio="pagina12.com.ar", pais="Argentina"),
            Source.create(nombre="La Nación", dominio="lanacion.com.ar", pais="Argentina"),
        ]

    @pytest.fixture
    def sample_article_dtos(self):
        """ArticleDTOs de ejemplo."""
        return [
            ArticleDTO(
                titulo="Artículo 1",
                url="https://ejemplo.com/articulo1",
                contenido="Contenido del artículo 1",
                fecha_publicacion=datetime.now(timezone.utc),
                fuente="Clarín"
            ),
            ArticleDTO(
                titulo="Artículo 2",
                url="https://ejemplo.com/articulo2",
                contenido="Contenido del artículo 2",
                fecha_publicacion=datetime.now(timezone.utc),
                fuente="Clarín"
            ),
        ]

    @pytest.mark.asyncio
    async def test_execute_with_no_active_sources(
        self,
        use_case,
        mock_source_repository
    ):
        """Debe retornar respuesta vacía cuando no hay fuentes activas."""
        mock_source_repository.get_active_sources.return_value = []

        result = await use_case.execute()

        assert result['total_sources'] == 0
        assert result['total_jobs_completed'] == 0
        assert result['total_jobs_failed'] == 0
        assert result['total_articles_scraped'] == 0
        assert result['total_articles_persisted'] == 0
        assert result['jobs_details'] == []

    @pytest.mark.asyncio
    async def test_execute_with_active_sources(
        self,
        use_case,
        mock_source_repository,
        mock_scraping_job_repository,
        mock_article_repository,
        sample_sources,
        sample_article_dtos
    ):
        """Debe procesar todas las fuentes activas correctamente."""
        # Configurar mocks
        mock_source_repository.get_active_sources.return_value = [sample_sources[0]]
        
        # Mock para crear y actualizar scraping jobs
        def create_job_side_effect(job):
            job.id = uuid4()
            return job
        mock_scraping_job_repository.create.side_effect = create_job_side_effect
        mock_scraping_job_repository.update.return_value = None
        
        # Mock para verificación de artículos duplicados
        mock_article_repository.get_by_url.return_value = None
        mock_article_repository.create.return_value = None

        # Mock del scraper
        with patch.object(use_case, '_get_scraper_for_source') as mock_get_scraper:
            mock_scraper = Mock()
            mock_scraper.scrape.return_value = sample_article_dtos
            mock_get_scraper.return_value = mock_scraper

            result = await use_case.execute()

            # Verificaciones
            assert result['total_sources'] == 1
            assert result['total_jobs_completed'] == 1
            assert result['total_jobs_failed'] == 0
            assert result['total_articles_scraped'] == 2
            assert result['total_articles_persisted'] == 2
            assert len(result['jobs_details']) == 1
            
            # Verificar que se llamaron los métodos correctos
            mock_source_repository.get_active_sources.assert_called_once()
            assert mock_scraping_job_repository.create.call_count == 1
            assert mock_scraping_job_repository.update.call_count >= 2  # start y complete

    @pytest.mark.asyncio
    async def test_execute_handles_scraper_failure(
        self,
        use_case,
        mock_source_repository,
        mock_scraping_job_repository,
        mock_article_repository,
        sample_sources
    ):
        """Debe manejar correctamente cuando un scraper falla."""
        mock_source_repository.get_active_sources.return_value = [sample_sources[0]]
        
        def create_job_side_effect(job):
            job.id = uuid4()
            return job
        mock_scraping_job_repository.create.side_effect = create_job_side_effect
        mock_scraping_job_repository.update.return_value = None

        # Mock del scraper que falla
        with patch.object(use_case, '_get_scraper_for_source') as mock_get_scraper:
            mock_scraper = Mock()
            mock_scraper.scrape.side_effect = Exception("Error de red")
            mock_get_scraper.return_value = mock_scraper

            result = await use_case.execute()

            # Verificaciones
            assert result['total_sources'] == 1
            assert result['total_jobs_completed'] == 0
            assert result['total_jobs_failed'] == 1
            assert len(result['jobs_details']) == 1
            assert result['jobs_details'][0]['status'] == 'failed'
            assert result['jobs_details'][0]['error'] == 'Error de red'

    @pytest.mark.asyncio
    async def test_execute_filters_duplicate_articles(
        self,
        use_case,
        mock_source_repository,
        mock_scraping_job_repository,
        mock_article_repository,
        sample_sources,
        sample_article_dtos
    ):
        """Debe filtrar artículos duplicados correctamente."""
        mock_source_repository.get_active_sources.return_value = [sample_sources[0]]
        
        def create_job_side_effect(job):
            job.id = uuid4()
            return job
        mock_scraping_job_repository.create.side_effect = create_job_side_effect
        mock_scraping_job_repository.update.return_value = None
        
        # Simular que el primer artículo ya existe
        existing_article = NewsArticle.create(
            titulo="Artículo existente",
            contenido="Contenido",
            fuente="Clarín",
            fecha_publicacion=datetime.now(timezone.utc),
            url=sample_article_dtos[0].url,
            categoria=None
        )
        
        def get_by_url_side_effect(url):
            if url == sample_article_dtos[0].url:
                return existing_article
            return None
        
        mock_article_repository.get_by_url.side_effect = get_by_url_side_effect
        mock_article_repository.create.return_value = None

        # Mock del scraper
        with patch.object(use_case, '_get_scraper_for_source') as mock_get_scraper:
            mock_scraper = Mock()
            mock_scraper.scrape.return_value = sample_article_dtos
            mock_get_scraper.return_value = mock_scraper

            result = await use_case.execute()

            # Verificaciones
            assert result['total_articles_scraped'] == 2
            assert result['total_articles_persisted'] == 1  # Solo uno nuevo
            assert result['jobs_details'][0]['duplicates'] == 1

    def test_get_scraper_for_source_clarin(self, use_case):
        """Debe retornar ClarinScraper para fuente Clarín."""
        scraper = use_case._get_scraper_for_source("Clarín")
        assert scraper is not None
        assert scraper.__class__.__name__ == "ClarinScraper"

    def test_get_scraper_for_source_pagina12(self, use_case):
        """Debe retornar Pagina12Scraper para fuente Página12."""
        scraper = use_case._get_scraper_for_source("Página12")
        assert scraper is not None
        assert scraper.__class__.__name__ == "Pagina12Scraper"

    def test_get_scraper_for_source_lanacion(self, use_case):
        """Debe retornar LaNacionScraper para fuente La Nación."""
        scraper = use_case._get_scraper_for_source("La Nación")
        assert scraper is not None
        assert scraper.__class__.__name__ == "LaNacionScraper"

    def test_get_scraper_for_source_unknown(self, use_case):
        """Debe retornar None para fuente desconocida."""
        scraper = use_case._get_scraper_for_source("Fuente Desconocida")
        assert scraper is None

    def test_build_job_detail(self, use_case):
        """Debe construir correctamente el detalle de un job."""
        job = ScrapingJob.create(fuente="Clarín")
        job.complete(total_articulos=10)
        
        detail = use_case._build_job_detail(
            scraping_job=job,
            articles_scraped=10,
            articles_persisted=8,
            error=None
        )
        
        assert detail['source'] == "Clarín"
        assert detail['status'] == "completed"
        assert detail['articles_scraped'] == 10
        assert detail['articles_persisted'] == 8
        assert detail['duplicates'] == 2
        assert detail['error'] is None

    def test_build_empty_response(self, use_case):
        """Debe construir correctamente la respuesta vacía."""
        response = use_case._build_empty_response()
        
        assert response['total_sources'] == 0
        assert response['total_jobs_completed'] == 0
        assert response['total_jobs_failed'] == 0
        assert response['total_articles_scraped'] == 0
        assert response['total_articles_persisted'] == 0
        assert response['jobs_details'] == []
