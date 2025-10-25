# Scrapy Adapter - News Scraper

Adapter para scraping de noticias de fuentes argentinas usando Scrapy y BeautifulSoup4.

## Arquitectura

Este módulo implementa el patrón de Adapter (Hexagonal Architecture) para integrar Scrapy como servicio externo.

### Componentes

```
scrapy_adapter/
├── __init__.py
├── scraper_adapter.py       # Adapter principal (implementa IScraperPort)
├── items.py                 # Definición de items de Scrapy
├── pipelines.py             # Pipelines de limpieza y validación
├── settings.py              # Configuración de Scrapy
└── spiders/                 # Spiders por fuente
    ├── __init__.py
    ├── base_spider.py       # Spider base con lógica común
    ├── clarin_spider.py     # Spider para Clarín
    ├── lanacion_spider.py   # Spider para La Nación
    ├── infobae_spider.py    # Spider para Infobae
    └── pagina12_spider.py   # Spider para Página/12
```

## Uso

### Básico

```python
from src.infrastructure.external_services import ScrapyAdapter, MockQueue

# Crear adapter
scraper = ScrapyAdapter()

# Scraping de fuentes
sources = ['clarin', 'lanacion', 'infobae', 'pagina12']
articles = scraper.scrape_sources(sources)

# Ver resultados
print(f"Total artículos: {len(articles)}")
for article in articles:
    print(f"- {article.titulo} ({article.fuente})")
```

### Con Queue Personalizada

```python
from src.infrastructure.external_services import ScrapyAdapter, MockQueue

queue = MockQueue()
scraper = ScrapyAdapter(queue=queue)

articles = scraper.scrape_sources(['clarin'])

# Procesar desde queue
while not queue.is_empty():
    article = queue.dequeue()
    # Guardar en BD, enviar a cola, etc.
```

### Integración con Caso de Uso

```python
from src.application.use_cases import ScrapeNewsUseCase
from src.infrastructure.external_services import ScrapyAdapter

scraper = ScrapyAdapter()
use_case = ScrapeNewsUseCase(scraper=scraper)

# Ejecutar scraping
dtos = use_case.execute(['clarin', 'lanacion'])
```

## Fuentes Soportadas

| Fuente | Identificador | Dominio | Artículos |
|--------|---------------|---------|-----------|
| Clarín | `clarin` | clarin.com | ~15 |
| La Nación | `lanacion` | lanacion.com.ar | ~15 |
| Infobae | `infobae` | infobae.com | ~15 |
| Página/12 | `pagina12` | pagina12.com.ar | ~15 |

## Añadir Nueva Fuente

1. **Crear spider** en `spiders/nueva_fuente_spider.py`:

```python
from .base_spider import BaseNewsSpider

class NuevaFuenteSpider(BaseNewsSpider):
    name = 'nuevafuente'
    allowed_domains = ['nuevafuente.com']
    start_urls = ['https://www.nuevafuente.com/']
    
    def parse(self, response):
        # Extraer links de artículos
        for link in response.css('article a::attr(href)').getall():
            yield scrapy.Request(link, callback=self.parse_article)
    
    def parse_article(self, response):
        titulo = response.css('h1::text').get()
        contenido = response.css('article p::text').getall()
        
        item = self.create_article_item(
            titulo=titulo,
            contenido=' '.join(contenido),
            fuente="Nueva Fuente",
            url=response.url
        )
        if item:
            yield item
```

2. **Registrar spider** en `spiders/__init__.py`:

```python
from .nueva_fuente_spider import NuevaFuenteSpider

__all__ = [..., "NuevaFuenteSpider"]
```

3. **Añadir al map** en `scraper_adapter.py`:

```python
SPIDER_MAP = {
    ...
    'nuevafuente': NuevaFuenteSpider,
}
```

## Pipelines

### TextCleaningPipeline

Limpia el contenido HTML y texto:
- Elimina tags HTML con BeautifulSoup4
- Normaliza espacios en blanco
- Elimina caracteres especiales
- Extrae solo texto relevante

### ValidationPipeline

Valida los items antes de procesarlos:
- Verifica campos requeridos
- Valida longitud mínima de contenido (100 chars)
- Descarta items inválidos

## Configuración

### settings.py

Configuraciones principales:

