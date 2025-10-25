# Migración a Django - Manteniendo Arquitectura Hexagonal

Este documento explica cómo se migró el proyecto de FastAPI a Django manteniendo la arquitectura hexagonal.

## 🎯 Objetivos de la Migración

1. ✅ Migrar de FastAPI a Django + Django REST Framework
2. ✅ Mantener la arquitectura hexagonal intacta
3. ✅ Preservar el dominio puro (sin dependencias de framework)
4. ✅ Dockerizar completamente el proyecto
5. ✅ Configurar PostgreSQL como base de datos

## 📦 Cambios Realizados

### 1. Dependencias (`requirements.txt`)

**Antes (FastAPI):**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
```

**Después (Django):**
```
Django==4.2.8
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-environ==0.11.2
gunicorn==21.2.0
```

### 2. Configuración de Django

**Archivos nuevos:**
- `src/infrastructure/config/django_settings.py` - Configuración de Django
- `src/infrastructure/config/wsgi.py` - WSGI application
- `src/infrastructure/config/asgi.py` - ASGI application
- `manage.py` - CLI de Django

**Características:**
- Configuración basada en variables de entorno
- Soporte para CORS
- PostgreSQL como base de datos
- Logging configurado
- Static files con WhiteNoise

### 3. Capa de Persistencia

**Modelos Django (`src/infrastructure/persistence/django_app/models.py`):**
```python
class NewsArticleModel(models.Model):
    # Adaptador de la entidad NewsArticle
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    titulo = models.CharField(max_length=500)
    contenido = models.TextField()
    # ... más campos
```

**Repositorios Django (`src/infrastructure/persistence/django_repositories.py`):**
```python
class DjangoNewsArticleRepository(NewsArticleRepository):
    # Implementa la interfaz del dominio usando Django ORM
    
    def _to_entity(self, model: NewsArticleModel) -> NewsArticle:
        # Convierte modelo Django → entidad dominio
        
    def _to_model(self, entity: NewsArticle) -> NewsArticleModel:
        # Convierte entidad dominio → modelo Django
```

### 4. Capa de Presentación

**Serializers (`src/presentation/django_app/serializers.py`):**
```python
class NewsArticleCreateSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=500)
    contenido = serializers.CharField()
    # Validación de entrada
```

**Views (`src/presentation/django_app/views.py`):**
```python
class NewsArticleListCreateView(APIView):
    def post(self, request):
        # 1. Validar entrada con serializer
        # 2. Crear DTO
        # 3. Ejecutar caso de uso
        # 4. Retornar respuesta serializada
```

### 5. Dockerización

**Dockerfile:**
- Python 3.11 slim
- PostgreSQL dependencies
- Gunicorn como servidor WSGI
- Collectstatic automático

**docker-compose.yml:**
- Servicio `web`: Django application
- Servicio `db`: PostgreSQL 15
- Health checks configurados
- Volúmenes para persistencia
- Migraciones automáticas al inicio

### 6. Makefile

Comandos simplificados para desarrollo:
```bash
make dev-setup      # Setup completo
make up            # Levantar servicios
make logs          # Ver logs
make migrate       # Ejecutar migraciones
make test          # Ejecutar tests
```

## 🔍 Arquitectura Preservada

### Dominio (Sin Cambios)

La capa de dominio **NO FUE MODIFICADA**:

```python
# src/domain/entities/news_article.py
# EXACTAMENTE IGUAL - sin imports de Django
@dataclass
class NewsArticle:
    id: UUID
    titulo: str
    # ... sin dependencias externas
    
    @classmethod
    def create(cls, ...):
        # Lógica de negocio pura
```

### Casos de Uso (Sin Cambios)

Los casos de uso permanecen idénticos:

```python
# src/application/use_cases/create_article.py
# EXACTAMENTE IGUAL
class CreateArticleUseCase:
    def __init__(self, article_repository: NewsArticleRepository):
        # Depende de interfaz, no de implementación
```

### Adaptadores (Nuevos)

Solo cambió la implementación de los repositorios:

```python
# ANTES: InMemoryUserRepository
# AHORA: DjangoUserRepository

# Ambos implementan la misma interfaz: UserRepository
```

## 🔄 Flujo de Datos

```
HTTP Request
    ↓
Django View (Presentación)
    ↓
Serializer (Validación)
    ↓
DTO (Transferencia)
    ↓
Use Case (Aplicación)
    ↓
Domain Entity (Dominio)
    ↓
Repository Interface (Dominio)
    ↓
Django Repository (Infraestructura)
    ↓
Django Model (Infraestructura)
    ↓
PostgreSQL
```

## ✅ Beneficios de la Arquitectura Hexagonal

1. **Cambio de Framework sin modificar el dominio**
   - El dominio sigue puro
   - Los casos de uso no cambiaron
   - Solo se reemplazaron adaptadores

2. **Testabilidad**
   - Tests unitarios del dominio siguen funcionando
   - No dependen de Django
   - Mocks fáciles de crear

3. **Flexibilidad**
   - Podríamos cambiar de Django a otro framework nuevamente
   - Podríamos usar múltiples adaptadores (Django + MongoDB)
   - Fácil añadir nuevas interfaces (GraphQL, gRPC)

4. **Mantenibilidad**
   - Separación clara de responsabilidades
   - Código organizado por capas
   - Fácil de entender y navegar

## 🚀 Próximos Pasos Sugeridos

1. **Implementar Celery para scraping asíncrono**
   - Mantener en capa de infraestructura
   - Usar casos de uso existentes

2. **Añadir autenticación JWT**
   - Middleware en capa de presentación
   - No afecta dominio ni casos de uso

3. **Implementar caché con Redis**
   - Decorador en adaptadores de repositorio
   - Transparente para casos de uso

4. **Añadir más endpoints REST**
   - Solo en capa de presentación
   - Reusar casos de uso existentes

5. **Implementar scraping real**
   - Nueva capa de servicios externos
   - Orquestado por casos de uso

## 📚 Referencias

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)

## 🎓 Lecciones Aprendidas

1. **La arquitectura hexagonal realmente funciona**
   - Pudimos cambiar el framework sin tocar el dominio
   - Los tests unitarios siguieron pasando

2. **Los adaptadores son clave**
   - Aíslan las dependencias externas
   - Facilitan el testing

3. **DTOs son esenciales**
   - Separan la API de las entidades
   - Permiten evolucionar independientemente

4. **Las interfaces (Repositories) son contratos**
   - Permiten múltiples implementaciones
   - Inversion of Dependency en acción
