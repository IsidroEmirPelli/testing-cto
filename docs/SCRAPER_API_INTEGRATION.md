# Integración del Scraper con API REST

Este documento muestra cómo integrar el Scrapy Adapter con endpoints de API REST usando Django REST Framework.

## Endpoint de Scraping

### View Básico

```python
# src/presentation/api/views/scraping_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

from src.application.use_cases import ScrapeNewsUseCase
from src.infrastructure.external_services import ScrapyAdapter
from src.domain.repositories import NewsArticleRepository

logger = logging.getLogger(__name__)


@api_view(['POST'])
def trigger_scraping(request):
    """
    POST /api/scraping/trigger
    Body: {
        "sources": ["clarin", "lanacion"]
    }
    """
    sources = request.data.get('sources', ['clarin', 'lanacion', 'infobae', 'pagina12'])
    
    try:
        # Setup
        scraper = ScrapyAdapter()
        use_case = ScrapeNewsUseCase(scraper=scraper)
        
        # Ejecutar scraping
        logger.info(f"Iniciando scraping de fuentes: {sources}")
        dtos = use_case.execute(sources)
        
        # Respuesta
        return Response({
            'success': True,
            'message': f'Scraping completado exitosamente',
            'articles_count': len(dtos),
            'sources': sources
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en scraping: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def scraping_status(request):
    """
    GET /api/scraping/status
    """
    # Obtener estadísticas de la queue
    from src.infrastructure.external_services import MockQueue
    
    queue = MockQueue()  # En producción, usar singleton
    
    return Response({
        'queue_size': queue.size(),
        'is_empty': queue.is_empty()
    })
```

### URLs

```python
# src/presentation/api/urls.py
from django.urls import path
from src.presentation.api.views import scraping_views

urlpatterns = [
    # ... otras rutas
    path('api/scraping/trigger', scraping_views.trigger_scraping, name='trigger_scraping'),
    path('api/scraping/status', scraping_views.scraping_status, name='scraping_status'),
]
```

## Scraping Asíncrono

### Con Celery Task

```python
# src/infrastructure/tasks/scraping_tasks.py
from celery import shared_task
import logging

from src.application.use_cases import ScrapeNewsUseCase, CreateArticleUseCase
from src.infrastructure.external_services import ScrapyAdapter
from src.infrastructure.persistence import NewsArticleRepositoryImpl

logger = logging.getLogger(__name__)


@shared_task
def scrape_and_save_news(sources):
    """
    Tarea asíncrona para scraping y persistencia
    """
    try:
        # Setup
        scraper = ScrapyAdapter()
        repository = NewsArticleRepositoryImpl()
        
        scrape_use_case = ScrapeNewsUseCase(scraper=scraper)
        create_use_case = CreateArticleUseCase(repository=repository)
        
        # Scraping
        logger.info(f"Iniciando scraping de {sources}")
        dtos = scrape_use_case.execute(sources)
        
        # Persistir
        saved_count = 0
        for dto in dtos:
            try:
                create_use_case.execute(dto)
                saved_count += 1
            except Exception as e:
                logger.warning(f"Error guardando artículo {dto.url}: {e}")
        
        logger.info(f"Scraping completado: {saved_count}/{len(dtos)} artículos guardados")
        
        return {
            'success': True,
            'total': len(dtos),
            'saved': saved_count
        }
        
    except Exception as e:
        logger.error(f"Error en tarea de scraping: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }
```

### Endpoint Asíncrono

```python
# src/presentation/api/views/scraping_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from src.infrastructure.tasks.scraping_tasks import scrape_and_save_news


@api_view(['POST'])
def trigger_async_scraping(request):
    """
    POST /api/scraping/trigger-async
    Body: {
        "sources": ["clarin", "lanacion"]
    }
    """
    sources = request.data.get('sources', ['clarin', 'lanacion', 'infobae', 'pagina12'])
    
    # Encolar tarea
    task = scrape_and_save_news.delay(sources)
    
    return Response({
        'success': True,
        'message': 'Scraping encolado',
        'task_id': task.id,
        'sources': sources
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def task_status(request, task_id):
    """
    GET /api/scraping/task/{task_id}
    """
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    
    response = {
        'task_id': task_id,
        'status': task.state,
    }
    
    if task.state == 'SUCCESS':
        response['result'] = task.result
    elif task.state == 'FAILURE':
        response['error'] = str(task.info)
    
    return Response(response)
```

## Scraping Programado

