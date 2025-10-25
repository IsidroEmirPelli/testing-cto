# Coordinador de Scraping - Documentación

## Descripción General

El **Coordinador de Scraping** (`ScrapeAllSourcesUseCase`) es un componente que ejecuta el scraping de todas las fuentes activas y registra los resultados en la tabla `ScrapingJob`. Actúa como un "job manager" interno que orquesta el proceso completo de extracción, persistencia y seguimiento de artículos de noticias.

## Arquitectura

### Componentes Principales

1. **ScrapeAllSourcesUseCase**: Caso de uso coordinador principal
2. **SourceRepository**: Gestiona las fuentes de noticias
3. **ScrapingJobRepository**: Gestiona los registros de trabajos de scraping
4. **NewsArticleRepository**: Gestiona los artículos extraídos
5. **Scrapers**: Implementaciones específicas por fuente (Clarín, Página12, La Nación)

### Diagrama de Flujo

```
┌─────────────────────────────────────────┐
│  ScrapeAllSourcesUseCase.execute()     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  1. Obtener fuentes activas             │
│     (SourceRepository)                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Para cada fuente activa:            │
│     ┌──────────────────────────────┐    │
│     │ 2.1 Crear ScrapingJob        │    │
│     │     (status: "pending")      │    │
│     └──────────────────────────────┘    │
│     ┌──────────────────────────────┐    │
│     │ 2.2 Iniciar Job              │    │
│     │     (status: "running")      │    │
│     └──────────────────────────────┘    │
│     ┌──────────────────────────────┐    │
│     │ 2.3 Ejecutar Scraper         │    │
│     │     (ClarinScraper, etc.)    │    │
│     └──────────────────────────────┘    │
│     ┌──────────────────────────────┐    │
│     │ 2.4 Persistir Artículos      │    │
│     │     (filtrar duplicados)     │    │
│     └──────────────────────────────┘    │
│     ┌──────────────────────────────┐    │
│     │ 2.5 Completar/Fallar Job     │    │
│     │     (status: "completed")    │    │
│     └──────────────────────────────┘    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Retornar estadísticas consolidadas  │
└─────────────────────────────────────────┘
```

## Uso del Coordinador

### Uso Básico

```python
import asyncio
from src.application.use_cases import ScrapeAllSourcesUseCase
from src.infrastructure.persistence.django_repositories import (
    DjangoSourceRepository,
    DjangoScrapingJobRepository,
    DjangoNewsArticleRepository,
)

async def run_scraping():
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
    
    # Ejecutar
    result = await scrape_all.execute()
    
    # Procesar resultados
    print(f"Fuentes procesadas: {result['total_sources']}")
    print(f"Artículos scrapeados: {result['total_articles_scraped']}")
    print(f"Artículos guardados: {result['total_articles_persisted']}")

# Ejecutar
asyncio.run(run_scraping())
```

### Uso con Demo Script

El proyecto incluye un script de demostración listo para usar:

```bash
python demo_scrape_all_sources.py
```

Este script:
- Configura logging detallado
- Inicializa Django ORM
- Ejecuta el coordinador
- Muestra estadísticas consolidadas y por fuente

## Estructura de Respuesta

El método `execute()` retorna un diccionario con la siguiente estructura:

```python
{
    'total_sources': int,              # Total de fuentes procesadas
    'total_jobs_completed': int,       # Jobs completados exitosamente
    'total_jobs_failed': int,          # Jobs que fallaron
    'total_articles_scraped': int,     # Total de artículos scrapeados
    'total_articles_persisted': int,   # Total de artículos nuevos guardados
    'jobs_details': [                  # Detalles por cada job
        {
            'job_id': str,             # UUID del job
            'source': str,             # Nombre de la fuente
            'status': str,             # Estado: completed/failed
            'fecha_inicio': str,       # ISO format
            'fecha_fin': str,          # ISO format
            'articles_scraped': int,   # Artículos scrapeados
            'articles_persisted': int, # Artículos nuevos guardados
            'duplicates': int,         # Artículos duplicados omitidos
            'error': str | None,       # Mensaje de error si falló
        },
        ...
    ]
}
```

## Gestión de Trabajos (ScrapingJob)

Cada ejecución del scraper para una fuente genera un registro `ScrapingJob` con:

