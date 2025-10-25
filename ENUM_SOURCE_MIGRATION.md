# Migración de Fuentes a ENUM

## Resumen del Cambio

Se ha refactorizado el sistema de fuentes de noticias para utilizar un ENUM en lugar de campos manuales. Esto elimina la necesidad de insertar manualmente tanto el dominio como el nombre de cada fuente.

## Cambios Principales

### 1. Nuevo ENUM: NewsSource

Se creó un enum `NewsSource` en `src/domain/enums/source_enum.py` que define todas las fuentes disponibles:

- **CLARIN** - Clarín (www.clarin.com)
- **LA_NACION** - La Nación (www.lanacion.com.ar)
- **PAGINA12** - Página 12 (www.pagina12.com.ar)
- **INFOBAE** - Infobae (www.infobae.com)

El enum utiliza `auto()` para generar automáticamente los valores, evitando problemas en migraciones futuras.

### 2. Entidad Source Actualizada

La entidad `Source` ahora:
- Almacena un `source_type: NewsSource` en lugar de campos individuales
- Proporciona propiedades `nombre`, `dominio` y `pais` que obtienen los valores del enum
- Tiene métodos simplificados:
  - `Source.create(source_type: NewsSource)` - Crea una fuente desde el enum
  - `Source.create_from_nombre(nombre: str)` - Crea una fuente desde su nombre

### 3. Modelo Django Actualizado

El modelo `SourceModel` ahora:
- Usa `source_type: IntegerField` con choices basadas en el enum
- El campo `source_type` es único (solo puede haber una instancia de cada fuente)
- Se eliminaron los campos `nombre`, `dominio` y `pais` de la base de datos

### 4. Migración de Base de Datos

Se creó la migración `0002_change_source_to_enum.py` que:
- Elimina los campos antiguos (nombre, dominio, pais)
- Agrega el nuevo campo `source_type`
- Actualiza los índices de la base de datos

**Nota:** Esta migración elimina los datos existentes de fuentes. Después de aplicar la migración, ejecutar el script de inicialización.

## Cómo Usar

### Crear una Fuente

```python
from src.domain.entities import Source
from src.domain.enums import NewsSource

# Método 1: Desde el enum directamente
source = Source.create(source_type=NewsSource.CLARIN)

# Método 2: Desde el nombre
source = Source.create_from_nombre("Clarín")

# Acceder a las propiedades
print(source.nombre)   # "Clarín"
print(source.dominio)  # "www.clarin.com"
print(source.pais)     # "Argentina"
```

### API REST

Para crear una fuente vía API:

```bash
POST /api/sources/
Content-Type: application/json

{
  "source_type": "CLARIN"
}
```

Opciones válidas para `source_type`: `CLARIN`, `LA_NACION`, `PAGINA12`, `INFOBAE`

### Script de Inicialización

Para poblar la base de datos con todas las fuentes predefinidas:

```bash
python scripts/init_sources.py
```

Este script:
- Verifica todas las fuentes disponibles en el enum
- Crea las que no existen en la base de datos
- Muestra el estado de cada fuente

## Aplicar la Migración

```bash
# 1. Aplicar la migración de base de datos
python manage.py migrate

# 2. Inicializar las fuentes
python scripts/init_sources.py
```

## Beneficios

1. **No hay errores tipográficos**: Los nombres y dominios están predefinidos
2. **Autocompletado en IDE**: El enum proporciona sugerencias automáticas
3. **Validación en tiempo de compilación**: Los errores se detectan antes de ejecutar
4. **Consistencia**: Una única fuente de verdad para las fuentes disponibles
5. **Fácil de extender**: Agregar nuevas fuentes es tan simple como añadir un valor al enum
6. **Sin duplicados**: El campo `source_type` es único en la base de datos

## Migración para Nuevas Fuentes

Para agregar una nueva fuente:

1. Agregar el valor al enum en `src/domain/enums/source_enum.py`:
   ```python
   class NewsSource(Enum):
       # ... fuentes existentes ...
       NUEVA_FUENTE = auto()
   ```

2. Agregar la configuración en los métodos del enum:
   ```python
   @property
   def nombre(self) -> str:
       nombres = {
           # ... fuentes existentes ...
           NewsSource.NUEVA_FUENTE: "Nombre de la Fuente",
       }
       return nombres[self]
   ```

3. Hacer lo mismo para `dominio` y si es necesario para `pais`

4. Ejecutar `python scripts/init_sources.py` para crear la fuente en la BD

## Formato de Código

Todo el proyecto ha sido formateado con Black para mantener consistencia en el estilo del código:

```bash
black . --exclude venv
```