### Django Management Command

```python
# src/infrastructure/management/commands/scrape_news.py
from django.core.management.base import BaseCommand
import logging

from src.application.use_cases import ScrapeNewsUseCase
from src.infrastructure.external_services import ScrapyAdapter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ejecuta scraping de noticias argentinas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sources',
            type=str,
            default='clarin,lanacion,infobae,pagina12',
            help='Fuentes separadas por coma'
        )
    
    def handle(self, *args, **options):
        sources = options['sources'].split(',')
        
        self.stdout.write(f"Iniciando scraping de: {sources}")
        
        try:
            scraper = ScrapyAdapter()
            use_case = ScrapeNewsUseCase(scraper=scraper)
            
            dtos = use_case.execute(sources)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Scraping completado: {len(dtos)} artículos')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )
            logger.error(f"Error en comando scrape_news: {e}", exc_info=True)
```

### Uso del Command

```bash
# Scraping de todas las fuentes
python manage.py scrape_news

# Scraping de fuentes específicas
python manage.py scrape_news --sources clarin,lanacion

# Con cron (cada 6 horas)
0 */6 * * * cd /app && python manage.py scrape_news >> /var/log/scraper.log 2>&1
```

## ViewSet Completo

### Serializers

```python
# src/presentation/api/serializers/scraping_serializers.py
from rest_framework import serializers


class TriggerScrapingSerializer(serializers.Serializer):
    sources = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['clarin', 'lanacion', 'infobae', 'pagina12']
    )
    
    def validate_sources(self, value):
        valid_sources = ['clarin', 'lanacion', 'infobae', 'pagina12']
        
        for source in value:
            if source not in valid_sources:
                raise serializers.ValidationError(
                    f"Fuente inválida: {source}. Fuentes válidas: {valid_sources}"
                )
        
        return value


class ScrapingResultSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    articles_count = serializers.IntegerField(required=False)
    sources = serializers.ListField(child=serializers.CharField(), required=False)
    error = serializers.CharField(required=False)
```

### ViewSet

```python
# src/presentation/api/views/scraping_viewset.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging

from src.application.use_cases import ScrapeNewsUseCase
from src.infrastructure.external_services import ScrapyAdapter
from src.presentation.api.serializers import TriggerScrapingSerializer

logger = logging.getLogger(__name__)


class ScrapingViewSet(viewsets.ViewSet):
    """
    ViewSet para operaciones de scraping
    """
    
    @action(detail=False, methods=['post'])
    def trigger(self, request):
        """
        POST /api/scraping/trigger/
        Inicia scraping de fuentes especificadas
        """
        serializer = TriggerScrapingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sources = serializer.validated_data['sources']
        
        try:
            scraper = ScrapyAdapter()
            use_case = ScrapeNewsUseCase(scraper=scraper)
            
            logger.info(f"Usuario {request.user} inició scraping de {sources}")
            dtos = use_case.execute(sources)
            
            return Response({
                'success': True,
                'message': 'Scraping completado exitosamente',
                'articles_count': len(dtos),
                'sources': sources
            })
            
        except Exception as e:
            logger.error(f"Error en scraping: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        GET /api/scraping/status/
        Obtiene estado de la queue
        """
        from src.infrastructure.external_services import MockQueue
        
        queue = MockQueue()
        
        return Response({
            'queue_size': queue.size(),
            'is_empty': queue.is_empty()
        })
    
    @action(detail=False, methods=['get'])
    def sources(self, request):
        """
        GET /api/scraping/sources/
        Lista fuentes disponibles
        """
        from src.infrastructure.external_services.scrapy_adapter import ScrapyAdapter
        
        sources = list(ScrapyAdapter.SPIDER_MAP.keys())
        
        return Response({
            'sources': sources,
            'count': len(sources)
        })
```

### Router

```python
# src/presentation/api/urls.py
from rest_framework.routers import DefaultRouter
from src.presentation.api.views.scraping_viewset import ScrapingViewSet

router = DefaultRouter()
router.register(r'scraping', ScrapingViewSet, basename='scraping')

urlpatterns = router.urls
```

## Webhooks

### Notificación Post-Scraping

