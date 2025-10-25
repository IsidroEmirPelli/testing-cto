# Ejemplos de Uso del Scraper Adapter

## 1. Uso Básico

### Scraping Simple

```python
from src.infrastructure.external_services import ScrapyAdapter

# Crear adapter
scraper = ScrapyAdapter()

# Scraping de una fuente
articles = scraper.scrape_sources(['clarin'])

print(f"Artículos extraídos: {len(articles)}")
for article in articles:
    print(f"- {article.titulo}")
    print(f"  Fuente: {article.fuente}")
    print(f"  URL: {article.url}")
```

### Múltiples Fuentes

```python
from src.infrastructure.external_services import ScrapyAdapter

scraper = ScrapyAdapter()

# Scraping de todas las fuentes argentinas
sources = ['clarin', 'lanacion', 'infobae', 'pagina12']
articles = scraper.scrape_sources(sources)

# Agrupar por fuente
from collections import defaultdict
by_source = defaultdict(list)

for article in articles:
    by_source[article.fuente].append(article)

for fuente, arts in by_source.items():
    print(f"{fuente}: {len(arts)} artículos")
```

## 2. Con Queue

### Usar MockQueue

```python
from src.infrastructure.external_services import ScrapyAdapter, MockQueue

# Crear queue y adapter
queue = MockQueue()
scraper = ScrapyAdapter(queue=queue)

# Scraping
articles = scraper.scrape_sources(['clarin', 'lanacion'])

# Procesar desde queue
print(f"Artículos en queue: {queue.size()}")

while not queue.is_empty():
    article = queue.dequeue()
    print(f"Procesando: {article.titulo}")
    # Guardar en BD, enviar a procesamiento, etc.
```

### Queue Personalizada

```python
from src.domain.ports.scraper_port import IScraperPort
from src.infrastructure.external_services import ScrapyAdapter

class RedisQueue:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def enqueue(self, article):
        import json
        data = {
            'titulo': article.titulo,
            'contenido': article.contenido,
            'fuente': article.fuente,
            'url': article.url,
        }
        self.redis.lpush('articles_queue', json.dumps(data))
    
    # ... otros métodos

# Usar con Redis
redis_queue = RedisQueue(redis_client)
scraper = ScrapyAdapter(queue=redis_queue)
articles = scraper.scrape_sources(['clarin'])
```

## 3. Con Casos de Uso

### Scraping Simple

```python
from src.application.use_cases import ScrapeNewsUseCase
from src.infrastructure.external_services import ScrapyAdapter

# Setup
scraper = ScrapyAdapter()
use_case = ScrapeNewsUseCase(scraper=scraper)

# Ejecutar
dtos = use_case.execute(['clarin', 'lanacion'])

# Los DTOs son serializables y listos para API
for dto in dtos:
    print(f"ID: {dto.id}")
    print(f"Título: {dto.titulo}")
    print(f"Fuente: {dto.fuente}")
```

### Con Persistencia

```python
from src.application.use_cases import ScrapeNewsUseCase, CreateArticleUseCase
from src.infrastructure.external_services import ScrapyAdapter
from src.infrastructure.persistence import NewsArticleRepositoryImpl

# Setup
scraper = ScrapyAdapter()
repository = NewsArticleRepositoryImpl()

scrape_use_case = ScrapeNewsUseCase(scraper=scraper)
create_use_case = CreateArticleUseCase(repository=repository)

# Scraping
dtos = scrape_use_case.execute(['clarin'])

# Persistir
for dto in dtos:
    try:
        saved = create_use_case.execute(dto)
        print(f"Guardado: {saved.titulo}")
    except Exception as e:
        print(f"Error guardando {dto.titulo}: {e}")
```

## 4. Scraping Programado

### Con APScheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler
from src.infrastructure.external_services import ScrapyAdapter
import logging

logger = logging.getLogger(__name__)

scraper = ScrapyAdapter()
sources = ['clarin', 'lanacion', 'infobae', 'pagina12']

def scheduled_scraping():
    logger.info("Iniciando scraping programado...")
    articles = scraper.scrape_sources(sources)
    logger.info(f"Scraping completado: {len(articles)} artículos")
    # Procesar artículos...

