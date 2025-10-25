# Guía de Uso

## Inicio Rápido

### 1. Instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

```bash
python main.py
```

O con make:
```bash
make run
```

La aplicación estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

## Ejemplos de API

### Health Check

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "app_name": "FastAPI Hexagonal App",
  "version": "1.0.0"
}
```

### Crear Usuario

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe"
  }'
```

Respuesta:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null,
  "is_active": true
}
```

### Obtener Usuario

```bash
curl http://localhost:8000/users/{user_id}
```

### Listar Usuarios

```bash
curl http://localhost:8000/users?skip=0&limit=10
```

### Actualizar Usuario

```bash
curl -X PUT http://localhost:8000/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe"
  }'
```

### Eliminar Usuario

```bash
curl -X DELETE http://localhost:8000/users/{user_id}
```

## Testing

### Ejecutar todos los tests

```bash
pytest
```

O con make:
```bash
make test
```

### Ejecutar tests con cobertura

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

O con make:
```bash
make test-cov
```

Esto generará un reporte HTML en `htmlcov/index.html`.

### Ejecutar tests específicos

```bash
# Tests unitarios solamente
pytest tests/unit/

# Tests de integración solamente
pytest tests/integration/

# Un archivo específico
pytest tests/unit/test_user_entity.py

# Una función específica
pytest tests/unit/test_user_entity.py::test_create_user
```

## Docker

### Construir imagen

```bash
docker-compose build
```

O con make:
```bash
make docker-build
```

### Iniciar contenedores

```bash
docker-compose up -d
```

O con make:
```bash
make docker-up
```

### Ver logs

```bash
docker-compose logs -f app
```

O con make:
```bash
make docker-logs
```

### Detener contenedores

```bash
docker-compose down
```

O con make:
```bash
make docker-down
```

## Estructura del Proyecto

```
.
├── src/
│   ├── domain/              # Lógica de negocio pura
│   │   ├── entities/        # Entidades del dominio
│   │   ├── value_objects/   # Objetos de valor inmutables
│   │   └── repositories/    # Interfaces de repositorios (puertos)
│   ├── application/         # Casos de uso
│   │   ├── use_cases/       # Implementación de casos de uso
│   │   └── dto/             # Data Transfer Objects
│   ├── infrastructure/      # Implementaciones técnicas
│   │   ├── persistence/     # Implementaciones de repositorios
│   │   ├── external_services/ # Integraciones externas
│   │   └── config/          # Configuración
│   └── presentation/        # Capa de presentación
│       ├── api/             # Endpoints REST
│       └── schemas/         # Schemas de validación
├── tests/
│   ├── unit/                # Tests unitarios
│   └── integration/         # Tests de integración
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias
└── README.md               # Documentación principal
```

## Agregar una Nueva Entidad

### 1. Crear la entidad en el dominio

```python
# src/domain/entities/product.py
from dataclasses import dataclass
from uuid import UUID

@dataclass
class Product:
    id: UUID
    name: str
    price: float
```

### 2. Crear el repositorio interface

```python
# src/domain/repositories/product_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.domain.entities.product import Product

class ProductRepository(ABC):
    @abstractmethod
    async def create(self, product: Product) -> Product:
        pass
```

### 3. Crear el caso de uso

```python
# src/application/use_cases/create_product.py
from src.domain.repositories.product_repository import ProductRepository

class CreateProductUseCase:
    def __init__(self, repository: ProductRepository):
        self._repository = repository
    
    async def execute(self, dto: CreateProductDTO) -> ProductDTO:
        # Lógica del caso de uso
        pass
```

### 4. Implementar el repositorio

```python
# src/infrastructure/persistence/in_memory_product_repository.py
class InMemoryProductRepository(ProductRepository):
    async def create(self, product: Product) -> Product:
        # Implementación
        pass
```

### 5. Crear los endpoints

```python
# src/presentation/api/routes/products.py
from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])

@router.post("")
async def create_product():
    pass
```

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
APP_NAME="FastAPI Hexagonal App"
APP_VERSION="1.0.0"
DEBUG=true
HOST=0.0.0.0
PORT=8000

DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## Comandos Útiles (Makefile)

```bash
make help          # Mostrar ayuda
make install       # Instalar dependencias
make run           # Ejecutar aplicación
make test          # Ejecutar tests
make test-cov      # Tests con cobertura
make clean         # Limpiar archivos cache
make docker-build  # Construir imagen Docker
make docker-up     # Iniciar contenedores
make docker-down   # Detener contenedores
```

## Próximos Pasos

1. **Implementar persistencia real**: Cambiar de InMemoryRepository a SQLAlchemy
2. **Agregar autenticación**: JWT, OAuth2
3. **Implementar logging**: Structured logging
4. **Agregar observabilidad**: Prometheus, Grafana
5. **CI/CD**: GitHub Actions, GitLab CI
6. **Documentación API**: OpenAPI enriquecida
7. **Rate limiting**: Protección contra abuso
8. **Caching**: Redis para mejorar performance
9. **Validaciones avanzadas**: Reglas de negocio complejas
10. **Event sourcing**: Si se necesita auditoría completa
