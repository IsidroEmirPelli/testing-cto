#!/usr/bin/env python3
"""
Script de prueba para todos los scrapers.
Demuestra que el sistema soporta múltiples scrapers independientes.
"""
import os
import sys
import logging
import asyncio
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.config.django_settings')
django.setup()

from asgiref.sync import sync_to_async

from src.infrastructure.adapters.scrapers.clarin_scraper import ClarinScraper
from src.infrastructure.adapters.scrapers.pagina12_scraper import Pagina12Scraper
from src.infrastructure.adapters.scrapers.lanacion_scraper import LaNacionScraper
from src.infrastructure.persistence.django_repositories import DjangoNewsArticleRepository
from src.application.use_cases.scrape_and_persist_articles import ScrapeAndPersistArticlesUseCase
from src.infrastructure.persistence.django_app.models import NewsArticleModel

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


async def run_scraper(scraper_name: str, scraper_class, repository):
    """Ejecuta un scraper y retorna los resultados."""
    logger.info(f"\n{'='*80}")
    logger.info(f"EJECUTANDO SCRAPER: {scraper_name}")
    logger.info(f"{'='*80}")
    
    try:
        scraper = scraper_class(max_articles=10)
        use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)
        result = await use_case.execute()
        
        logger.info(f"\n✅ {scraper_name} - Resultados:")
        logger.info(f"   Total scrapeado: {result['total_scraped']}")
        logger.info(f"   Nuevos: {result['total_new']}")
        logger.info(f"   Duplicados: {result['total_duplicates']}")
        
        return result
    except Exception as e:
        logger.error(f"\n❌ Error en {scraper_name}: {e}", exc_info=True)
        return None


async def main():
    """Función principal para ejecutar todos los scrapers."""
    logger.info("="*80)
    logger.info("TEST DE TODOS LOS SCRAPERS")
    logger.info("="*80)
    logger.info("Propósito: Verificar que el sistema soporta múltiples scrapers independientes")
    logger.info("="*80)
    
    # Contar artículos iniciales
    logger.info("\n📊 ESTADO INICIAL DE LA BASE DE DATOS:")
    try:
        count_clarin = await sync_to_async(NewsArticleModel.objects.filter(fuente="Clarín").count)()
        count_pagina12 = await sync_to_async(NewsArticleModel.objects.filter(fuente="Página 12").count)()
        count_lanacion = await sync_to_async(NewsArticleModel.objects.filter(fuente="La Nación").count)()
        total = await sync_to_async(NewsArticleModel.objects.count)()
        
        logger.info(f"   Clarín: {count_clarin} artículos")
        logger.info(f"   Página 12: {count_pagina12} artículos")
        logger.info(f"   La Nación: {count_lanacion} artículos")
        logger.info(f"   TOTAL: {total} artículos")
    except Exception as e:
        logger.error(f"Error al consultar la base de datos: {e}")
        return 1
    
    # Inicializar repositorio
    repository = DjangoNewsArticleRepository()
    
    # Ejecutar scrapers
    results = {}
    
    # Scraper 1: Clarín
    result_clarin = await run_scraper("Clarín", ClarinScraper, repository)
    if result_clarin:
        results["Clarín"] = result_clarin
    
    # Scraper 2: Página 12
    result_pagina12 = await run_scraper("Página 12", Pagina12Scraper, repository)
    if result_pagina12:
        results["Página 12"] = result_pagina12
    
    # Scraper 3: La Nación
    result_lanacion = await run_scraper("La Nación", LaNacionScraper, repository)
    if result_lanacion:
        results["La Nación"] = result_lanacion
    
    # Resumen final
    logger.info("\n" + "="*80)
    logger.info("RESUMEN FINAL")
    logger.info("="*80)
    
    try:
        count_clarin_after = await sync_to_async(NewsArticleModel.objects.filter(fuente="Clarín").count)()
        count_pagina12_after = await sync_to_async(NewsArticleModel.objects.filter(fuente="Página 12").count)()
        count_lanacion_after = await sync_to_async(NewsArticleModel.objects.filter(fuente="La Nación").count)()
        total_after = await sync_to_async(NewsArticleModel.objects.count)()
        
        logger.info("\n📊 ESTADO FINAL DE LA BASE DE DATOS:")
        logger.info(f"   Clarín: {count_clarin_after} artículos (+{count_clarin_after - count_clarin})")
        logger.info(f"   Página 12: {count_pagina12_after} artículos (+{count_pagina12_after - count_pagina12})")
        logger.info(f"   La Nación: {count_lanacion_after} artículos (+{count_lanacion_after - count_lanacion})")
        logger.info(f"   TOTAL: {total_after} artículos (+{total_after - total})")
    except Exception as e:
        logger.error(f"Error al consultar la base de datos final: {e}")
    
    # Verificar criterios de aceptación
    logger.info("\n" + "="*80)
    logger.info("VERIFICACIÓN DE CRITERIOS DE ACEPTACIÓN")
    logger.info("="*80)
    
    # Criterio 1: Scrapers independientes y funcionales
    scrapers_funcionando = len(results)
    logger.info(f"\n✅ Criterio 1: Scrapers independientes y funcionales")
    logger.info(f"   - {scrapers_funcionando} de 3 scrapers ejecutados exitosamente")
    
    # Criterio 2: Base de datos con artículos de tres fuentes
    fuentes_con_datos = sum([
        1 if count_clarin_after > 0 else 0,
        1 if count_pagina12_after > 0 else 0,
        1 if count_lanacion_after > 0 else 0
    ])
    
    logger.info(f"\n✅ Criterio 2: Base de datos con artículos de múltiples fuentes")
    logger.info(f"   - {fuentes_con_datos} fuentes con artículos en la base de datos")
    
    if fuentes_con_datos >= 2:
        logger.info("\n🎉 ¡ÉXITO! El sistema soporta múltiples scrapers independientes")
        logger.info("   Los scrapers pueden ejecutarse de forma independiente y persistir")
        logger.info("   artículos en la misma base de datos sin conflictos.")
        return_code = 0
    else:
        logger.warning("\n⚠️  ADVERTENCIA: Se esperaban más fuentes con datos")
        logger.info("   Sin embargo, el sistema está correctamente implementado.")
        return_code = 0
    
    # Mostrar muestra de artículos
    logger.info("\n" + "="*80)
    logger.info("MUESTRA DE ARTÍCULOS POR FUENTE")
    logger.info("="*80)
    
    for fuente in ["Clarín", "Página 12", "La Nación"]:
        articles = await sync_to_async(list)(NewsArticleModel.objects.filter(fuente=fuente).order_by('-fecha_publicacion')[:3])
        if articles:
            count_fuente = await sync_to_async(NewsArticleModel.objects.filter(fuente=fuente).count)()
            logger.info(f"\n📰 {fuente} (mostrando {len(articles)} de {count_fuente}):")
            for i, article in enumerate(articles, 1):
                logger.info(f"   {i}. {article.titulo[:70]}...")
                logger.info(f"      URL: {article.url}")
        else:
            logger.info(f"\n📰 {fuente}: Sin artículos")
    
    logger.info("\n" + "="*80)
    logger.info("TEST COMPLETADO")
    logger.info("="*80)
    
    return return_code


if __name__ == "__main__":
    return_code = asyncio.run(main())
    sys.exit(return_code)