# Programar cada 6 horas
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scraping, 'interval', hours=6)
scheduler.start()
```

### Con Celery

```python
from celery import Celery
from src.infrastructure.external_services import ScrapyAdapter

app = Celery('news_scraper', broker='redis://localhost:6379/0')

@app.task
def scrape_news_task(sources):
    scraper = ScrapyAdapter()
    articles = scraper.scrape_sources(sources)
    
    # Guardar en BD
    for article in articles:
        # save_to_db(article)
        pass
    
    return len(articles)

# Programar
from celery.schedules import crontab

app.conf.beat_schedule = {
    'scrape-every-6-hours': {
        'task': 'scrape_news_task',
        'schedule': crontab(hour='*/6'),
        'args': (['clarin', 'lanacion', 'infobae', 'pagina12'],)
    },
}
```

## 5. Filtrado y Procesamiento

### Filtrar por Categoría

```python
from src.infrastructure.external_services import ScrapyAdapter

scraper = ScrapyAdapter()
articles = scraper.scrape_sources(['clarin', 'lanacion'])

# Filtrar política
politica = [a for a in articles if a.categoria and 'polít' in a.categoria.lower()]
print(f"Artículos de política: {len(politica)}")

# Filtrar economía
economia = [a for a in articles if a.categoria and 'econom' in a.categoria.lower()]
print(f"Artículos de economía: {len(economia)}")
```

### Procesamiento con NLP

```python
from src.infrastructure.external_services import ScrapyAdapter
import spacy

# Cargar modelo de español
nlp = spacy.load('es_core_news_sm')

scraper = ScrapyAdapter()
articles = scraper.scrape_sources(['clarin'])

for article in articles:
    # Procesar con spaCy
    doc = nlp(article.contenido[:1000])  # Primeros 1000 chars
    
    # Extraer entidades
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Extraer palabras clave
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    
    print(f"\nArtículo: {article.titulo}")
    print(f"Entidades: {entities[:5]}")
    print(f"Palabras clave: {keywords[:10]}")
```

### Análisis de Sentimiento

```python
from src.infrastructure.external_services import ScrapyAdapter
from textblob import TextBlob

scraper = ScrapyAdapter()
articles = scraper.scrape_sources(['clarin'])

for article in articles:
    # Analizar sentimiento
    blob = TextBlob(article.contenido)
    polarity = blob.sentiment.polarity
    
    sentiment = "Positivo" if polarity > 0.1 else "Negativo" if polarity < -0.1 else "Neutral"
    
    print(f"{article.titulo}")
    print(f"  Sentimiento: {sentiment} ({polarity:.2f})")
```

## 6. Manejo de Errores

### Error Handling Básico

```python
from src.infrastructure.external_services import ScrapyAdapter
import logging

logger = logging.getLogger(__name__)

scraper = ScrapyAdapter()

try:
    articles = scraper.scrape_sources(['clarin', 'lanacion'])
    
    if not articles:
        logger.warning("No se extrajeron artículos")
    else:
        logger.info(f"Éxito: {len(articles)} artículos")
        
except Exception as e:
    logger.error(f"Error en scraping: {e}", exc_info=True)
    # Notificar, reintentar, etc.
```

### Retry con Tenacity

```python
from tenacity import retry, stop_after_attempt, wait_fixed
from src.infrastructure.external_services import ScrapyAdapter
import logging

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(60))
def scrape_with_retry(sources):
    scraper = ScrapyAdapter()
    articles = scraper.scrape_sources(sources)
    
    if len(articles) < 10:
        raise Exception("Muy pocos artículos extraídos")
    
    return articles

try:
    articles = scrape_with_retry(['clarin'])
    logger.info(f"Scraping exitoso: {len(articles)} artículos")
except Exception as e:
    logger.error(f"Scraping falló después de 3 intentos: {e}")
```

## 7. Monitoreo y Métricas

### Estadísticas Básicas

```python
from src.infrastructure.external_services import ScrapyAdapter
from datetime import datetime, timezone
import statistics

scraper = ScrapyAdapter()
start_time = datetime.now(timezone.utc)

articles = scraper.scrape_sources(['clarin', 'lanacion', 'infobae', 'pagina12'])

end_time = datetime.now(timezone.utc)
duration = (end_time - start_time).total_seconds()

