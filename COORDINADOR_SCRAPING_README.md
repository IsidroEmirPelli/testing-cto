# Coordinador de Scraping - Guía Rápida

## 🎯 Propósito

El **Coordinador de Scraping** (`ScrapeAllSourcesUseCase`) es un componente que ejecuta automáticamente el scraping de todas las fuentes activas de noticias (Clarín, Página12, La Nación) y registra los resultados en la base de datos.

## ✨ Características

- ✅ Ejecuta scraping de múltiples fuentes en una sola operación
- ✅ Registra cada ejecución en la tabla `ScrapingJob` con estadísticas detalladas
- ✅ Filtra automáticamente artículos duplicados
- ✅ Manejo robusto de errores (una fuente que falla no detiene las demás)
- ✅ Logging centralizado y detallado
- ✅ Listo para integración con sistemas de programación (cron, APScheduler, Celery)
- ✅ Estadísticas consolidadas en tiempo real

## 🚀 Inicio Rápido

### Opción 1: Script de Demostración

La forma más rápida de probar el coordinador:

```bash
# Activar el entorno virtual
source venv/bin/activate

# Ejecutar el script de demostración
python demo_scrape_all_sources.py
```

El script mostrará:
- Fuentes activas encontradas
- Progreso del scraping por fuente
- Estadísticas consolidadas
- Detalles por cada fuente

### Opción 2: Uso Programático

```python
import asyncio
from src.application.use_cases import ScrapeAllSourcesUseCase
from src.infrastructure.persistence.django_repositories import (
    DjangoSourceRepository,
    DjangoScrapingJobRepository,
    DjangoNewsArticleRepository,
)

async def main():
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
    print(f"Artículos scrapeados: {result['total_articles_scraped']}")
    print(f"Artículos nuevos: {result['total_articles_persisted']}")

asyncio.run(main())
```

## 📊 Respuesta del Coordinador

El método `execute()` retorna un diccionario con estadísticas completas:

```python
{
    'total_sources': 3,                    # Fuentes procesadas
    'total_jobs_completed': 3,             # Jobs exitosos
    'total_jobs_failed': 0,                # Jobs fallidos
    'total_articles_scraped': 45,          # Total artículos encontrados
    'total_articles_persisted': 38,        # Artículos nuevos guardados
    'jobs_details': [                      # Detalle por fuente
        {
            'job_id': 'uuid-here',
            'source': 'Clarín',
            'status': 'completed',
            'fecha_inicio': '2024-01-15T10:00:00Z',
            'fecha_fin': '2024-01-15T10:02:30Z',
            'articles_scraped': 15,
            'articles_persisted': 12,
            'duplicates': 3,
            'error': None
        },
        # ... más fuentes
    ]
}
```

## 📁 Archivos Importantes

### Código Principal
- **`src/application/use_cases/scrape_all_sources.py`** - Implementación del coordinador
- **`demo_scrape_all_sources.py`** - Script de demostración ejecutable
- **`examples_scheduler_integration.py`** - Ejemplos de integración con schedulers

### Documentación
- **`SCRAPING_COORDINATOR_DOCUMENTATION.md`** - Documentación completa y detallada
- **`COORDINADOR_SCRAPING_README.md`** - Esta guía rápida

### Tests
- **`tests/unit/test_scrape_all_sources_use_case.py`** - Suite de tests completa

## 🔄 Integración con Schedulers

### Cron (Linux/Unix)

```bash
# Editar crontab
crontab -e

# Ejecutar diariamente a las 6 AM
0 6 * * * cd /path/to/project && source venv/bin/activate && python demo_scrape_all_sources.py >> /var/log/scraping.log 2>&1
```

### APScheduler (Python)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
    execute_scraping,
    'cron',
    hour=6,
    minute=0
)
scheduler.start()
```

### Celery (Distribuido)

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost')

@app.task
def scrape_task():
    return asyncio.run(execute_scraping())

# Configurar schedule
app.conf.beat_schedule = {
    'daily-scraping': {
        'task': 'tasks.scrape_task',
        'schedule': crontab(hour=6, minute=0),
    },
}
```

Ver `examples_scheduler_integration.py` para más ejemplos detallados.

## 📝 Registro de Scraping Jobs

Cada ejecución crea registros en la tabla `ScrapingJob`:

| Campo | Descripción |
|-------|-------------|
| `id` | UUID único del job |
| `fuente` | Nombre de la fuente (Clarín, Página12, La Nación) |
| `fecha_inicio` | Timestamp de inicio |
| `fecha_fin` | Timestamp de finalización |
| `status` | Estado: `pending`, `running`, `completed`, `failed` |
| `total_articulos` | Cantidad de artículos scrapeados |
| `created_at` | Fecha de creación del registro |
| `updated_at` | Fecha de última actualización |

