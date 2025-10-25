# 🕷️ Scraper de Clarín - Documentación

## 📋 Resumen

Implementación completa de un scraper específico para el sitio web de Clarín que extrae artículos recientes y los persiste en la base de datos, evitando duplicados.

## ✅ Características Implementadas

### 1. Scraper (ClarinScraper)
- ✅ Implementa la interfaz `ScraperPort` mediante Protocol typing
- ✅ Extrae artículos de múltiples secciones:
  - Últimas Noticias
  - Política
  - Economía
- ✅ Retorna objetos `ArticleDTO` estandarizados
- ✅ Manejo robusto de errores y logging
- ✅ Configuración flexible (max_articles, timeout)

### 2. Extracción de Datos
- ✅ **Título**: Múltiples selectores de fallback
- ✅ **Contenido**: Extracción de párrafos y texto completo
- ✅ **URL**: URLs absolutas y completas
- ✅ **Fecha de Publicación**: Extracción de metadatos o fecha actual
- ✅ **Fuente**: "Clarín" hardcodeado

### 3. Caso de Uso (ScrapeAndPersistArticlesUseCase)
- ✅ Orquesta el flujo completo de scraping y persistencia
- ✅ Verifica duplicados por URL antes de insertar
- ✅ Utiliza el repositorio de NewsArticle para persistencia
- ✅ Retorna estadísticas detalladas del proceso

### 4. Prevención de Duplicados
- ✅ Consulta la base de datos por URL antes de insertar
- ✅ Logging de artículos duplicados omitidos
- ✅ Contador de duplicados en las estadísticas

### 5. Testing
- ✅ 10 tests unitarios implementados
- ✅ Tests de inicialización
- ✅ Tests de extracción de título, contenido y fecha
- ✅ Tests de manejo de errores
- ✅ Tests de filtrado de URLs
- ✅ Script de prueba funcional (`test_clarin_scraper.py`)

## 📁 Estructura de Archivos

```
src/infrastructure/adapters/scrapers/
├── __init__.py
└── clarin_scraper.py              # Scraper de Clarín

src/application/use_cases/
└── scrape_and_persist_articles.py # Caso de uso de scraping + persistencia

tests/unit/
└── test_clarin_scraper.py         # Tests unitarios

test_clarin_scraper.py             # Script de prueba funcional
```

## 🚀 Uso

### Uso Básico

```python
from src.infrastructure.adapters.scrapers.clarin_scraper import ClarinScraper

# Crear instancia del scraper
scraper = ClarinScraper(max_articles=15)

# Ejecutar scraping
articles = scraper.scrape()

# Procesar artículos
for article in articles:
    print(f"{article.titulo} - {article.url}")
```

### Uso con Persistencia

```python
import asyncio
from src.infrastructure.adapters.scrapers.clarin_scraper import ClarinScraper
from src.infrastructure.persistence.django_repositories import DjangoNewsArticleRepository
from src.application.use_cases.scrape_and_persist_articles import ScrapeAndPersistArticlesUseCase

async def main():
    # Inicializar componentes
    scraper = ClarinScraper(max_articles=15)
    repository = DjangoNewsArticleRepository()
    use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)
    
    # Ejecutar
    result = await use_case.execute()
    
    print(f"Total scrapeados: {result['total_scraped']}")
    print(f"Nuevos insertados: {result['total_new']}")
    print(f"Duplicados omitidos: {result['total_duplicates']}")

asyncio.run(main())
```

### Uso del Script de Prueba

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar test del scraper
python test_clarin_scraper.py
```

## 🔧 Configuración

### Parámetros del Scraper

```python
ClarinScraper(
    max_articles=15,  # Número máximo de artículos a extraer
    timeout=30        # Timeout para peticiones HTTP (segundos)
)
```

### Secciones Scrapeadas

El scraper extrae artículos de las siguientes secciones:
- `/ultimas-noticias/`
- `/politica/`
- `/economia/`

## 📊 Resultados de Pruebas

### Test Funcional
```
✅ Total de artículos scrapeados: 15
✅ Artículos nuevos insertados: 15 (primera ejecución)
✅ Artículos duplicados omitidos: 0 (primera ejecución)