- **id**: UUID único del job
- **fuente**: Nombre de la fuente (Clarín, Página12, La Nación)
- **fecha_inicio**: Timestamp de inicio
- **fecha_fin**: Timestamp de finalización
- **status**: Estado del job
  - `pending`: Creado pero no iniciado
  - `running`: En ejecución
  - `completed`: Completado exitosamente
  - `failed`: Falló con error
- **total_articulos**: Cantidad de artículos scrapeados
- **created_at**: Timestamp de creación del registro
- **updated_at**: Timestamp de última actualización

## Manejo de Duplicados

El coordinador implementa deduplicación automática:

1. Para cada artículo scrapeado, verifica si ya existe en la BD (por URL)
2. Si existe, lo omite y cuenta como duplicado
3. Si no existe, lo persiste en la BD
4. Las estadísticas incluyen tanto artículos scrapeados como nuevos guardados

## Logging Centralizado

El coordinador implementa logging detallado en múltiples niveles:

### Nivel INFO
- Inicio y fin del proceso general
- Fuentes activas encontradas
- Inicio y fin de procesamiento por fuente
- Artículos scrapeados y guardados por fuente
- Resumen consolidado final

### Nivel WARNING
- No hay fuentes activas
- No hay scraper disponible para una fuente
- No se pudo extraer contenido de un artículo

### Nivel ERROR
- Errores al procesar una fuente específica
- Errores al persistir artículos
- Errores críticos del coordinador

### Nivel DEBUG
- Artículos duplicados omitidos
- Detalles de cada artículo guardado

### Ejemplo de Configuración

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Consola
        logging.FileHandler('scraping_coordinator.log')  # Archivo
    ]
)
```

## Integración con Programadores

El coordinador está diseñado para integrarse fácilmente con sistemas de programación:

### Cron

```bash
# Ejecutar cada día a las 6 AM
0 6 * * * cd /path/to/project && python demo_scrape_all_sources.py >> /var/log/scraping.log 2>&1
```

### APScheduler

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

async def scheduled_scraping():
    scrape_all = ScrapeAllSourcesUseCase(...)
    await scrape_all.execute()

scheduler = AsyncIOScheduler()
scheduler.add_job(
    scheduled_scraping,
    'cron',
    hour=6,
    minute=0,
    id='daily_scraping'
)
scheduler.start()
```

### Celery

```python
from celery import Celery
import asyncio

app = Celery('scraping_tasks')

@app.task
def scrape_all_sources_task():
    async def run():
        scrape_all = ScrapeAllSourcesUseCase(...)
        return await scrape_all.execute()
    
    return asyncio.run(run())

# Programar
app.conf.beat_schedule = {
    'scrape-daily': {
        'task': 'tasks.scrape_all_sources_task',
        'schedule': crontab(hour=6, minute=0),
    },
}
```

## Extensibilidad

### Agregar una Nueva Fuente

Para agregar soporte para una nueva fuente de noticias:

1. **Crear el Scraper** (implementar `ScraperPort`)
```python
class ElCronistaScraper:
    def scrape(self) -> list[ArticleDTO]:
        # Implementación específica
        ...
```

2. **Actualizar el Factory**
```python
# En ScrapeAllSourcesUseCase.__init__
self._scraper_factory = {
    "Clarín": lambda: ClarinScraper(max_articles=15),
    "Página12": lambda: Pagina12Scraper(max_articles=15),
    "La Nación": lambda: LaNacionScraper(max_articles=15),
    "El Cronista": lambda: ElCronistaScraper(max_articles=15),  # Nueva fuente
}
```

3. **Registrar la Fuente en BD**
```python
source = Source.create(
    nombre="El Cronista",
    dominio="cronista.com",
    pais="Argentina"
)
await source_repository.create(source)
```

### Personalizar Comportamiento

El coordinador puede personalizarse mediante herencia:

```python
class CustomScrapeAllSourcesUseCase(ScrapeAllSourcesUseCase):
    
    async def _process_source(self, source):
        # Lógica personalizada antes del scraping
        await self._notify_start(source)
        
        # Ejecutar procesamiento original
        result = await super()._process_source(source)
        
        # Lógica personalizada después del scraping
        await self._notify_completion(source, result)
        
        return result
    
    async def _notify_start(self, source):
        # Enviar notificación, email, etc.
        ...
    
    async def _notify_completion(self, source, result):
        # Enviar estadísticas, alertas, etc.
        ...
```

