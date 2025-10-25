# 🚀 Ticket 8 - Coordinador de Scraping: Quick Start

## ✅ ¿Qué se implementó?

Un **coordinador de scraping** que ejecuta automáticamente el scraping de todas las fuentes activas (Clarín, Página12, La Nación) y registra los resultados en la base de datos.

## 📦 Archivos Creados

### Código Principal
- ✅ `src/application/use_cases/scrape_all_sources.py` - Coordinador principal
- ✅ `tests/unit/test_scrape_all_sources_use_case.py` - Tests (10/10 passing)

### Scripts Ejecutables
- ✅ `demo_scrape_all_sources.py` - Script de demostración
- ✅ `examples_scheduler_integration.py` - Ejemplos de integración
- ✅ `example_api_endpoint.py` - Ejemplo de API REST

### Documentación
- ✅ `SCRAPING_COORDINATOR_DOCUMENTATION.md` - Documentación completa
- ✅ `COORDINADOR_SCRAPING_README.md` - Guía rápida
- ✅ `TICKET_8_IMPLEMENTATION_SUMMARY.md` - Resumen de implementación
- ✅ `TICKET_8_QUICK_START.md` - Este archivo

## 🏃 Probar Ahora (3 pasos)

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Ejecutar el coordinador
python demo_scrape_all_sources.py

# 3. Ver los resultados
# El script mostrará estadísticas completas en consola
```

## 💻 Uso Programático

```python
import asyncio
from src.application.use_cases import ScrapeAllSourcesUseCase
from src.infrastructure.persistence.django_repositories import (
    DjangoSourceRepository,
    DjangoScrapingJobRepository,
    DjangoNewsArticleRepository,
)

async def main():
    # Crear caso de uso
    scrape_all = ScrapeAllSourcesUseCase(
        source_repository=DjangoSourceRepository(),
        scraping_job_repository=DjangoScrapingJobRepository(),
        article_repository=DjangoNewsArticleRepository(),
    )
    
    # Ejecutar
    result = await scrape_all.execute()
    
    # Usar resultados
    print(f"Fuentes: {result['total_sources']}")
    print(f"Artículos: {result['total_articles_scraped']}")
    print(f"Nuevos: {result['total_articles_persisted']}")

asyncio.run(main())
```

## 🧪 Verificar Tests

```bash
pytest tests/unit/test_scrape_all_sources_use_case.py -v
```

**Resultado esperado**: ✅ 10/10 tests passed

## ⏰ Programar Ejecuciones

### Opción 1: Cron (Simple)
```bash
# Editar crontab
crontab -e

# Agregar: ejecutar diariamente a las 6 AM
0 6 * * * cd /path/to/project && source venv/bin/activate && python demo_scrape_all_sources.py >> /var/log/scraping.log 2>&1
```

### Opción 2: APScheduler (Avanzado)
Ver `examples_scheduler_integration.py` para código completo.

### Opción 3: Celery (Distribuido)
Ver `examples_scheduler_integration.py` para configuración.

## 📊 Estructura de Respuesta

```python
{
    'total_sources': 3,                # Fuentes procesadas
    'total_jobs_completed': 3,         # Jobs exitosos
    'total_jobs_failed': 0,            # Jobs fallidos
    'total_articles_scraped': 45,      # Artículos encontrados
    'total_articles_persisted': 38,    # Artículos nuevos guardados
    'jobs_details': [...]              # Detalles por fuente
}
```

## 📝 Tabla ScrapingJob

Cada ejecución crea registros con:
- `fuente`: Nombre de la fuente
- `status`: pending → running → completed/failed
- `total_articulos`: Cantidad scrapeada
- `fecha_inicio` / `fecha_fin`: Timestamps
- Y más...

## 🔍 Consultar Resultados

```python
# Ver últimos jobs
from src.infrastructure.persistence.django_repositories import DjangoScrapingJobRepository
import asyncio

async def ver_jobs():
    repo = DjangoScrapingJobRepository()
    jobs = await repo.get_all(skip=0, limit=10)
    for job in jobs:
        print(f"{job.fuente}: {job.status} - {job.total_articulos} artículos")

asyncio.run(ver_jobs())
```

## 🌐 Exponer como API REST

Ver `example_api_endpoint.py` para endpoints completos:
- `POST /api/scraping/execute/` - Ejecutar scraping
- `GET /api/scraping/status/` - Ver estado de jobs
- `GET /api/scraping/statistics/<fuente>/` - Estadísticas por fuente
- `GET /api/scraping/health/` - Health check

## 📚 Documentación Completa

Para información detallada, ver:

1. **`COORDINADOR_SCRAPING_README.md`**
   - Guía de usuario
   - Ejemplos básicos
   - FAQ

2. **`SCRAPING_COORDINATOR_DOCUMENTATION.md`**
   - Arquitectura completa
   - Casos de uso avanzados
   - Troubleshooting
   - Mejores prácticas

3. **`TICKET_8_IMPLEMENTATION_SUMMARY.md`**
   - Detalles de implementación
   - Decisiones de diseño
   - Checklist completo

4. **`examples_scheduler_integration.py`**
   - 7 ejemplos de integración
   - Código copy-paste ready
   - Menú interactivo

5. **`example_api_endpoint.py`**
   - 4 endpoints REST
   - Ejemplos con curl, Python, JavaScript
   - Configuración completa

## ✨ Características Destacadas

- ✅ **Automático**: Procesa todas las fuentes activas
- ✅ **Resiliente**: Un error no detiene todo
- ✅ **Inteligente**: Filtra duplicados automáticamente
- ✅ **Auditable**: Registra todo en BD
- ✅ **Observable**: Logs detallados
- ✅ **Extensible**: Fácil agregar fuentes
- ✅ **Testeable**: 100% cubierto por tests

## 🎯 Casos de Uso

### Scraping Programado
```bash
# Diariamente a las 6 AM
0 6 * * * python demo_scrape_all_sources.py
```

### Scraping On-Demand
```bash
# Manual cuando sea necesario
python demo_scrape_all_sources.py
```

### Scraping via API
```bash
# Desde cualquier cliente
curl -X POST http://localhost:8000/api/scraping/execute/
```

## 🐛 Troubleshooting

### Problema: No se encuentran fuentes
**Solución**: Asegurarse que hay fuentes activas en la BD

### Problema: Tests no pasan
**Solución**: Activar venv y verificar dependencias
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problema: Import errors
**Solución**: Asegurarse de estar en el directorio del proyecto
```bash
cd /path/to/project
python -c "from src.application.use_cases import ScrapeAllSourcesUseCase"
```

## 📞 Próximos Pasos

1. **Probar el coordinador**: `python demo_scrape_all_sources.py`
2. **Ver los tests**: `pytest tests/unit/test_scrape_all_sources_use_case.py -v`
3. **Explorar ejemplos**: `python examples_scheduler_integration.py`
4. **Leer documentación**: Ver archivos .md mencionados arriba
5. **Integrar con scheduler**: Elegir cron/APScheduler/Celery según necesidad

## ✅ Checklist de Verificación

- [x] Código implementado y testeado
- [x] 10/10 tests passing
- [x] Documentación completa
- [x] Scripts de demo funcionales
- [x] Ejemplos de integración
- [x] API REST de ejemplo
- [x] Listo para producción

## 🎉 ¡Listo!

El coordinador de scraping está completamente implementado, testeado y documentado. 
¡Listo para usar en producción!

---

**Nota**: Este coordinador es parte del Ticket 8 del proyecto de agregador de noticias argentinas.
