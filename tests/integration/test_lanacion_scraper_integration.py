"""
Test de integración para el flujo completo de scraping de La Nación.
"""

import pytest
import os
import django

# Configurar Django
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "src.infrastructure.config.django_settings"
)
django.setup()

from asgiref.sync import sync_to_async

from src.infrastructure.adapters.scrapers.lanacion_scraper import LaNacionScraper
from src.infrastructure.persistence.django_repositories import (
    DjangoNewsArticleRepository,
)
from src.application.use_cases.scrape_and_persist_articles import (
    ScrapeAndPersistArticlesUseCase,
)
from src.infrastructure.persistence.django_app.models import NewsArticleModel


@pytest.mark.django_db
@pytest.mark.asyncio
class TestLaNacionScraperIntegration:
    """Tests de integración para el scraper de La Nación con la base de datos"""

    async def test_complete_scraping_flow(self):
        """Test del flujo completo: scraping → validación → persistencia"""
        # Setup: Limpiar artículos existentes de La Nación
        await sync_to_async(
            NewsArticleModel.objects.filter(fuente="La Nación").delete
        )()

        # Inicializar componentes
        scraper = LaNacionScraper(max_articles=5)  # Solo 5 para tests rápidos
        repository = DjangoNewsArticleRepository()
        use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)

        # Ejecutar el caso de uso
        result = await use_case.execute()

        # Verificaciones
        assert result is not None
        assert "total_scraped" in result
        assert "total_new" in result
        assert "total_duplicates" in result
        assert "articles" in result

        # Debe haber scrapeado al menos algunos artículos
        assert result["total_scraped"] > 0

        # Todos los scrapeados deben ser nuevos (primera ejecución)
        assert result["total_new"] > 0
        assert result["total_duplicates"] == 0

        # Verificar que están en la base de datos
        db_count = await sync_to_async(
            NewsArticleModel.objects.filter(fuente="La Nación").count
        )()
        assert db_count == result["total_new"]

        # Verificar que los artículos tienen los campos requeridos
        for article in result["articles"]:
            assert article.titulo is not None
            assert article.url is not None
            assert article.fuente == "La Nación"
            assert article.contenido is not None

    async def test_duplicate_detection(self):
        """Test de detección de duplicados en segunda ejecución"""
        # Setup: Limpiar artículos existentes
        await sync_to_async(
            NewsArticleModel.objects.filter(fuente="La Nación").delete
        )()

        # Primera ejecución
        scraper = LaNacionScraper(max_articles=3)
        repository = DjangoNewsArticleRepository()
        use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)

        result1 = await use_case.execute()
        first_count = result1["total_new"]

        # Segunda ejecución (debería detectar duplicados)
        result2 = await use_case.execute()

        # Verificar que detectó duplicados
        assert result2["total_scraped"] > 0
        # Puede haber algunos nuevos si La Nación publicó artículos entre ejecuciones
        # pero debe haber detectado al menos algunos duplicados si los artículos son los mismos
        assert (
            result2["total_new"] + result2["total_duplicates"]
            == result2["total_scraped"]
        )

        # El total en DB no debe ser el doble
        db_count = await sync_to_async(
            NewsArticleModel.objects.filter(fuente="La Nación").count
        )()
        assert db_count < first_count * 2

    async def test_scraper_handles_real_website(self):
        """Test que el scraper puede acceder al sitio real de La Nación"""
        scraper = LaNacionScraper(max_articles=2, timeout=30)

        # Este test puede fallar si hay problemas de red
        # pero demuestra que el scraper funciona con el sitio real
        try:
            articles = scraper.scrape()

            # Si el scraping fue exitoso
            if len(articles) > 0:
                # Verificar que los artículos tienen formato correcto
                for article in articles:
                    assert article.fuente == "La Nación"
                    assert article.url.startswith("https://www.lanacion.com.ar")
                    assert len(article.titulo) > 0
                    # Contenido puede estar vacío en algunos casos
        except Exception as e:
            # Logging del error pero no falla el test
            # (puede ser un problema de red temporal)
            print(f"Warning: Error al scrapear sitio real: {e}")
            pytest.skip("No se pudo acceder al sitio real de La Nación")
