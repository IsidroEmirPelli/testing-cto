# 🕷️ Scraper de La Nación - Documentación

## 📋 Resumen

Implementación completa de un scraper específico para el sitio web de La Nación que extrae artículos recientes y los persiste en la base de datos, evitando duplicados.

## ✅ Características Implementadas

### 1. Scraper (LaNacionScraper)
- ✅ Implementa la interfaz `ScraperPort` mediante Protocol typing
- ✅ Extrae artículos de múltiples secciones:
  - Política
  - Economía
  - Sociedad
- ✅ Retorna objetos `ArticleDTO` estandarizados
- ✅ Manejo robusto de errores y logging
- ✅ Configuración flexible (max_articles, timeout)

### 2. Extracción de Datos
- ✅ **Título**: Múltiples selectores de fallback
- ✅ **Contenido**: Extracción de párrafos con normalización de texto
- ✅ **URL**: URLs absolutas y completas
- ✅ **Fecha de Publicación**: Extracción de metadatos o fecha actual
- ✅ **Fuente**: "La Nación" hardcodeado
- ✅ **Normalización**: Limpieza de espacios, saltos de línea y caracteres especiales

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
- ✅ Tests unitarios completos implementados
- ✅ Tests de inicialización
- ✅ Tests de extracción de título, contenido y fecha
- ✅ Tests de normalización de texto
- ✅ Tests de manejo de errores
- ✅ Tests de filtrado de URLs
- ✅ Tests de integración con base de datos
- ✅ Script de prueba funcional (`test_lanacion_scraper.py`)

## 📁 Estructura de Archivos

```
src/infrastructure/adapters/scrapers/
├── __init__.py
├── clarin_scraper.py
├── pagina12_scraper.py
└── lanacion_scraper.py              # Scraper de La Nación

src/application/use_cases/
└── scrape_and_persist_articles.py # Caso de uso de scraping + persistencia

tests/unit/
└── test_lanacion_scraper.py         # Tests unitarios

tests/integration/
└── test_lanacion_scraper_integration.py  # Tests de integración

test_lanacion_scraper.py             # Script de prueba funcional
```

## 🚀 Uso

### Uso Básico

```python
from src.infrastructure.adapters.scrapers.lanacion_scraper import LaNacionScraper

# Crear instancia del scraper
scraper = LaNacionScraper(max_articles=15)

# Ejecutar scraping
articles = scraper.scrape()

# Procesar artículos
for article in articles:
    print(f"{article.titulo} - {article.url}")
```

### Uso con Persistencia

```python
import asyncio
from src.infrastructure.adapters.scrapers.lanacion_scraper import LaNacionScraper
from src.infrastructure.persistence.django_repositories import DjangoNewsArticleRepository
from src.application.use_cases.scrape_and_persist_articles import ScrapeAndPersistArticlesUseCase

async def main():
    # Inicializar componentes
    scraper = LaNacionScraper(max_articles=15)
    repository = DjangoNewsArticleRepository()
    use_case = ScrapeAndPersistArticlesUseCase(scraper, repository)
    
    # Ejecutar
    result = await use_case.execute()
    
    print(f"Total scrapeados: {result['total_scraped']}")
    print(f"Nuevos insertados: {result['total_new']}")
    print(f"Duplicados omitidos: {result['total_duplicates']}")

asyncio.run(main())
```

### Script de Prueba

```bash
# Ejecutar el script de prueba funcional
python test_lanacion_scraper.py

# El script realiza:
# 1. Scrapea artículos de La Nación
# 2. Los persiste en la base de datos
# 3. Verifica duplicados
# 4. Muestra estadísticas y muestra de artículos
```

## 🔧 Configuración

### Parámetros del Scraper

```python
scraper = LaNacionScraper(
    max_articles=15,  # Número máximo de artículos a extraer
    timeout=30        # Timeout para peticiones HTTP (segundos)
)
```

### Secciones Extraídas

El scraper extrae artículos de las siguientes secciones:

1. **Política**: `https://www.lanacion.com.ar/politica/`
2. **Economía**: `https://www.lanacion.com.ar/economia/`
3. **Sociedad**: `https://www.lanacion.com.ar/sociedad/`

## 📊 Flujo de Extracción

### Fase 1: Recolección de URLs

1. Accede a cada sección configurada
2. Extrae URLs de artículos de:
   - Tags `<article>` con enlaces
   - Títulos `<h2>` y `<h3>` con enlaces
3. Filtra URLs no deseadas (temas, autores, secciones)
4. Elimina duplicados
5. Limita a `max_articles`

### Fase 2: Extracción de Contenido

Para cada URL:

1. **Título**: Busca en selectores específicos de La Nación
   - `h1.com-title`
   - `h1.title`
   - `h1.nota-title`
   - `h1` genérico
   - Meta tag `og:title`

