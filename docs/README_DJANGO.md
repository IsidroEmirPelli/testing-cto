# News Scraping System - Django + Arquitectura Hexagonal

Sistema de scraping de noticias implementado con Django y Django REST Framework, manteniendo una arquitectura hexagonal (clean architecture).

## 🏗️ Arquitectura

El proyecto sigue los principios de Clean Architecture / Arquitectura Hexagonal:

```
src/
├── domain/              # Capa de Dominio (núcleo - sin dependencias)
│   ├── entities/        # Entidades del dominio
│   ├── repositories/    # Interfaces de repositorios (puertos)
│   └── value_objects/   # Objetos de valor
├── application/         # Capa de Aplicación (casos de uso)
│   ├── dto/            # Data Transfer Objects
│   └── use_cases/      # Casos de uso del negocio
├── infrastructure/      # Capa de Infraestructura (adaptadores)
│   ├── config/         # Configuración de Django
│   └── persistence/    # Implementaciones de repositorios
│       ├── django_app/          # App Django (models)
│       └── django_repositories.py  # Adaptadores de repositorio
└── presentation/        # Capa de Presentación (API)
    └── django_app/     # Views, serializers, URLs de Django REST Framework
```

### Principios Aplicados

- ✅ **Separation of Concerns**: Cada capa tiene su responsabilidad específica
- ✅ **Dependency Inversion**: Las capas externas dependen de las internas
- ✅ **Domain Independence**: El dominio no conoce Django ni ningún framework
- ✅ **Repository Pattern**: Abstracción de la persistencia
- ✅ **Use Cases**: Lógica de negocio encapsulada
- ✅ **DTOs**: Transferencia de datos entre capas

## 🐳 Docker Setup

### Prerequisitos

- Docker
- Docker Compose

### Inicio Rápido

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Configurar entorno completo (build, migrate, up)
make dev-setup

# 3. Ver logs
make logs

# 4. Crear superusuario para el admin de Django
make createsuperuser
```

### Comandos Docker Disponibles

```bash
make help              # Ver todos los comandos disponibles
make build            # Construir imágenes
make up               # Levantar servicios
make down             # Detener servicios
make restart          # Reiniciar servicios
make logs             # Ver logs en tiempo real
make shell            # Abrir shell en el contenedor
make migrate          # Ejecutar migraciones
make makemigrations   # Crear nuevas migraciones
make test             # Ejecutar tests
make test-unit        # Ejecutar solo tests unitarios
make clean            # Limpiar contenedores y volúmenes
```

## 🚀 Uso

### Servicios Disponibles

Una vez levantado el sistema con `make up`:

- **API REST**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/
- **PostgreSQL**: localhost:5432

### Endpoints de la API

#### News Articles

```bash
# Listar artículos
GET http://localhost:8000/api/articles/?skip=0&limit=100

# Crear artículo
POST http://localhost:8000/api/articles/
{
  "titulo": "Título del artículo",
  "contenido": "Contenido completo...",
  "fuente": "elpais.com",
  "fecha_publicacion": "2024-01-01T12:00:00Z",
  "url": "https://elpais.com/article",
  "categoria": "Tecnología"
}
```

#### Sources

```bash
# Registrar fuente
POST http://localhost:8000/api/sources/
{
  "nombre": "El País",
  "dominio": "elpais.com",
  "pais": "España"
}
```

#### Users

```bash
# Listar usuarios
GET http://localhost:8000/api/users/?skip=0&limit=100

# Crear usuario
POST http://localhost:8000/api/users/
{
  "email": "user@example.com",
  "name": "User Name"
}
```

## 🧪 Tests

### Ejecutar Tests

```bash
# Todos los tests
make test

# Solo tests unitarios
make test-unit

# Con cobertura
make test-coverage
```

### Tests Implementados

- ✅ Tests unitarios de entidades del dominio
- ✅ Tests de casos de uso
- ✅ Tests de value objects
- Sin dependencias de framework en tests de dominio

## 📊 Base de Datos

### Migraciones

```bash
# Crear migraciones
make makemigrations

# Aplicar migraciones
make migrate

# Ver estado de migraciones
docker-compose exec web python manage.py showmigrations
```

### Modelos Django

Los modelos Django son **adaptadores** de la capa de infraestructura:

- `UserModel` → adapta `User` entity
- `SourceModel` → adapta `Source` entity  
- `NewsArticleModel` → adapta `NewsArticle` entity
- `ScrapingJobModel` → adapta `ScrapingJob` entity

**Importante**: Los modelos Django NO son las entidades del dominio. El dominio permanece puro y sin dependencias de Django.

## 🔧 Desarrollo Local (sin Docker)

```bash
# Crear virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración local

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Ejecutar tests
pytest
```

## 📝 Comandos Django Útiles

```bash
# Abrir shell de Django
docker-compose exec web python manage.py shell

# Crear app Django
docker-compose exec web python manage.py startapp nombre_app

# Limpiar sesiones
docker-compose exec web python manage.py clearsessions

# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic

# Verificar configuración
make check
```

## 🏭 Producción

### Variables de Entorno Requeridas

```bash
SECRET_KEY=<clave-secreta-segura>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
DATABASE_URL=postgresql://user:pass@host:5432/db
CORS_ALLOWED_ORIGINS=https://tu-frontend.com
```

### Consideraciones de Seguridad

- ✅ Cambiar `SECRET_KEY` en producción
- ✅ Establecer `DEBUG=False`
- ✅ Configurar `ALLOWED_HOSTS` correctamente
- ✅ Usar HTTPS
- ✅ Configurar CORS apropiadamente
- ✅ Usar contraseñas seguras para la base de datos

## 📚 Recursos

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

## 🤝 Contribuir

1. Las entidades del dominio NO deben importar nada de Django
2. Los casos de uso solo dependen del dominio
3. Los adaptadores (repositories) implementan las interfaces del dominio
4. La capa de presentación (views) orquesta llamadas a casos de uso
5. Mantener tests unitarios puros sin dependencias de framework

## 📄 Licencia

[Tu licencia aquí]