## Manejo de Errores

El coordinador implementa manejo robusto de errores:

1. **Errores a nivel de fuente**: Si una fuente falla, las demás continúan
2. **Errores a nivel de artículo**: Si un artículo falla, los demás continúan
3. **Errores críticos**: Cualquier error no manejado se propaga con contexto

### Estrategias de Recuperación

```python
# El coordinador registra el error pero no detiene la ejecución
try:
    article = await self._extract_article(url)
except Exception as e:
    logger.error(f"Error extrayendo artículo {url}: {e}")
    continue  # Continuar con el siguiente artículo
```

## Testing

El proyecto incluye tests comprehensivos:

```bash
# Ejecutar tests del coordinador
pytest tests/unit/test_scrape_all_sources_use_case.py -v

# Ejecutar con cobertura
pytest tests/unit/test_scrape_all_sources_use_case.py --cov=src.application.use_cases.scrape_all_sources
```

### Tests Incluidos

- ✅ Ejecución sin fuentes activas
- ✅ Ejecución con fuentes activas
- ✅ Manejo de fallos de scraper
- ✅ Filtrado de duplicados
- ✅ Obtención de scraper por fuente
- ✅ Construcción de detalles de job
- ✅ Construcción de respuesta vacía

## Monitoreo y Observabilidad

### Métricas Recomendadas

- **Tasa de éxito**: `total_jobs_completed / total_sources`
- **Artículos por fuente**: Promedio de artículos scrapeados por fuente
- **Tasa de duplicados**: `duplicates / total_articles_scraped`
- **Tiempo de ejecución**: Duración de cada job
- **Errores**: Frecuencia y tipos de errores

### Integración con Herramientas

```python
# Ejemplo con Prometheus
from prometheus_client import Counter, Histogram

scraping_jobs_total = Counter('scraping_jobs_total', 'Total scraping jobs', ['source', 'status'])
scraping_duration = Histogram('scraping_duration_seconds', 'Scraping duration', ['source'])

# En el coordinador
with scraping_duration.labels(source=source_name).time():
    result = await self._process_source(source)
    
scraping_jobs_total.labels(source=source_name, status=result['status']).inc()
```

## Mejores Prácticas

1. **Configurar timeouts**: Los scrapers deben tener timeouts configurados
2. **Rate limiting**: Implementar delays entre requests para no sobrecargar servidores
3. **User agents**: Usar user agents realistas y rotativos
4. **Respeto a robots.txt**: Verificar y respetar las políticas de scraping
5. **Monitoreo activo**: Implementar alertas para fallos recurrentes
6. **Backup de datos**: Mantener backups regulares de la BD de artículos
7. **Logs rotativos**: Configurar rotación de logs para evitar llenar el disco

## Troubleshooting

### Problema: No se encuentran fuentes activas

**Solución**: Verificar que hay fuentes registradas y activas en la BD

```python
sources = await source_repository.get_active_sources()
print(f"Fuentes activas: {len(sources)}")
```

### Problema: Todos los jobs fallan

**Solución**: Verificar conectividad, user agents, y logs detallados

```python
# Habilitar logging DEBUG
logging.getLogger('src.application.use_cases').setLevel(logging.DEBUG)
logging.getLogger('src.infrastructure.adapters.scrapers').setLevel(logging.DEBUG)
```

### Problema: Alto número de duplicados

**Solución**: Puede ser normal si se ejecuta frecuentemente. Ajustar frecuencia de ejecución.

### Problema: Scraper específico siempre falla

**Solución**: El sitio puede haber cambiado su estructura. Actualizar selectores del scraper.

## Roadmap

Futuras mejoras planeadas:

- [ ] Soporte para scraping paralelo (asyncio.gather)
- [ ] Reintentos automáticos con backoff exponencial
- [ ] Detección automática de cambios en estructura de sitios
- [ ] Dashboard web para visualización de estadísticas
- [ ] Notificaciones push/email de resultados
- [ ] Soporte para plugins de scrapers externos
- [ ] API REST para ejecutar y consultar jobs
- [ ] Filtros y categorización automática de artículos

## Contacto y Soporte

Para preguntas, reportes de bugs o sugerencias, contactar al equipo de desarrollo.

## Licencia

Este componente es parte del proyecto de agregador de noticias argentinas.
