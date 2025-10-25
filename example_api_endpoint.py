"""
Ejemplo de endpoint REST API para el coordinador de scraping.

Este módulo muestra cómo exponer el coordinador mediante una API REST
usando Django REST Framework.

Para integrarlo en tu proyecto:
1. Copiar este código a src/presentation/api/views.py
2. Configurar las rutas en urls.py
3. Asegurarse de tener djangorestframework instalado
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import asyncio
import logging

from src.application.use_cases import ScrapeAllSourcesUseCase
from src.infrastructure.persistence.django_repositories import (
    DjangoSourceRepository,
    DjangoScrapingJobRepository,
    DjangoNewsArticleRepository,
)

logger = logging.getLogger(__name__)


# =============================================================================
# ENDPOINT 1: Ejecutar Scraping (POST)
# =============================================================================


@api_view(["POST"])
@permission_classes(
    [IsAuthenticated]
)  # Cambiar a AllowAny si no requiere autenticación
def execute_scraping(request):
    """
    Ejecuta el coordinador de scraping para todas las fuentes activas.

    POST /api/scraping/execute/

    Respuesta:
    {
        "success": true,
        "message": "Scraping ejecutado exitosamente",
        "data": {
            "total_sources": 3,
            "total_jobs_completed": 3,
            "total_jobs_failed": 0,
            "total_articles_scraped": 45,
            "total_articles_persisted": 38,
            "jobs_details": [...]
        }
    }
    """
    try:
        logger.info(f"Iniciando scraping via API - Usuario: {request.user}")

        # Crear repositorios
        source_repo = DjangoSourceRepository()
        job_repo = DjangoScrapingJobRepository()
        article_repo = DjangoNewsArticleRepository()

        # Crear caso de uso
        scrape_all = ScrapeAllSourcesUseCase(
            source_repository=source_repo,
            scraping_job_repository=job_repo,
            article_repository=article_repo,
        )

        # Ejecutar (async)
        result = asyncio.run(scrape_all.execute())

        logger.info(
            f"Scraping completado - Artículos: {result['total_articles_scraped']}"
        )

        return Response(
            {
                "success": True,
                "message": "Scraping ejecutado exitosamente",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error ejecutando scraping via API: {e}", exc_info=True)
        return Response(
            {"success": False, "message": "Error ejecutando scraping", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# =============================================================================
# ENDPOINT 2: Obtener Estado del Último Scraping (GET)
# =============================================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def get_last_scraping_status(request):
    """
    Obtiene el estado de los últimos jobs de scraping.

    GET /api/scraping/status/
    GET /api/scraping/status/?limit=10

    Respuesta:
    {
        "success": true,
        "data": {
            "jobs": [...],
            "summary": {
                "total_jobs": 3,
                "completed": 3,
                "failed": 0,
                "total_articles": 45
            }
        }
    }
    """
    try:
        limit = int(request.GET.get("limit", 10))

        job_repo = DjangoScrapingJobRepository()
        jobs = asyncio.run(job_repo.get_all(skip=0, limit=limit))

        # Construir respuesta
        jobs_data = []
        total_articles = 0
        completed_count = 0
        failed_count = 0

        for job in jobs:
            jobs_data.append(
                {
                    "id": str(job.id),
                    "fuente": job.fuente,
                    "status": job.status,
                    "total_articulos": job.total_articulos,
                    "fecha_inicio": job.fecha_inicio.isoformat(),
                    "fecha_fin": job.fecha_fin.isoformat() if job.fecha_fin else None,
                }
            )

            total_articles += job.total_articulos
            if job.status == "completed":
                completed_count += 1
            elif job.status == "failed":
                failed_count += 1

        return Response(
            {
                "success": True,
                "data": {
                    "jobs": jobs_data,
                    "summary": {
                        "total_jobs": len(jobs),
                        "completed": completed_count,
                        "failed": failed_count,
                        "total_articles": total_articles,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error obteniendo estado de scraping: {e}", exc_info=True)
        return Response(
            {"success": False, "message": "Error obteniendo estado", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# =============================================================================
# ENDPOINT 3: Obtener Estadísticas por Fuente (GET)
# =============================================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def get_source_statistics(request, source_name):
    """
    Obtiene estadísticas históricas de una fuente específica.

    GET /api/scraping/statistics/Clarín/
    GET /api/scraping/statistics/Clarín/?limit=20

    Respuesta:
    {
        "success": true,
        "data": {
            "source": "Clarín",
            "total_jobs": 15,
            "total_articles": 225,
            "avg_articles_per_job": 15.0,
            "success_rate": 100.0,
            "recent_jobs": [...]
        }
    }
    """
    try:
        limit = int(request.GET.get("limit", 10))

        job_repo = DjangoScrapingJobRepository()
        jobs = asyncio.run(job_repo.get_by_fuente(source_name, skip=0, limit=100))

        if not jobs:
            return Response(
                {
                    "success": False,
                    "message": f"No se encontraron jobs para la fuente: {source_name}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Calcular estadísticas
        total_jobs = len(jobs)
        total_articles = sum(job.total_articulos for job in jobs)
        completed_jobs = sum(1 for job in jobs if job.status == "completed")

        avg_articles = total_articles / total_jobs if total_jobs > 0 else 0
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0

        recent_jobs = [
            {
                "id": str(job.id),
                "status": job.status,
                "total_articulos": job.total_articulos,
                "fecha_inicio": job.fecha_inicio.isoformat(),
                "fecha_fin": job.fecha_fin.isoformat() if job.fecha_fin else None,
            }
            for job in jobs[:limit]
        ]

        return Response(
            {
                "success": True,
                "data": {
                    "source": source_name,
                    "total_jobs": total_jobs,
                    "total_articles": total_articles,
                    "avg_articles_per_job": round(avg_articles, 2),
                    "success_rate": round(success_rate, 2),
                    "recent_jobs": recent_jobs,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(
            f"Error obteniendo estadísticas de {source_name}: {e}", exc_info=True
        )
        return Response(
            {
                "success": False,
                "message": "Error obteniendo estadísticas",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# =============================================================================
# ENDPOINT 4: Health Check (GET)
# =============================================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def scraping_health_check(request):
    """
    Verifica el estado del sistema de scraping.

    GET /api/scraping/health/

    Respuesta:
    {
        "success": true,
        "data": {
            "status": "healthy",
            "active_sources": 3,
            "last_job_time": "2024-01-15T10:00:00Z",
            "system_ready": true
        }
    }
    """
    try:
        source_repo = DjangoSourceRepository()
        job_repo = DjangoScrapingJobRepository()

        # Verificar fuentes activas
        active_sources = asyncio.run(source_repo.get_active_sources())

        # Obtener último job
        recent_jobs = asyncio.run(job_repo.get_all(skip=0, limit=1))
        last_job = recent_jobs[0] if recent_jobs else None

        system_ready = len(active_sources) > 0

        return Response(
            {
                "success": True,
                "data": {
                    "status": "healthy" if system_ready else "warning",
                    "active_sources": len(active_sources),
                    "last_job_time": (
                        last_job.fecha_inicio.isoformat() if last_job else None
                    ),
                    "system_ready": system_ready,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error en health check: {e}", exc_info=True)
        return Response(
            {"success": False, "message": "Sistema no disponible", "error": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# =============================================================================
# CONFIGURACIÓN DE URLS
# =============================================================================

"""
Para integrar estos endpoints, agregar a urls.py:

