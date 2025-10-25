# Quick Start - News Scraper

Guía rápida para usar el scraper de noticias argentinas.

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

## Uso Rápido

### 1. Scraping Simple

```python
from src.infrastructure.external_services import ScrapyAdapter

scraper = ScrapyAdapter()
articles = scraper.scrape_sources(['clarin', 'lanacion'])

for article in articles:
    print(f"{article.titulo} - {article.fuente}")
```

### 2. Con Queue

```python
from src.infrastructure.external_services import ScrapyAdapter, MockQueue

queue = MockQueue()
scraper = ScrapyAdapter(queue=queue)

articles = scraper.scrape_sources(['clarin'])

print(f"Artículos en queue: {queue.size()}")

while not queue.is_empty():
    article = queue.dequeue()
    print(f"Procesando: {article.titulo}")
```

### 3. Con Caso de Uso

```python
from src.application.use_cases import ScrapeNewsUseCase
from src.infrastructure.external_services import ScrapyAdapter

scraper = ScrapyAdapter()
use_case = ScrapeNewsUseCase(scraper=scraper)

dtos = use_case.execute(['clarin', 'lanacion', 'infobae', 'pagina12'])

print(f"Total: {len(dtos)} artículos")
```

## Test Manual

Ejecuta el script de test incluido:

```bash
python test_scraper.py
```

Esto ejecutará el scraping de todas las fuentes y mostrará estadísticas.

## Fuentes Disponibles

| Identificador | Fuente | URL |
|--------------|--------|-----|
| `clarin` | Clarín | clarin.com |
| `lanacion` | La Nación | lanacion.com.ar |
| `infobae` | Infobae | infobae.com |
| `pagina12` | Página/12 | pagina12.com.ar |

## Estructura de NewsArticle

Cada artículo extraído tiene:

```python
article.id              # UUID
article.titulo          # str
article.contenido       # str (HTML limpiado)
article.fuente          # str
article.url             # str
article.fecha_publicacion  # datetime
article.categoria       # Optional[str]
article.procesado       # bool
article.created_at      # datetime
```

## Configuración

### Modificar límite de artículos

En cada spider, ajusta:

```python
class ClarinSpider(BaseNewsSpider):
    max_articles = 20  # Default: 15
```

### Cambiar delay entre requests

En `settings.py`:

```python
DOWNLOAD_DELAY = 2  # segundos (default: 1)
```

### Nivel de logging

En `settings.py`:

```python
LOG_LEVEL = 'DEBUG'  # INFO, WARNING, ERROR
```

## Arquitectura

```
IScraperPort (Domain)
    ↓
ScrapyAdapter (Infrastructure)
    ↓
Spiders (Scrapy)
    ↓
Pipelines (Cleaning + Validation)
    ↓
MockQueue (Storage)
```

## Características

✅ 4 fuentes argentinas principales  
✅ Limpieza automática de HTML con BeautifulSoup  
✅ Validación de datos  
✅ Manejo robusto de errores  
✅ Logging detallado  
✅ Queue para procesamiento asíncrono  
✅ Tests unitarios completos  
✅ Respetar robots.txt y rate limiting  

## Próximos Pasos

1. **Persistir artículos**: Integrar con repositorio para guardar en BD
2. **Scheduler**: Automatizar con Celery/Cron
3. **API REST**: Exponer endpoints para scraping on-demand
4. **Monitoring**: Dashboard con estadísticas

## Documentación Adicional

- `TICKET-3-SUMMARY.md` - Resumen completo de implementación
- `SCRAPER_USAGE_EXAMPLES.md` - Ejemplos de uso avanzados
- `SCRAPER_API_INTEGRATION.md` - Integración con API REST
- `src/infrastructure/external_services/scrapy_adapter/README.md` - Documentación técnica

## Tests

```bash
# Tests unitarios
pytest tests/unit/test_scraper_adapter.py -v
pytest tests/unit/test_pipelines.py -v
pytest tests/unit/test_scrape_news_use_case.py -v

# Todos los tests
pytest tests/unit/ -v
```

## Troubleshooting

### No se extraen artículos

1. Verificar conexión a internet
2. Verificar que los sitios estén accesibles
3. Revisar logs de Scrapy
4. Comprobar selectores CSS (sitios pueden cambiar)

### Errores de timeout

Aumentar timeout en `settings.py`:

```python
DOWNLOAD_TIMEOUT = 60  # segundos
```

### Contenido muy corto

El pipeline descarta artículos con menos de 100 caracteres. Para cambiar:

```python
# pipelines.py - ValidationPipeline
if len(item['contenido']) < 50:  # Reducir a 50
```

## Soporte

Para issues y preguntas, revisar:
1. Logs de Scrapy (nivel INFO)
2. Documentación técnica
3. Tests unitarios como ejemplos