2. **Contenido**: Extrae párrafos de:
   - `div.nota`
   - `div.contenido`
   - `div.article-body`
   - Tags `<article>`

3. **Fecha de Publicación**: Extrae de:
   - Meta tag `article:published_time`
   - Meta tag `publishdate`
   - Tag `<time>` con atributo `datetime`
   - Spans con clase `fecha` o `date`
   - Default: fecha actual si no se encuentra

4. **Normalización**: Limpia el texto extraído
   - Elimina espacios múltiples
   - Elimina saltos de línea
   - Elimina caracteres especiales

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
pytest tests/unit/test_lanacion_scraper.py -v
```

### Ejecutar Tests de Integración

```bash
pytest tests/integration/test_lanacion_scraper_integration.py -v
```

### Tests Implementados

**Tests Unitarios:**
- `test_scraper_initialization`: Inicialización correcta
- `test_scraper_default_initialization`: Valores por defecto
- `test_scrape_returns_list`: Tipo de retorno
- `test_extract_title_from_different_selectors`: Extracción de títulos
- `test_extract_content_from_paragraphs`: Extracción de contenido
- `test_extract_publication_date_from_meta`: Extracción de fechas
- `test_extract_publication_date_defaults_to_now`: Fecha por defecto
- `test_article_dto_has_required_fields`: Validación de DTO
- `test_scraper_handles_network_errors_gracefully`: Manejo de errores
- `test_scraper_filters_unwanted_urls`: Filtrado de URLs
- `test_clean_text_removes_extra_whitespace`: Normalización de espacios
- `test_clean_text_removes_newlines`: Normalización de saltos de línea

**Tests de Integración:**
- `test_complete_scraping_flow`: Flujo completo de scraping y persistencia
- `test_duplicate_detection`: Detección de duplicados
- `test_scraper_handles_real_website`: Prueba con sitio real

## 🔍 Manejo de Errores

El scraper implementa manejo robusto de errores:

### Errores de Red
- Timeout en peticiones HTTP
- Errores de conexión
- Respuestas HTTP no exitosas (4xx, 5xx)

### Errores de Parsing
- HTML malformado
- Selectores no encontrados
- Encoding incorrecto

### Logging
- Nivel INFO para operaciones normales
- Nivel WARNING para artículos sin título/contenido
- Nivel ERROR para errores de red o parsing

## 📈 Estadísticas y Resultados

El caso de uso retorna un diccionario con:

```python
{
    'total_scraped': int,      # Total de artículos scrapeados
    'total_new': int,          # Artículos nuevos insertados
    'total_duplicates': int,   # Artículos duplicados omitidos
    'articles': list[Entity]   # Lista de artículos (entidades)
}
```

## 🎯 Criterios de Aceptación

✅ **Scraper independiente y funcional**
- El scraper funciona de manera autónoma
- No depende de implementaciones específicas de otros scrapers
- Sigue el mismo patrón que Clarín y Página 12

✅ **Múltiples secciones**
- Extrae de Política, Economía y Sociedad
- Hasta 15 artículos por defecto

✅ **Manejo de encoding**
- Utiliza BeautifulSoup con parser 'lxml'
- Maneja correctamente UTF-8 y otros encodings

✅ **Normalización de contenido**
- Limpia espacios múltiples
- Elimina saltos de línea
- Normaliza texto extraído

✅ **Prevención de duplicados**
- Verifica URLs antes de insertar
- No inserta artículos duplicados

✅ **Base de datos con tres fuentes**
- La base de datos ahora contiene artículos de:
  - Clarín
  - Página 12
  - La Nación

## 🔗 URLs de Ejemplo

```
https://www.lanacion.com.ar/politica/
https://www.lanacion.com.ar/economia/
https://www.lanacion.com.ar/sociedad/
```

## 🚀 Próximos Pasos

1. **Configurar cron jobs**: Ejecutar el scraper periódicamente
2. **Monitoreo**: Implementar alertas para errores de scraping
3. **Rate limiting**: Agregar delays entre peticiones si es necesario
4. **Caché**: Implementar caché de URLs ya procesadas
5. **Scrapers adicionales**: Agregar más fuentes de noticias

## 📝 Notas Técnicas

### Diferencias con Scrapers Anteriores

- Similar a Clarín y Página 12 en estructura
- Incluye método `_clean_text()` para normalización
- Busca también en tags `<h2>` y `<h3>` para URLs
- Filtros específicos para URLs de La Nación

### Consideraciones de Performance

- Sesiones HTTP reutilizadas para eficiencia
- Timeout configurable para evitar bloqueos
- Logging detallado para debugging
- Manejo graceful de errores sin interrumpir el proceso

### Compatibilidad

- Python 3.12+
- Django ORM para persistencia
- BeautifulSoup4 con lxml parser
- Requests para peticiones HTTP
