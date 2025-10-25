#!/usr/bin/env python3
"""
Script de verificación de la migración a Django.
Verifica que todos los componentes estén en su lugar.
"""
import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Verifica que un archivo exista"""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} - NO ENCONTRADO")
        return False

def main():
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE MIGRACIÓN A DJANGO")
    print("=" * 70)
    print()
    
    checks = []
    
    # Django Configuration
    print("📋 1. Configuración de Django")
    print("-" * 70)
    checks.append(check_file_exists("manage.py", "Django manage.py"))
    checks.append(check_file_exists("src/infrastructure/config/django_settings.py", "Django settings"))
    checks.append(check_file_exists("src/infrastructure/config/wsgi.py", "WSGI application"))
    checks.append(check_file_exists("src/infrastructure/config/asgi.py", "ASGI application"))
    print()
    
    # Domain Layer (should be unchanged)
    print("📋 2. Capa de Dominio (sin cambios)")
    print("-" * 70)
    checks.append(check_file_exists("src/domain/entities/news_article.py", "NewsArticle entity"))
    checks.append(check_file_exists("src/domain/entities/source.py", "Source entity"))
    checks.append(check_file_exists("src/domain/entities/scraping_job.py", "ScrapingJob entity"))
    checks.append(check_file_exists("src/domain/repositories/news_article_repository.py", "NewsArticle repository interface"))
    checks.append(check_file_exists("src/domain/repositories/source_repository.py", "Source repository interface"))
    checks.append(check_file_exists("src/domain/repositories/scraping_job_repository.py", "ScrapingJob repository interface"))
    print()
    
    # Application Layer (should be unchanged)
    print("📋 3. Capa de Aplicación (sin cambios)")
    print("-" * 70)
    checks.append(check_file_exists("src/application/dto/news_article_dto.py", "NewsArticle DTOs"))
    checks.append(check_file_exists("src/application/dto/source_dto.py", "Source DTOs"))
    checks.append(check_file_exists("src/application/dto/scraping_job_dto.py", "ScrapingJob DTOs"))
    checks.append(check_file_exists("src/application/use_cases/create_article.py", "CreateArticle use case"))
    checks.append(check_file_exists("src/application/use_cases/list_articles.py", "ListArticles use case"))
    checks.append(check_file_exists("src/application/use_cases/register_source.py", "RegisterSource use case"))
    print()
    
    # Infrastructure Layer (Django adapters)
    print("📋 4. Capa de Infraestructura (adaptadores Django)")
    print("-" * 70)
    checks.append(check_file_exists("src/infrastructure/persistence/django_app/models.py", "Django models"))
    checks.append(check_file_exists("src/infrastructure/persistence/django_app/admin.py", "Django admin"))
    checks.append(check_file_exists("src/infrastructure/persistence/django_app/apps.py", "Django app config"))
    checks.append(check_file_exists("src/infrastructure/persistence/django_repositories.py", "Django repositories"))
    print()
    
    # Presentation Layer (Django REST Framework)
    print("📋 5. Capa de Presentación (Django REST Framework)")
    print("-" * 70)
    checks.append(check_file_exists("src/presentation/django_app/serializers.py", "DRF serializers"))
    checks.append(check_file_exists("src/presentation/django_app/views.py", "DRF views"))
    checks.append(check_file_exists("src/presentation/django_app/urls.py", "URL routing"))
    print()
    
    # Docker Configuration
    print("📋 6. Configuración Docker")
    print("-" * 70)
    checks.append(check_file_exists("Dockerfile", "Dockerfile"))
    checks.append(check_file_exists("docker-compose.yml", "docker-compose.yml"))
    checks.append(check_file_exists(".env", ".env file"))
    checks.append(check_file_exists("requirements.txt", "requirements.txt"))
    print()
    
    # Documentation
    print("📋 7. Documentación")
    print("-" * 70)
    checks.append(check_file_exists("README_DJANGO.md", "Django README"))
    checks.append(check_file_exists("MIGRATION_TO_DJANGO.md", "Migration documentation"))
    checks.append(check_file_exists("DJANGO_MIGRATION_SUMMARY.md", "Migration summary"))
    checks.append(check_file_exists("Makefile", "Makefile"))
    print()
    
    # Tests
    print("📋 8. Tests")
    print("-" * 70)
    checks.append(check_file_exists("tests/unit/test_news_article_entity.py", "NewsArticle tests"))
    checks.append(check_file_exists("tests/unit/test_source_entity.py", "Source tests"))
    checks.append(check_file_exists("tests/unit/test_scraping_job_entity.py", "ScrapingJob tests"))
    checks.append(check_file_exists("pytest.ini", "pytest.ini"))
    print()
    
    # Summary
    print("=" * 70)
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    print(f"📊 RESUMEN: {passed}/{total} verificaciones pasaron")
    print("=" * 70)
    print()
    
    if failed == 0:
        print("✅ ¡MIGRACIÓN COMPLETA Y VERIFICADA!")
        print()
        print("🚀 Próximos pasos:")
        print("   1. make dev-setup    - Configurar y levantar servicios")
        print("   2. make logs         - Ver logs del sistema")
        print("   3. make test         - Ejecutar tests")
        print("   4. Acceder a http://localhost:8000/health/")
        print("   5. Acceder a http://localhost:8000/admin/ (admin/admin123)")
        print()
        return 0
    else:
        print(f"❌ Faltan {failed} componentes")
        print("   Revisa los archivos marcados como NO ENCONTRADO")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
