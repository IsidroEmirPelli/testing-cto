# 📡 Ejemplos de Uso de la API

## 🚀 Inicio Rápido

```bash
# Levantar servicios
make dev-setup

# Verificar que está funcionando
curl http://localhost:8000/health/
```

## 📋 Endpoints Disponibles

### Health Check

```bash
curl -X GET http://localhost:8000/health/
```

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "News Scraping API",
  "architecture": "Hexagonal (Clean Architecture)"
}
```

---

## 📰 News Articles

### Crear un Artículo

```bash
curl -X POST http://localhost:8000/api/articles/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "España gana el Mundial de Fútbol 2024",
    "contenido": "En un emocionante partido disputado en...",
    "fuente": "elpais.com",
    "fecha_publicacion": "2024-01-15T18:30:00Z",
    "url": "https://elpais.com/deportes/2024/mundial",
    "categoria": "Deportes"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "titulo": "España gana el Mundial de Fútbol 2024",
  "contenido": "En un emocionante partido disputado en...",
  "fuente": "elpais.com",
  "fecha_publicacion": "2024-01-15T18:30:00.000000Z",
  "url": "https://elpais.com/deportes/2024/mundial",
  "categoria": "Deportes",
  "procesado": false,
  "created_at": "2024-01-15T20:00:00.000000Z",
  "updated_at": null
}
```

**Error si ya existe (400):**
```json
{
  "error": "Article with URL https://elpais.com/deportes/2024/mundial already exists"
}
```

### Listar Artículos

```bash
# Sin paginación (primeros 100)
curl -X GET http://localhost:8000/api/articles/

# Con paginación
curl -X GET "http://localhost:8000/api/articles/?skip=0&limit=10"

# Siguiente página
curl -X GET "http://localhost:8000/api/articles/?skip=10&limit=10"
```

**Respuesta:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "titulo": "España gana el Mundial de Fútbol 2024",
    "contenido": "En un emocionante partido...",
    "fuente": "elpais.com",
    "fecha_publicacion": "2024-01-15T18:30:00.000000Z",
    "url": "https://elpais.com/deportes/2024/mundial",
    "categoria": "Deportes",
    "procesado": false,
    "created_at": "2024-01-15T20:00:00.000000Z",
    "updated_at": null
  }
]
```

---

## 🌍 Sources (Fuentes)

### Registrar una Fuente

```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "El País",
    "dominio": "elpais.com",
    "pais": "España"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "id": "987e6543-e21b-12d3-a456-426614174111",
  "nombre": "El País",
  "dominio": "elpais.com",
  "pais": "España",
  "activo": true,
  "created_at": "2024-01-15T20:00:00.000000Z",
  "updated_at": null
}
```

**Error si ya existe (400):**
```json
{
  "error": "Source with domain elpais.com already exists"
}
```

### Más Ejemplos de Fuentes

```bash
# El Mundo
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "El Mundo",
    "dominio": "elmundo.es",
    "pais": "España"
  }'

# BBC News
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "BBC News",
    "dominio": "bbc.com",
    "pais": "Reino Unido"
  }'

# CNN
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "CNN",
    "dominio": "cnn.com",
    "pais": "Estados Unidos"
  }'
```

---

## 👥 Users (Usuarios)

### Crear un Usuario

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "name": "Juan Pérez"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "id": "456e7890-e12b-34d5-a678-426614174222",
  "email": "usuario@example.com",
  "name": "Juan Pérez",
  "is_active": true,
  "created_at": "2024-01-15T20:00:00.000000Z",
  "updated_at": null
}
```

**Error si ya existe (400):**
```json
{
  "error": "User with email usuario@example.com already exists"
}
```

### Listar Usuarios

```bash
# Todos los usuarios
curl -X GET http://localhost:8000/api/users/

# Con paginación
curl -X GET "http://localhost:8000/api/users/?skip=0&limit=10"
```

**Respuesta:**
```json
[
  {
    "id": "456e7890-e12b-34d5-a678-426614174222",
    "email": "usuario@example.com",
    "name": "Juan Pérez",
    "is_active": true,
    "created_at": "2024-01-15T20:00:00.000000Z",
    "updated_at": null
  }
]
```

---

## 🔧 Ejemplos con Python

### Usando requests

```python
import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

