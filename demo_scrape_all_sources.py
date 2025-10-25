#!/usr/bin/env python3
"""
Script de demostración del coordinador de scraping ScrapeAllSourcesUseCase.

Este script muestra cómo usar el coordinador para ejecutar el scraping
de todas las fuentes activas y obtener estadísticas consolidadas.

Uso:
    python demo_scrape_all_sources.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.application.use_cases import ScrapeAllSourcesUseCase
from src.infrastructure.persistence.django_repositories import (
    DjangoSourceRepository,
    DjangoScrapingJobRepository,
    DjangoNewsArticleRepository,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraping_coordinator.log')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """
    Función principal que ejecuta el coordinador de scraping.
    """
    try:
        logger.info("="*80)
        logger.info("DEMO: Coordinador de Scraping - Scrape All Sources")
        logger.info("="*80)
        
        # Inicializar Django para ORM
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.config.django_settings')
        django.setup()
        
        # Crear instancias de los repositorios
        source_repository = DjangoSourceRepository()
        scraping_job_repository = DjangoScrapingJobRepository()
        article_repository = DjangoNewsArticleRepository()
        
        # Crear instancia del caso de uso
        scrape_all_use_case = ScrapeAllSourcesUseCase(
            source_repository=source_repository,
            scraping_job_repository=scraping_job_repository,
            article_repository=article_repository,
        )
        
        # Ejecutar el coordinador
        logger.info("Iniciando ejecución del coordinador...")
        result = await scrape_all_use_case.execute()
        
        # Mostrar resultados
        print("\n" + "="*80)
        print("RESULTADOS DEL COORDINADOR DE SCRAPING")
        print("="*80)
        print(f"Fuentes procesadas: {result['total_sources']}")
        print(f"Jobs completados exitosamente: {result['total_jobs_completed']}")
        print(f"Jobs fallidos: {result['total_jobs_failed']}")
        print(f"Total artículos scrapeados: {result['total_articles_scraped']}")
        print(f"Total artículos nuevos guardados: {result['total_articles_persisted']}")
        print(f"Total duplicados omitidos: {result['total_articles_scraped'] - result['total_articles_persisted']}")
        print("="*80)
        
        # Mostrar detalles por fuente
        if result['jobs_details']:
            print("\nDETALLE POR FUENTE:")
            print("-"*80)
            for job_detail in result['jobs_details']:
                print(f"\nFuente: {job_detail['source']}")
                print(f"  Estado: {job_detail['status']}")
                print(f"  Job ID: {job_detail['job_id']}")
                print(f"  Artículos scrapeados: {job_detail['articles_scraped']}")
                print(f"  Artículos guardados: {job_detail['articles_persisted']}")
                print(f"  Duplicados: {job_detail['duplicates']}")
                if job_detail['error']:
                    print(f"  Error: {job_detail['error']}")
            print("-"*80)
        
        logger.info("Ejecución del coordinador finalizada exitosamente")
        
    except Exception as e:
        logger.error(f"Error ejecutando el coordinador: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