Segunda ejecución:
✅ Total de artículos scrapeados: 15
✅ Artículos nuevos insertados: 6
✅ Artículos duplicados omitidos: 9
```

### Tests Unitarios
```
✅ 10/10 tests pasando
- test_scraper_initialization
- test_scraper_default_initialization
- test_scrape_returns_list
- test_extract_title_from_different_selectors
- test_extract_content_from_paragraphs
- test_extract_publication_date_from_meta
- test_extract_publication_date_defaults_to_now
- test_article_dto_has_required_fields
- test_scraper_handles_network_errors_gracefully
- test_scraper_filters_unwanted_urls
```

## 🎯 Criterios de Aceptación

- [x] Scraper funcional que extrae artículos reales de Clarín
- [x] Implementa la interfaz ScraperPort
- [x] Extrae título, contenido, URL y fecha
- [x] Evita duplicados al insertar en la base de datos
- [x] Manejo apropiado de logs y errores
- [x] Al menos 10 artículos reales en la base de datos

## 🏗️ Arquitectura

### Principios Seguidos

1. **Arquitectura Hexagonal**: El scraper es un adaptador en la capa de infraestructura
2. **Protocol Typing**: Uso de `ScraperPort` Protocol para tipado estructural
3. **Separación de Responsabilidades**: 
   - `ClarinScraper`: Extracción de datos
   - `ScrapeAndPersistArticlesUseCase`: Lógica de negocio y persistencia
4. **Dependency Inversion**: El caso de uso depende de interfaces, no de implementaciones concretas

### Flujo de Datos

```
┌─────────────────┐
│  ClarinScraper  │ (Adaptador)
└────────┬────────┘
         │ scrape()
         ↓
┌─────────────────┐
│   ArticleDTO    │ (DTO)
└────────┬────────┘
         │
         ↓
┌─────────────────────────────┐
│ ScrapeAndPersistArticles    │ (Use Case)
│   UseCase                    │
└────────┬────────────────────┘
         │ check duplicates
         │ create entities
         │ persist
         ↓
┌─────────────────────────────┐
│ DjangoNewsArticleRepository │ (Repository)
└────────┬────────────────────┘
         │
         ↓
┌─────────────────┐
│    Database     │
└─────────────────┘
```

## 🐛 Manejo de Errores

El scraper implementa múltiples niveles de manejo de errores:

1. **Errores de Red**: Capturados y loggeados, continúa con otros artículos
2. **Errores de Parsing**: Intentos con múltiples selectores de fallback
3. **Artículos Sin Título**: Omitidos con warning en el log
4. **Duplicados en DB**: Detectados y omitidos sin error

## 📝 Logging

El scraper proporciona logging detallado:

```
INFO - ClarinScraper inicializado - max_articles: 15
INFO - Iniciando scraping de Clarín
INFO - Extrayendo URLs de sección: https://www.clarin.com/ultimas-noticias/
INFO - URLs extraídas de /ultimas-noticias/: 8
INFO - Extrayendo contenido de 15 artículos
INFO - Artículo extraído exitosamente: Título del artículo...
INFO - Scraping completado. Total de artículos extraídos: 15
INFO - Artículos nuevos insertados: 15
INFO - Artículos duplicados (omitidos): 0
```

## 🔄 Mejoras Futuras

Posibles mejoras para el scraper:

1. **Extracción de Categorías**: Parsear la categoría desde el breadcrumb
2. **Extracción de Imágenes**: Agregar URLs de imágenes principales
3. **Extracción de Autores**: Identificar autores de los artículos
4. **Rate Limiting**: Implementar delays entre peticiones
5. **Cache de Sesión**: Mantener cookies entre ejecuciones
6. **Scraping Incremental**: Solo scrapear artículos nuevos desde última ejecución
7. **Validación de Contenido**: Verificar que el contenido tenga longitud mínima

## 📚 Referencias

- **Documentación de BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/
- **Requests Library**: https://docs.python-requests.org/
- **Arquitectura Hexagonal**: Documentada en `docs/ARCHITECTURE.md`
- **ScraperPort Interface**: `src/domain/ports/scraper_port.py`

## 👥 Desarrollo

Implementado siguiendo los principios de:
- Clean Code
- SOLID
- Arquitectura Hexagonal
- Test-Driven Development (TDD)

---

**Estado**: ✅ Completado
**Fecha**: Octubre 2025
**Ticket**: #5 - Scraper Clarín