```python
ROBOTSTXT_OBEY = True            # Respetar robots.txt
DOWNLOAD_DELAY = 1               # 1 segundo entre requests
CONCURRENT_REQUESTS = 8          # Requests concurrentes
AUTOTHROTTLE_ENABLED = True      # Ajuste automático de velocidad
LOG_LEVEL = 'INFO'               # Nivel de logging
RETRY_TIMES = 3                  # Reintentos en errores
```

### Modificar Configuración

Para cambiar configuraciones globalmente, edita `settings.py`.

Para configuraciones por spider, usa `custom_settings`:

```python
class MiSpider(BaseNewsSpider):
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CLOSESPIDER_ITEMCOUNT': 20
    }
```

## Logging

El adapter usa logging de Python estándar:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logs automáticos:
# - Inicio de scraping
# - Artículos procesados
# - Errores en parseo
# - Finalización con estadísticas
```

## Manejo de Errores

### Errores de Red

- Retry automático (3 veces)
- Timeout de 30 segundos
- Errback en requests

### Errores de Parseo

- Try-catch en métodos parse
- Logging de errores
- Continúa con siguiente artículo

### Validación

- Pipeline valida campos requeridos
- Descarta items inválidos
- Logging de items descartados

## Testing

### Tests Unitarios

```bash
pytest tests/unit/test_scraper_adapter.py -v
pytest tests/unit/test_pipelines.py -v
```

### Test Manual

```bash
python test_scraper.py
```

Esto ejecuta un scraping real y muestra estadísticas.

## Mejores Prácticas

### 1. Respetar Sitios Web

- ✅ ROBOTSTXT_OBEY habilitado
- ✅ Download delay de 1 segundo
- ✅ User-Agent identificable
- ✅ Autothrottle para ajuste dinámico

### 2. Selectores CSS

Usar selectores robustos:

```python
# ❌ Malo
response.css('div div div p::text')

# ✅ Bueno
response.css('article.content p::text, div.article-body p::text')
```

### 3. Manejo de Campos Opcionales

```python
# Siempre verificar None
titulo = response.css('h1::text').get()
if not titulo:
    logger.warning(f"No se encontró título en {response.url}")
    return
```

### 4. Límite de Artículos

```python
# Control en spider
if self.articles_count >= self.max_articles:
    return

# O en settings
custom_settings = {
    'CLOSESPIDER_ITEMCOUNT': 15
}
```

## Performance

### Optimizaciones Implementadas

1. **Concurrent Requests**: 8 requests simultáneos
2. **Autothrottle**: Ajuste automático según respuesta del servidor
3. **HTTP Caching**: Deshabilitado (siempre fresh data)
4. **Connection Pooling**: Scrapy usa conexiones persistentes
5. **Download Timeout**: 30 segundos

### Métricas Típicas

- **Tiempo por fuente**: 30-60 segundos
- **Total 4 fuentes**: 2-4 minutos
- **Artículos/minuto**: ~10-15
- **Success rate**: >90%

## Troubleshooting

### Spider no encuentra artículos

1. Verificar selectores CSS en navegador
2. Revisar estructura HTML del sitio
3. Comprobar robots.txt
4. Verificar logs de Scrapy

### Errores 403/429

- Aumentar DOWNLOAD_DELAY
- Verificar User-Agent
- Reducir CONCURRENT_REQUESTS
- Revisar IP bloqueada

### Contenido vacío

- Verificar pipeline de limpieza
- Comprobar selectores de contenido
- Revisar validación de longitud mínima

### Artículos duplicados

- Usar dont_filter=False en Request
- Implementar deduplicación en adapter
- Verificar URLs únicas

## Extensiones Futuras

### 1. Categorización Automática

```python
from sklearn.feature_extraction.text import TfidfVectorizer

def classify_category(content):
    # ML model para clasificar
    pass
```

### 2. Extracción de Entidades

```python
import spacy

nlp = spacy.load('es_core_news_sm')
doc = nlp(article.contenido)
entities = [(ent.text, ent.label_) for ent in doc.ents]
```

### 3. Detección de Duplicados

```python
from difflib import SequenceMatcher

def is_duplicate(article1, article2):
    ratio = SequenceMatcher(None, article1.contenido, article2.contenido).ratio()
    return ratio > 0.9
```

### 4. Scraping Incremental

```python
def scrape_since(date):
    # Solo artículos desde fecha
    pass
```

## Licencia

Este módulo es parte del proyecto News Scraper y sigue la misma licencia.