from django.urls import path
from .api.views import (
    execute_scraping,
    get_last_scraping_status,
    get_source_statistics,
    scraping_health_check,
)

urlpatterns = [
    # Scraping API
    path('api/scraping/execute/', execute_scraping, name='execute-scraping'),
    path('api/scraping/status/', get_last_scraping_status, name='scraping-status'),
    path('api/scraping/statistics/<str:source_name>/', get_source_statistics, name='source-statistics'),
    path('api/scraping/health/', scraping_health_check, name='scraping-health'),
]
"""


# =============================================================================
# EJEMPLO DE CONSUMO CON CURL/HTTPIE
# =============================================================================

"""
# 1. Ejecutar scraping
curl -X POST http://localhost:8000/api/scraping/execute/ \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -H "Content-Type: application/json"

# 2. Ver estado de últimos jobs
curl http://localhost:8000/api/scraping/status/

# 3. Ver estadísticas de Clarín
curl http://localhost:8000/api/scraping/statistics/Clarín/

# 4. Health check
curl http://localhost:8000/api/scraping/health/
"""


# =============================================================================
# EJEMPLO DE CONSUMO CON PYTHON REQUESTS
# =============================================================================

"""
import requests

# 1. Ejecutar scraping
response = requests.post(
    'http://localhost:8000/api/scraping/execute/',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
result = response.json()
print(f"Artículos scrapeados: {result['data']['total_articles_scraped']}")

# 2. Ver estado
response = requests.get('http://localhost:8000/api/scraping/status/')
status_data = response.json()
print(f"Jobs completados: {status_data['data']['summary']['completed']}")

# 3. Estadísticas de fuente
response = requests.get('http://localhost:8000/api/scraping/statistics/Clarín/')
stats = response.json()
print(f"Promedio artículos: {stats['data']['avg_articles_per_job']}")
"""


# =============================================================================
# EJEMPLO DE CONSUMO CON JAVASCRIPT/FETCH
# =============================================================================

"""
// 1. Ejecutar scraping
fetch('http://localhost:8000/api/scraping/execute/', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => {
    console.log('Artículos scrapeados:', data.data.total_articles_scraped);
});

// 2. Ver estado
fetch('http://localhost:8000/api/scraping/status/')
.then(response => response.json())
.then(data => {
    console.log('Jobs:', data.data.jobs);
});

// 3. Estadísticas
fetch('http://localhost:8000/api/scraping/statistics/Clarín/')
.then(response => response.json())
.then(data => {
    console.log('Estadísticas:', data.data);
});
"""
