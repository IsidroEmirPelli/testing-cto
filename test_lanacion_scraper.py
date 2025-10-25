#!/usr/bin/env python3
"""
Script de prueba para el scraper de La Nación.
Scrapea artículos y los persiste en la base de datos, evitando duplicados.
"""
import os
import sys
import logging
import asyncio
import django

# Configurar el entorno de Django
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "src.infrastructure.config.django_settings"
)
django.setup()

from src.infrastructure.adapters.scrapers.lanacion_scraper import LaNacionScraper
from src.infrastructure.persistence.django_repositories import (
    DjangoNewsArticleRepository,
)
from src.application.use_cases.scrape_and_persist_articles import (
    ScrapeAndPersistArticlesUseCase,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def main():
    """Función principal para ejecutar el test del scraper."""
    logger.info("=" * 80)
    logger.info("TEST DEL SCRAPER DE LA NACIÓN")
    logger.info("=" * 80)

    try:
        # Inicializar el scraper
        scraper = LaNacionScraper(max_articles=15)

        # Inicializar el repositorio
        article_repository = DjangoNewsArticleRepository()

        # Crear el caso de uso
        use_case = ScrapeAndPersistArticlesUseCase(
            scraper=scraper, article_repository=article_repository
        )

        # Ejecutar el caso de uso
        logger.info("Ejecutando scraping y persistencia...")
        result = await use_case.execute()

        # Mostrar resultados
        logger.info("\n" + "=" * 80)
        logger.info("RESULTADOS DEL TEST")
        logger.info("=" * 80)
        logger.info(f"Total de artículos scrapeados: {result['total_scraped']}")
        logger.info(f"Artículos nuevos insertados: {result['total_new']}")
        logger.info(f"Artículos duplicados (omitidos): {result['total_duplicates']}")
        logger.info("=" * 80)

        # Mostrar muestra de artículos insertados
        if result["articles"]:
            logger.info("\nMUESTRA DE ARTÍCULOS INSERTADOS:")
            logger.info("-" * 80)
            for i, article in enumerate(result["articles"][:5], 1):
                logger.info(f"\nArtículo #{i}:")
                logger.info(f"  ID: {article.id}")
                logger.info(f"  Título: {article.titulo}")
                logger.info(f"  Fuente: {article.fuente}")
                logger.info(f"  URL: {article.url}")
                logger.info(f"  Fecha: {article.fecha_publicacion}")
                logger.info(
                    f"  Contenido (primeros 150 chars): {article.contenido[:150]}..."
                )
                logger.info(
                    f"  Longitud contenido: {len(article.contenido)} caracteres"
                )

        # Verificar criterios de aceptación
        logger.info("\n" + "=" * 80)
        logger.info("VERIFICACIÓN DE CRITERIOS DE ACEPTACIÓN")
        logger.info("=" * 80)

        if result["total_new"] >= 10:
            logger.info(
                "✅ CRITERIO CUMPLIDO: Al menos 10 artículos nuevos en la base de datos"
            )
            return_code = 0
        else:
            logger.warning(
                f"⚠️  CRITERIO NO CUMPLIDO: Solo {result['total_new']} artículos nuevos (se requieren al menos 10)"
            )
            logger.info(
                "    Nota: Puede que haya duplicados. Intenta limpiar la base de datos o ejecutar de nuevo."
            )
            return_code = 1

        logger.info("=" * 80)
        logger.info("TEST COMPLETADO")
        logger.info("=" * 80)

        return return_code

    except Exception as e:
        logger.error(f"Error durante el test: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    return_code = asyncio.run(main())
    sys.exit(return_code)
