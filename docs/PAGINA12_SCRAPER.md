# 📰 Scraper de Página 12 - Documentación Técnica

## 🎯 Propósito

Implementación de un scraper para extraer artículos del sitio web de Página 12 (https://www.pagina12.com.ar), siguiendo el mismo patrón arquitectónico que el scraper de Clarín.

## 🏗️ Arquitectura

### Implementación del ScraperPort

El `Pagina12Scraper` implementa la interfaz `ScraperPort` mediante Protocol typing estructural:

```python
class Pagina12Scraper:
    def scrape(self) -> list[ArticleDTO]:
        """Extrae artículos de Página 12"""
```

### Componentes

```
┌──────────────────────────────────────────────────────┐
│                  Pagina12Scraper                     │
│  (Infrastructure/Adapters/Scrapers)                  │
└───────────────────┬──────────────────────────────────┘
                    │
                    ├─► _extract_article_urls_from_section()
                    ├─► _extract_article_content()
                    ├─► _extract_title()
                    ├─► _extract_content()
                    ├─► _extract_publication_date()
                    └─► _clean_text()
```

## 🔍 Funcionalidad

### Secciones Scrapeadas

1. **El País** (`/secciones/el-pais`) - Noticias nacionales
2. **Economía** (`/secciones/economia`) - Noticias económicas
3. **Sociedad** (`/secciones/sociedad`) - Noticias de sociedad

### Campos Extraídos

| Campo | Descripción | Fuente HTML |
|-------|-------------|-------------|
| `titulo` | Título del artículo | `<h1>`, `<meta property="og:title">` |
| `url` | URL completa del artículo | URLs con `/notas/` o `/articulos/` |
| `contenido` | Texto completo del artículo | `<div class="article-text">`, `<p>` |
| `fecha_publicacion` | Fecha y hora de publicación | `<meta property="article:published_time">` |
| `fuente` | Nombre de la fuente | "Página 12" (hardcoded) |

## 🛠️ Implementación

### Inicialización

```python
from src.infrastructure.adapters.scrapers import Pagina12Scraper

# Con valores por defecto
scraper = Pagina12Scraper()

# Con configuración personalizada
scraper = Pagina12Scraper(max_articles=20, timeout=30)
```

**Parámetros:**
- `max_articles` (int): Número máximo de artículos a extraer (default: 15)
- `timeout` (int): Timeout para peticiones HTTP en segundos (default: 30)

### Uso Básico

```python
# Extraer artículos
articles = scraper.scrape()

# Procesar resultados
for article in articles:
    print(f"Título: {article.titulo}")
    print(f"URL: {article.url}")
    print(f"Fuente: {article.fuente}")
```

### Uso con Persistencia

```python
from src.application.use_cases import ScrapeAndPersistArticlesUseCase
from src.infrastructure.persistence.django_app.repositories import DjangoNewsArticleRepository

scraper = Pagina12Scraper()
repository = DjangoNewsArticleRepository()
use_case = ScrapeAndPersistArticlesUseCase(repository)

# Ejecutar scraping y persistencia
result = await use_case.execute(scraper)
print(f"Nuevos: {result['nuevos_insertados']}")
print(f"Duplicados: {result['duplicados']}")
```

## 🔧 Detalles Técnicos

### Proceso de Extracción

1. **Fase 1: Recolección de URLs**
   - Accede a cada sección configurada
   - Busca elementos `<article>` y `<div>` con clases de noticias
   - Filtra URLs no deseadas (autores, tags, suplementos)
   - Valida que las URLs contengan `/notas/` o `/articulos/`

2. **Fase 2: Extracción de Contenido**
   - Para cada URL recolectada:
     - Extrae título usando múltiples selectores
     - Extrae contenido de párrafos (filtra párrafos < 20 caracteres)
     - Extrae fecha de publicación
     - Limpia y normaliza el texto
     - Crea ArticleDTO

### Selectores HTML

#### Títulos
```python
title_selectors = [
    ('h1', {'class': 'article-title'}),
    ('h1', {'class': 'titulo-nota'}),
    ('h1', {'class': 'title'}),
    ('h1', {}),
    ('meta', {'property': 'og:title'}),
]
```

#### Contenido
```python
content_selectors = [
    ('div', {'class': 'article-text'}),
    ('div', {'class': 'article-body'}),
    ('div', {'class': 'texto-nota'}),
    ('div', {'class': 'content-nota'}),
    ('article', {'class': 'article'}),
]
```

#### Fechas
```python
date_selectors = [
    ('meta', {'property': 'article:published_time'}),
    ('meta', {'name': 'publishdate'}),
    ('meta', {'property': 'og:published_time'}),
    ('time', {'datetime': True}),
    ('span', {'class': 'date'}),
]
```

### Limpieza de Texto

El método `_clean_text()` reutiliza la lógica del scraper de Clarín:

```python
def _clean_text(self, text: str) -> str:
    """Limpia y normaliza el texto extraído"""
    if not text:
        return ""
    
    # Eliminar espacios múltiples
    text = ' '.join(text.split())
    
    # Eliminar saltos de línea y caracteres especiales
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # Eliminar espacios múltiples resultantes
    text = ' '.join(text.split())
    
    return text.strip()
```

## 📊 Manejo de Errores

### Errores de Red

```python
try:
    response = self.session.get(url, timeout=self.timeout)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Error de red: {e}")
    return None
```

### Errores de Parsing

```python
try:
    soup = BeautifulSoup(response.content, 'lxml')
    titulo = self._extract_title(soup)
    if not titulo:
        logger.warning(f"No se pudo extraer título")
        return None
except Exception as e:
    logger.error(f"Error inesperado: {e}", exc_info=True)
    return None
```

### Logging

El scraper utiliza logging estructurado:

```python
logger.info("Iniciando scraping de Página 12")
logger.info(f"Extrayendo URLs de sección: {section_url}")
logger.info(f"URLs extraídas: {len(urls)}")
logger.info(f"Artículo extraído: {titulo[:60]}...")
logger.error(f"Error extrayendo artículo {url}: {e}", exc_info=True)
logger.info(f"Scraping completado. Total: {len(articles)}")
```

## 🧪 Testing

### Tests Unitarios

Ubicación: `tests/unit/test_pagina12_scraper.py`

Tests implementados:
- ✅ Inicialización del scraper
- ✅ Extracción de títulos con diferentes selectores
- ✅ Extracción de contenido de párrafos
- ✅ Filtrado de párrafos cortos
- ✅ Extracción de fechas
- ✅ Manejo de errores de red
- ✅ Filtrado de URLs no deseadas
- ✅ Limpieza de texto
- ✅ Conformidad con ScraperPort

```bash
# Ejecutar tests unitarios
python -m pytest tests/unit/test_pagina12_scraper.py -v
```

### Tests de Integración

Ubicación: `tests/integration/test_pagina12_scraper_integration.py`

Tests implementados:
- ✅ Extracción de artículos del sitio real
- ✅ Flujo completo de scraping y persistencia
- ✅ Detección de duplicados

```bash
# Ejecutar tests de integración
python -m pytest tests/integration/test_pagina12_scraper_integration.py -v
```

### Script de Prueba Funcional

Ubicación: `test_pagina12_scraper.py`

```bash
# Ejecutar script de prueba
python test_pagina12_scraper.py
```

Salida esperada:
```
====================================================================
TEST FUNCIONAL: Scraper de Página 12
====================================================================

📊 Artículos de Página 12 en BD antes: 0

🔧 Inicializando componentes...
✅ Componentes inicializados

🕷️  Ejecutando scraping de Página 12...
--------------------------------------------------------------------

====================================================================
RESULTADOS DEL SCRAPING
====================================================================
✅ Total scrapeado:     15 artículos
✅ Nuevos insertados:   15 artículos
⚠️  Duplicados:         0 artículos
====================================================================

📊 Artículos de Página 12 en BD después: 15
📈 Incremento: +15 artículos

✅ CRITERIO CUMPLIDO: Al menos 10 artículos de Página 12 en la base de datos
```

## 🔄 Comparación con ClarinScraper

### Similitudes

| Aspecto | Ambos Scrapers |
|---------|----------------|
| Arquitectura | Implementan ScraperPort |
| Estructura | Dos fases: URLs → Contenido |
| Limpieza | Mismo método `_clean_text()` |
| Errores | Manejo gracioso, logging comprehensivo |
| Testing | Cobertura completa (unit + integration) |

### Diferencias

| Aspecto | ClarinScraper | Pagina12Scraper |
|---------|---------------|-----------------|
| Base URL | `www.clarin.com` | `www.pagina12.com.ar` |
| Secciones | `/ultimas-noticias/`, `/politica/`, `/economia/` | `/secciones/el-pais`, `/secciones/economia`, `/secciones/sociedad` |
| URLs válidas | Cualquier URL de Clarín | Solo con `/notas/` o `/articulos/` |
| Filtros | `/tema/`, `/tags/`, `/autor/` | `/autores/`, `/tags/`, `/suplementos/` |
| Selectores | Específicos de Clarín | Específicos de Página 12 |
| Filtro contenido | Sin filtro por longitud | Filtra párrafos < 20 caracteres |

## 📝 Características Destacadas

### 1. Reutilización de Código
- ✅ Mismo patrón arquitectónico que ClarinScraper
- ✅ Reutilización de lógica de limpieza de texto
- ✅ Mismo flujo de persistencia

### 2. Validación de Arquitectura
- ✅ Demuestra extensibilidad del sistema
- ✅ Nuevo scraper sin modificar dominio
- ✅ Conformidad con ScraperPort

### 3. Filtrado Inteligente
- ✅ Filtra URLs no deseadas (autores, tags, suplementos)
- ✅ Solo extrae URLs de notas/artículos
- ✅ Filtra párrafos muy cortos (< 20 caracteres)

### 4. Robustez
- ✅ Múltiples selectores de fallback
- ✅ Manejo gracioso de errores
- ✅ Logging comprehensivo
- ✅ Cierre automático de sesión

## 🚀 Ejemplo de Uso Completo

```python
#!/usr/bin/env python3
import asyncio
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.config.django_settings')
django.setup()

from src.infrastructure.adapters.scrapers import Pagina12Scraper
from src.infrastructure.persistence.django_app.repositories import DjangoNewsArticleRepository
from src.application.use_cases import ScrapeAndPersistArticlesUseCase

async def main():
    # Inicializar componentes
    scraper = Pagina12Scraper(max_articles=15)
    repository = DjangoNewsArticleRepository()
    use_case = ScrapeAndPersistArticlesUseCase(repository)
    
    # Ejecutar scraping y persistencia
    result = await use_case.execute(scraper)
    
    # Mostrar resultados
    print(f"Total scrapeado: {result['total_scrapeado']}")
    print(f"Nuevos insertados: {result['nuevos_insertados']}")
    print(f"Duplicados: {result['duplicados']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📈 Mejoras Futuras

### Funcionalidad
- [ ] Extracción de autores
- [ ] Extracción de categorías/tags
- [ ] Extracción de imágenes
- [ ] Soporte para más secciones

### Performance
- [ ] Scraping asíncrono con aiohttp
- [ ] Rate limiting configurable
- [ ] Caché de artículos
- [ ] Pool de conexiones

### Calidad
- [ ] Fixtures HTML para tests
- [ ] Tests de performance
- [ ] Validación de contenido
- [ ] Estadísticas detalladas

## 🎓 Conclusión

El `Pagina12Scraper` demuestra exitosamente:

1. ✅ **Extensibilidad**: Nuevo scraper sin modificar el dominio
2. ✅ **Reutilización**: Mismo patrón y lógica base
3. ✅ **Conformidad**: Implementa ScraperPort correctamente
4. ✅ **Calidad**: Cobertura completa de tests
5. ✅ **Documentación**: Documentación técnica detallada

El scraper está listo para producción y puede servir como plantilla para implementar scrapers de otras fuentes de noticias.

---

**Fecha**: Octubre 2025  
**Status**: ✅ COMPLETADO  
**Ticket**: #6 - Scraper Página 12