```python
# src/infrastructure/external_services/webhooks.py
import requests
import logging

logger = logging.getLogger(__name__)


def notify_scraping_completed(articles_count, sources):
    """
    Envía notificación webhook al completar scraping
    """
    webhook_url = "https://hooks.example.com/scraping-completed"
    
    payload = {
        'event': 'scraping_completed',
        'articles_count': articles_count,
        'sources': sources,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Webhook enviado exitosamente")
    except Exception as e:
        logger.error(f"Error enviando webhook: {e}")


# Uso en scraping
dtos = use_case.execute(sources)
notify_scraping_completed(len(dtos), sources)
```

## Tests de Integración

### Test del Endpoint

```python
# tests/integration/test_scraping_api.py
import pytest
from unittest.mock import Mock, patch
from django.test import Client
from datetime import datetime, timezone

from src.domain.entities import NewsArticle


@pytest.mark.django_db
class TestScrapingAPI:
    
    def test_trigger_scraping_success(self, client):
        with patch('src.infrastructure.external_services.ScrapyAdapter') as mock_adapter:
            # Mock scraper
            mock_instance = Mock()
            mock_instance.scrape_sources.return_value = [
                NewsArticle.create(
                    titulo="Test",
                    contenido="Content " * 50,
                    fuente="Test Source",
                    fecha_publicacion=datetime.now(timezone.utc),
                    url="https://test.com"
                )
            ]
            mock_adapter.return_value = mock_instance
            
            # Request
            response = client.post('/api/scraping/trigger', {
                'sources': ['clarin']
            }, content_type='application/json')
            
            # Assert
            assert response.status_code == 200
            assert response.json()['success'] is True
            assert response.json()['articles_count'] == 1
    
    def test_trigger_scraping_invalid_source(self, client):
        response = client.post('/api/scraping/trigger', {
            'sources': ['invalid_source']
        }, content_type='application/json')
        
        assert response.status_code == 400
```

## Ejemplo de Cliente

### Python Client

```python
import requests


class NewsScraperClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
    
    def trigger_scraping(self, sources):
        """Inicia scraping de fuentes"""
        url = f"{self.base_url}/api/scraping/trigger"
        
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        response = requests.post(
            url,
            json={'sources': sources},
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_status(self):
        """Obtiene estado de la queue"""
        url = f"{self.base_url}/api/scraping/status"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


# Uso
client = NewsScraperClient('http://localhost:8000')
result = client.trigger_scraping(['clarin', 'lanacion'])
print(f"Artículos extraídos: {result['articles_count']}")
```

### JavaScript Client

```javascript
class NewsScraperClient {
    constructor(baseURL, apiKey = null) {
        this.baseURL = baseURL;
        this.apiKey = apiKey;
    }
    
    async triggerScraping(sources) {
        const url = `${this.baseURL}/api/scraping/trigger`;
        
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.apiKey) {
            headers['Authorization'] = `Bearer ${this.apiKey}`;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify({ sources })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getStatus() {
        const url = `${this.baseURL}/api/scraping/status`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Uso
const client = new NewsScraperClient('http://localhost:8000');

client.triggerScraping(['clarin', 'lanacion'])
    .then(result => {
        console.log(`Artículos extraídos: ${result.articles_count}`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

## Seguridad

### Autenticación con Token

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class ScrapingViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    # ... métodos
```

### Rate Limiting

```python
from rest_framework.throttling import UserRateThrottle


class ScrapingRateThrottle(UserRateThrottle):
    rate = '5/hour'  # 5 requests por hora


class ScrapingViewSet(viewsets.ViewSet):
    throttle_classes = [ScrapingRateThrottle]
    
    # ... métodos
```

## Monitoring

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram
import time

scraping_requests = Counter('scraping_requests_total', 'Total scraping requests')
scraping_duration = Histogram('scraping_duration_seconds', 'Scraping duration')
scraping_articles = Counter('scraping_articles_total', 'Total articles scraped')


@scraping_duration.time()
def execute_scraping(sources):
    scraping_requests.inc()
    
    scraper = ScrapyAdapter()
    use_case = ScrapeNewsUseCase(scraper=scraper)
    
    dtos = use_case.execute(sources)
    
    scraping_articles.inc(len(dtos))
    
    return dtos
```

## Conclusión

Esta integración permite:
- ✅ Endpoints REST para scraping on-demand
- ✅ Scraping asíncrono con Celery
- ✅ Commands de Django para cron jobs
- ✅ ViewSets completos con validación
- ✅ Webhooks para notificaciones
- ✅ Tests de integración
- ✅ Clientes en Python y JavaScript
- ✅ Seguridad con autenticación y rate limiting
- ✅ Monitoring con Prometheus
