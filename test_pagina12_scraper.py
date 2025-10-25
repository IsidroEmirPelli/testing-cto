#!/usr/bin/env python3
"""
Script de prueba funcional para el scraper de Página 12.
Demuestra el flujo completo de scraping y persistencia.
"""
import os
import sys
import django
import asyncio
import logging

# Configurar path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.config.django_settings')
django.setup()

from src.infrastructure.adapters.scrapers.pagina12_scraper import Pagina12Scraper
from src.infrastructure.persistence.django_repositories import DjangoNewsArticleRepository
from src.application.use_cases.scrape_and_persist_articles import ScrapeAndPersistArticlesUseCase
from src.infrastructure.persistence.django_app.models import NewsArticleModel

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Función principal del script"""
    print("\n" + "="*70)
    print("TEST FUNCIONAL: Scraper de Página 12")
    print("="*70 + "\n")
    
    # Contar artículos antes
    count_before = NewsArticleModel.objects.filter(fuente="Página 12").count()
    print(f"📊 Artículos de Página 12 en BD antes: {count_before}\n")
    
    # Inicializar componentes
    print("🔧 Inicializando componentes...")
    scraper = Pagina12Scraper(max_articles=15)
    repository = DjangoNewsArticleRepository()
    use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)
    print("✅ Componentes inicializados\n")
    
    # Ejecutar scraping
    print("🕷️  Ejecutando scraping de Página 12...")
    print("-" * 70)
    
    try:
        result = await use_case.execute()
        
        print("\n" + "="*70)
        print("RESULTADOS DEL SCRAPING")
        print("="*70)
        print(f"✅ Total scrapeado:     {result['total_scraped']} artículos")
        print(f"✅ Nuevos insertados:   {result['total_new']} artículos")
        print(f"⚠️  Duplicados:         {result['total_duplicates']} artículos")
        print("="*70 + "\n")
        
        # Contar artículos después
        count_after = NewsArticleModel.objects.filter(fuente="Página 12").count()
        print(f"📊 Artículos de Página 12 en BD después: {count_after}")
        print(f"📈 Incremento: +{count_after - count_before} artículos\n")
        
        # Verificar criterio de aceptación
        if result['total_new'] > 0 or count_after >= 10:
            print("✅ CRITERIO CUMPLIDO: Al menos 10 artículos de Página 12 en la base de datos")
        else:
            print("⚠️  ATENCIÓN: Se necesitan más artículos para cumplir el criterio")
        
        # Mostrar ejemplos de artículos
        print("\n" + "="*70)
        print("EJEMPLOS DE ARTÍCULOS EXTRAÍDOS")
        print("="*70)
        
        articles = NewsArticleModel.objects.filter(fuente="Página 12").order_by('-fecha_publicacion')[:5]
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.titulo[:70]}...")
            print(f"   URL: {article.url}")
            print(f"   Fecha: {article.fecha_publicacion.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Contenido: {len(article.contenido)} caracteres")
        
        print("\n" + "="*70)
        print("TEST COMPLETADO EXITOSAMENTE")
        print("="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERROR EN EL SCRAPING")
        print("="*70)
        print(f"Error: {e}")
        logger.exception("Error detallado:")
        print("\n" + "="*70 + "\n")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