# Métricas
by_source = {}
content_lengths = []

for article in articles:
    by_source[article.fuente] = by_source.get(article.fuente, 0) + 1
    content_lengths.append(len(article.contenido))

print(f"\n=== MÉTRICAS DE SCRAPING ===")
print(f"Duración: {duration:.2f} segundos")
print(f"Total artículos: {len(articles)}")
print(f"Artículos/segundo: {len(articles)/duration:.2f}")

print(f"\nPor fuente:")
for source, count in by_source.items():
    print(f"  {source}: {count}")

if content_lengths:
    print(f"\nLongitud de contenido:")
    print(f"  Media: {statistics.mean(content_lengths):.0f} chars")
    print(f"  Mediana: {statistics.median(content_lengths):.0f} chars")
    print(f"  Min: {min(content_lengths)} chars")
    print(f"  Max: {max(content_lengths)} chars")
```

### Logging Avanzado

```python
from src.infrastructure.external_services import ScrapyAdapter
import logging
import sys

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

scraper = ScrapyAdapter()

logger.info("=== INICIO SCRAPING ===")
sources = ['clarin', 'lanacion']

for source in sources:
    logger.info(f"Procesando fuente: {source}")
    
    try:
        articles = scraper.scrape_sources([source])
        logger.info(f"  ✅ {source}: {len(articles)} artículos")
        
        for article in articles[:3]:  # Primeros 3
            logger.debug(f"    - {article.titulo[:50]}...")
            
    except Exception as e:
        logger.error(f"  ❌ {source}: Error - {e}")

logger.info("=== FIN SCRAPING ===")
```

## 8. Testing

### Test con Datos Mock

```python
from unittest.mock import Mock
from src.domain.entities import NewsArticle
from src.application.use_cases import ScrapeNewsUseCase
from datetime import datetime, timezone

# Mock scraper
mock_scraper = Mock()
mock_scraper.scrape_sources.return_value = [
    NewsArticle.create(
        titulo="Test Article",
        contenido="Content " * 50,
        fuente="Test Source",
        fecha_publicacion=datetime.now(timezone.utc),
        url="https://test.com/article"
    )
]

# Test use case
use_case = ScrapeNewsUseCase(scraper=mock_scraper)
dtos = use_case.execute(['test'])

assert len(dtos) == 1
assert dtos[0].titulo == "Test Article"
```

## 9. Deployment

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scraper_worker.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  scraper:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres
    command: python scraper_worker.py

  redis:
    image: redis:alpine
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: news_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

## 10. Mejores Prácticas

### 1. Logging Estructurado

```python
import structlog

logger = structlog.get_logger()

scraper = ScrapyAdapter()
articles = scraper.scrape_sources(['clarin'])

logger.info(
    "scraping_completed",
    source="clarin",
    articles_count=len(articles),
    duration=duration
)
```

### 2. Configuración Externalizada

```python
import os
from src.infrastructure.external_services import ScrapyAdapter

# Variables de entorno
SOURCES = os.getenv('SCRAPER_SOURCES', 'clarin,lanacion').split(',')
ENABLED = os.getenv('SCRAPER_ENABLED', 'true') == 'true'

if ENABLED:
    scraper = ScrapyAdapter()
    articles = scraper.scrape_sources(SOURCES)
```

### 3. Rate Limiting

```python
from ratelimit import limits, sleep_and_retry
from src.infrastructure.external_services import ScrapyAdapter

CALLS = 1
PERIOD = 60  # 1 call per minute

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def rate_limited_scrape(sources):
    scraper = ScrapyAdapter()
    return scraper.scrape_sources(sources)

articles = rate_limited_scrape(['clarin'])
```

### 4. Graceful Shutdown

```python
import signal
import sys
from src.infrastructure.external_services import ScrapyAdapter

scraper = ScrapyAdapter()
shutdown = False

def signal_handler(sig, frame):
    global shutdown
    print('Shutdown signal recibido, finalizando...')
    shutdown = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while not shutdown:
    try:
        articles = scraper.scrape_sources(['clarin'])
        # Procesar...
        break
    except Exception as e:
        if shutdown:
            break
        print(f"Error: {e}")

sys.exit(0)
```