## 🐛 Debugging y Logs

### Configurar Logging Detallado

```python
import logging

# Para ver todos los detalles
logging.basicConfig(level=logging.DEBUG)

# Solo para el coordinador
logging.getLogger('src.application.use_cases.scrape_all_sources').setLevel(logging.DEBUG)

# Solo para scrapers
logging.getLogger('src.infrastructure.adapters.scrapers').setLevel(logging.DEBUG)
```

### Ver Logs en Tiempo Real

```bash
# Durante la ejecución
python demo_scrape_all_sources.py 2>&1 | tee scraping_$(date +%Y%m%d_%H%M%S).log

# Ver el archivo de log
tail -f scraping_coordinator.log
```

## 🧪 Testing

```bash
# Ejecutar tests del coordinador
pytest tests/unit/test_scrape_all_sources_use_case.py -v

# Con cobertura
pytest tests/unit/test_scrape_all_sources_use_case.py --cov=src.application.use_cases.scrape_all_sources --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html
```

## 🔧 Configuración

### Ajustar Cantidad de Artículos

Por defecto, cada scraper extrae hasta 15 artículos. Para cambiar:

```python
# En scrape_all_sources.py, línea ~45
self._scraper_factory = {
    "Clarín": lambda: ClarinScraper(max_articles=30),        # Aumentar a 30
    "Página12": lambda: Pagina12Scraper(max_articles=30),
    "La Nación": lambda: LaNacionScraper(max_articles=30),
}
```

### Agregar Nueva Fuente

1. Crear el scraper (implementar `ScraperPort`)
2. Agregar al factory en `ScrapeAllSourcesUseCase.__init__`
3. Registrar la fuente en la base de datos

Ver documentación completa para detalles.

## 📚 Documentación Adicional

- **Documentación Completa**: Ver `SCRAPING_COORDINATOR_DOCUMENTATION.md`
- **Ejemplos de Integración**: Ver `examples_scheduler_integration.py`
- **Tests**: Ver `tests/unit/test_scrape_all_sources_use_case.py`

## ⚡ Tips de Rendimiento

1. **Rate Limiting**: Los scrapers ya incluyen delays razonables
2. **Timeouts**: Configurados a 30 segundos por request
3. **Connection Pooling**: Usa `requests.Session()` para eficiencia
4. **Error Handling**: Un error en una fuente no detiene las demás
5. **Logging**: Use nivel INFO en producción, DEBUG solo para troubleshooting

## 🔒 Consideraciones de Seguridad

- Respetar robots.txt de cada sitio
- No ejecutar con demasiada frecuencia (recomendado: máximo cada 4 horas)
- Usar user agents realistas
- Implementar rate limiting si es necesario
- Monitorear logs de errores

## 💡 Casos de Uso Comunes

### 1. Scraping Programado Diario
```bash
# Cron para ejecutar todos los días a las 6 AM
0 6 * * * cd /path/to/project && source venv/bin/activate && python demo_scrape_all_sources.py
```

### 2. Scraping On-Demand via API
```python
@app.post("/api/scraping/execute")
async def execute_scraping_endpoint():
    result = await scrape_all_use_case.execute()
    return result
```

### 3. Monitoreo de Jobs
```python
# Ver últimos jobs
jobs = await job_repository.get_all(skip=0, limit=10)
for job in jobs:
    print(f"{job.fuente}: {job.status} - {job.total_articulos} artículos")
```

### 4. Estadísticas Históricas
```python
# Jobs por fuente
clarin_jobs = await job_repository.get_by_fuente("Clarín")
total_articles = sum(job.total_articulos for job in clarin_jobs)
print(f"Total artículos de Clarín: {total_articles}")
```

## ❓ FAQ

**P: ¿Con qué frecuencia debo ejecutar el coordinador?**  
R: Recomendado cada 4-6 horas para evitar sobrecarga de los sitios.

**P: ¿Qué pasa si una fuente falla?**  
R: El coordinador registra el error pero continúa con las demás fuentes.

**P: ¿Cómo maneja los duplicados?**  
R: Verifica cada artículo por URL antes de guardar. Los duplicados se omiten automáticamente.

**P: ¿Puedo ejecutar múltiples coordinadores en paralelo?**  
R: No recomendado. Usar un solo coordinador con un scheduler apropiado.

**P: ¿Cómo agrego una nueva fuente?**  
R: Ver sección de extensibilidad en `SCRAPING_COORDINATOR_DOCUMENTATION.md`.

## 🆘 Soporte

Para problemas, bugs o preguntas:
- Revisar logs en `scraping_coordinator.log`
- Ejecutar con nivel DEBUG
- Verificar conectividad y acceso a sitios
- Revisar tests para ejemplos de uso

## 📄 Licencia

Este componente es parte del proyecto de agregador de noticias argentinas.
