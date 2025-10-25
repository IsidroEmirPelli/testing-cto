# Ticket 2: Definición del Modelo de Dominio - Entregables

## ✅ Entidades de Dominio Creadas

### 1. NewsArticle (`src/domain/entities/news_article.py`)
**Campos:**
- `id`: UUID (generado automáticamente)
- `titulo`: str
- `contenido`: str
- `fuente`: str
- `fecha_publicacion`: datetime
- `url`: str
- `categoria`: Optional[str]
- `procesado`: bool (default: False)
- `created_at`: datetime
- `updated_at`: Optional[datetime]

**Métodos:**
- `create()`: Factory method para crear artículos
- `mark_as_processed()`: Marcar artículo como procesado
- `update_content()`: Actualizar título y contenido
- `update_category()`: Actualizar categoría

### 2. Source (`src/domain/entities/source.py`)
**Campos:**
- `id`: UUID (generado automáticamente)
- `nombre`: str
- `dominio`: str
- `pais`: str
- `activo`: bool (default: True)
- `created_at`: datetime
- `updated_at`: Optional[datetime]

**Métodos:**
- `create()`: Factory method para crear fuentes
- `activate()`: Activar fuente
- `deactivate()`: Desactivar fuente
- `update_info()`: Actualizar información de la fuente

### 3. ScrapingJob (`src/domain/entities/scraping_job.py`)
**Campos:**
- `id`: UUID (generado automáticamente)
- `fuente`: str
- `fecha_inicio`: datetime
- `fecha_fin`: Optional[datetime]
- `status`: str (pending, running, completed, failed)
- `total_articulos`: int (default: 0)
- `created_at`: datetime
- `updated_at`: Optional[datetime]

**Métodos:**
- `create()`: Factory method para crear jobs
- `start()`: Iniciar job (status: running)
- `complete()`: Completar job (status: completed)
- `fail()`: Marcar job como fallido (status: failed)
- `increment_articles()`: Incrementar contador de artículos

## ✅ Interfaces de Repositorio Creadas

### 1. NewsArticleRepository (`src/domain/repositories/news_article_repository.py`)
**Métodos:**
- `create()`: Crear artículo
- `get_by_id()`: Obtener por ID
- `get_by_url()`: Obtener por URL
- `get_all()`: Listar todos con paginación
- `get_by_fuente()`: Filtrar por fuente
- `get_by_categoria()`: Filtrar por categoría
- `update()`: Actualizar artículo
- `delete()`: Eliminar artículo

### 2. SourceRepository (`src/domain/repositories/source_repository.py`)
**Métodos:**
- `create()`: Crear fuente
- `get_by_id()`: Obtener por ID
- `get_by_nombre()`: Obtener por nombre
- `get_by_dominio()`: Obtener por dominio
- `get_all()`: Listar todas con paginación
- `get_active_sources()`: Listar solo fuentes activas
- `update()`: Actualizar fuente
- `delete()`: Eliminar fuente

### 3. ScrapingJobRepository (`src/domain/repositories/scraping_job_repository.py`)
**Métodos:**
- `create()`: Crear job
- `get_by_id()`: Obtener por ID
- `get_all()`: Listar todos con paginación
- `get_by_fuente()`: Filtrar por fuente
- `get_by_status()`: Filtrar por estado
- `update()`: Actualizar job
- `delete()`: Eliminar job

## ✅ DTOs Creados

### 1. NewsArticle DTOs (`src/application/dto/news_article_dto.py`)
- `CreateNewsArticleDTO`: Para crear artículos
- `UpdateNewsArticleDTO`: Para actualizar artículos
- `NewsArticleDTO`: Respuesta con datos completos

### 2. Source DTOs (`src/application/dto/source_dto.py`)
- `CreateSourceDTO`: Para registrar fuentes
- `UpdateSourceDTO`: Para actualizar fuentes
- `SourceDTO`: Respuesta con datos completos

### 3. ScrapingJob DTOs (`src/application/dto/scraping_job_dto.py`)
- `CreateScrapingJobDTO`: Para crear jobs
- `ScrapingJobDTO`: Respuesta con datos completos

## ✅ Casos de Uso Implementados

### 1. CreateArticleUseCase (`src/application/use_cases/create_article.py`)
- Valida que el artículo no exista por URL
- Crea la entidad NewsArticle
- Persiste el artículo usando el repositorio
- Retorna DTO con los datos del artículo creado

### 2. ListArticlesUseCase (`src/application/use_cases/list_articles.py`)
- Lista artículos con paginación
- Convierte entidades a DTOs
- Retorna lista de NewsArticleDTO

### 3. RegisterSourceUseCase (`src/application/use_cases/register_source.py`)
- Valida que la fuente no exista por dominio
- Crea la entidad Source
- Persiste la fuente usando el repositorio
- Retorna DTO con los datos de la fuente creada

## ✅ Tests Unitarios

### Cobertura de Tests:
- ✅ `test_news_article_entity.py` (5 tests)
- ✅ `test_source_entity.py` (4 tests)
- ✅ `test_scraping_job_entity.py` (5 tests)

**Total: 14 nuevos tests creados**
**Estado: Todos los tests pasan (24/24 incluyendo tests existentes)**

## ✅ Características Implementadas

1. **Código Limpio y Tipado:**
   - Todas las clases usan type hints
   - Dataclasses para entidades y DTOs
   - Interfaces abstractas para repositorios

2. **Sin Dependencias Externas:**
   - Solo librerías estándar de Python
   - No hay dependencias de frameworks
   - Lógica de negocio pura

3. **Patrón Factory:**
   - Método `create()` en todas las entidades
   - Inicialización consistente con valores por defecto

4. **Inmutabilidad de IDs:**
   - IDs generados automáticamente con UUID
   - Timestamps automáticos (created_at, updated_at)

5. **Validación en Capas:**
   - Use cases validan duplicados
   - Entidades mantienen invariantes

6. **Documentación:**
   - Código auto-documentado con nombres claros
   - Exports organizados en `__init__.py`

## 📁 Archivos Creados

### Domain Layer
- `src/domain/entities/news_article.py`
- `src/domain/entities/source.py`
- `src/domain/entities/scraping_job.py`
- `src/domain/repositories/news_article_repository.py`
- `src/domain/repositories/source_repository.py`
- `src/domain/repositories/scraping_job_repository.py`

### Application Layer
- `src/application/dto/news_article_dto.py`
- `src/application/dto/source_dto.py`
- `src/application/dto/scraping_job_dto.py`
- `src/application/use_cases/create_article.py`
- `src/application/use_cases/list_articles.py`
- `src/application/use_cases/register_source.py`

### Tests
- `tests/unit/test_news_article_entity.py`
- `tests/unit/test_source_entity.py`
- `tests/unit/test_scraping_job_entity.py`

### Updated Files
- `src/domain/entities/__init__.py`
- `src/domain/repositories/__init__.py`
- `src/application/dto/__init__.py`
- `src/application/use_cases/__init__.py`

## 🎯 Objetivos Cumplidos

✅ Diseñar entidades de dominio (NewsArticle, Source, ScrapingJob)  
✅ Implementar casos de uso base (Create, List, Register)  
✅ Mantener dominio sin dependencias externas  
✅ Código limpio y tipado  
✅ Tests unitarios completos  
✅ Seguir arquitectura hexagonal  
✅ Patrones de diseño aplicados correctamente  