# 1. Verificar salud
response = requests.get(f"{BASE_URL}/health/")
print(response.json())

# 2. Crear fuente
source_data = {
    "nombre": "El País",
    "dominio": "elpais.com",
    "pais": "España"
}
response = requests.post(f"{BASE_URL}/api/sources/", json=source_data)
print(f"Fuente creada: {response.json()}")

# 3. Crear artículo
article_data = {
    "titulo": "Nueva tecnología revoluciona la industria",
    "contenido": "Una innovación sin precedentes...",
    "fuente": "elpais.com",
    "fecha_publicacion": datetime.now(timezone.utc).isoformat(),
    "url": "https://elpais.com/tecnologia/nueva-tech",
    "categoria": "Tecnología"
}
response = requests.post(f"{BASE_URL}/api/articles/", json=article_data)
print(f"Artículo creado: {response.json()}")

# 4. Listar artículos
response = requests.get(f"{BASE_URL}/api/articles/", params={"limit": 10})
print(f"Artículos: {len(response.json())} encontrados")

# 5. Crear usuario
user_data = {
    "email": "desarrollador@example.com",
    "name": "María García"
}
response = requests.post(f"{BASE_URL}/api/users/", json=user_data)
print(f"Usuario creado: {response.json()}")
```

---

## 🐳 Ejemplos con Docker

### Usando el contenedor

```bash
# Ejecutar curl desde el contenedor web
docker-compose exec web curl http://localhost:8000/health/

# Crear artículo desde el contenedor
docker-compose exec web curl -X POST http://localhost:8000/api/articles/ \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Test","contenido":"Content","fuente":"test.com","fecha_publicacion":"2024-01-01T12:00:00Z","url":"https://test.com/1"}'
```

---

## 🔐 Admin de Django

Accede a http://localhost:8000/admin/ con:
- **Usuario**: admin
- **Contraseña**: admin123

Desde el admin puedes:
- Ver y editar todos los datos
- Filtrar y buscar
- Ver estadísticas
- Ejecutar acciones en lote

---

## 🧪 Probar desde el Shell de Django

```bash
# Entrar al shell
make shell

# Dentro del contenedor
python manage.py shell
```

```python
# Crear datos de prueba
from src.domain.entities import NewsArticle, Source
from src.infrastructure.persistence.django_app.models import NewsArticleModel, SourceModel
from datetime import datetime, timezone
from asgiref.sync import sync_to_async

# Crear fuente
source = Source.create(
    nombre="Test Source",
    dominio="test.com",
    pais="Test Country"
)

# Crear artículo
article = NewsArticle.create(
    titulo="Test Article",
    contenido="Test Content",
    fuente="test.com",
    fecha_publicacion=datetime.now(timezone.utc),
    url="https://test.com/article-1",
    categoria="Test"
)

print(f"Article created: {article.id}")
```

---

## 📊 Queries Útiles

### Verificar datos en la base de datos

```bash
# Conectar a PostgreSQL
docker-compose exec db psql -U newsuser -d newsdb

# Queries útiles
SELECT COUNT(*) FROM news_articles;
SELECT COUNT(*) FROM sources;
SELECT * FROM sources WHERE activo = true;
SELECT * FROM news_articles WHERE procesado = false LIMIT 10;
```

---

## 🚨 Manejo de Errores

### Error 400 - Bad Request

```json
{
  "titulo": ["This field is required."],
  "url": ["Enter a valid URL."]
}
```

### Error 400 - Duplicado

```json
{
  "error": "Article with URL https://example.com already exists"
}
```

### Error 404 - Not Found

```json
{
  "detail": "Not found."
}
```

### Error 500 - Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## 💡 Tips

1. **Validación de URLs**: Deben ser URLs válidas
2. **Fechas**: Usar formato ISO 8601 con timezone (Z o +00:00)
3. **Paginación**: Default limit es 100, máximo recomendado 1000
4. **IDs**: Son UUIDs, no integers
5. **Campos opcionales**: categoria puede ser null

---

## 📚 Más Información

- Ver `README_DJANGO.md` para más detalles
- Ver `DJANGO_MIGRATION_SUMMARY.md` para arquitectura
- Usar `make help` para ver todos los comandos disponibles
