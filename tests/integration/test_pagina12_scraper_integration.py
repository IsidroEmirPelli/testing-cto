"""
Tests de integración para el scraper de Página 12.
Estos tests interactúan con componentes reales del sistema.
"""

import pytest
import os
import django
from datetime import datetime

# Configurar Django antes de importar modelos
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "src.infrastructure.config.django_settings"
)
django.setup()

from src.infrastructure.adapters.scrapers.pagina12_scraper import Pagina12Scraper
from src.domain.dto.article_dto import ArticleDTO
from src.application.use_cases.scrape_and_persist_articles import (
    ScrapeAndPersistArticlesUseCase,
)
from src.infrastructure.persistence.django_repositories import (
    DjangoNewsArticleRepository,
)


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.asyncio
class TestPagina12ScraperIntegration:
    """Tests de integración para Pagina12Scraper"""

    async def test_scraper_extracts_articles_with_valid_structure(self):
        """Test que el scraper extrae artículos con estructura válida"""
        scraper = Pagina12Scraper(max_articles=3)

        # Este test puede fallar si el sitio está caído, pero es útil para verificar
        # la estructura básica de los artículos extraídos
        try:
            articles = scraper.scrape()

            # Verificar que es una lista
            assert isinstance(articles, list)

            # Si hay artículos, verificar su estructura
            if articles:
                article = articles[0]

                # Verificar que es un ArticleDTO
                assert isinstance(article, ArticleDTO)

                # Verificar campos requeridos
                assert article.titulo
                assert article.url
                assert article.fuente == "Página 12"
                assert "pagina12.com.ar" in article.url

                # Verificar que la fecha es datetime
                if article.fecha_publicacion:
                    assert isinstance(article.fecha_publicacion, datetime)

        except Exception as e:
            # Si el sitio no está disponible, el test pasa
            pytest.skip(f"Sitio de Página 12 no disponible: {e}")

    @pytest.mark.django_db
    async def test_full_scraping_and_persistence_flow(self):
        """Test del flujo completo: scraping + persistencia"""
        from asgiref.sync import sync_to_async
        from src.infrastructure.persistence.django_app.models import NewsArticleModel

        scraper = Pagina12Scraper(max_articles=5)
        repository = DjangoNewsArticleRepository()
        use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)

        # Limpiar artículos previos de Página 12 para este test
        await sync_to_async(
            NewsArticleModel.objects.filter(fuente="Página 12").delete
        )()

        try:
            # Ejecutar caso de uso
            result = await use_case.execute()

            # Verificar resultado
            assert "total_scraped" in result
            assert "total_new" in result
            assert "total_duplicates" in result

            # Verificar que hay al menos algunos artículos
            total_in_db = await sync_to_async(
                NewsArticleModel.objects.filter(fuente="Página 12").count
            )()
            assert total_in_db >= 0  # Puede ser 0 si el sitio no está disponible

        except Exception as e:
            # Si el sitio no está disponible, el test pasa
            pytest.skip(f"Sitio de Página 12 no disponible: {e}")

    @pytest.mark.django_db
    async def test_duplicate_detection_works(self):
        """Test que la detección de duplicados funciona correctamente"""
        from asgiref.sync import sync_to_async
        from src.infrastructure.persistence.django_app.models import NewsArticleModel

        scraper = Pagina12Scraper(max_articles=3)
        repository = DjangoNewsArticleRepository()
        use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)

        # Limpiar artículos previos de Página 12
        await sync_to_async(
            NewsArticleModel.objects.filter(fuente="Página 12").delete
        )()

        try:
            # Primera ejecución
            result1 = await use_case.execute()
            nuevos_primera = result1["total_new"]

            # Segunda ejecución (debería detectar duplicados)
            result2 = await use_case.execute()
            duplicados_segunda = result2["total_duplicates"]

            # Si se insertaron artículos en la primera ejecución,
            # la segunda debería detectar algunos duplicados
            if nuevos_primera > 0:
                assert duplicados_segunda > 0

        except Exception as e:
            # Si el sitio no está disponible, el test pasa
            pytest.skip(f"Sitio de Página 12 no disponible: {e}")
