# FastAPI Hexagonal Architecture

Una aplicación base de FastAPI siguiendo los principios de Clean Code y arquitectura hexagonal.

## 🏗️ Arquitectura

Este proyecto implementa la arquitectura hexagonal (puertos y adaptadores) con las siguientes capas:

```
src/
├── domain/              # Capa de dominio (núcleo de negocio)
│   ├── entities/        # Entidades del dominio
│   ├── value_objects/   # Objetos de valor
│   └── repositories/    # Interfaces de repositorios (puertos)
├── application/         # Capa de aplicación
│   ├── use_cases/       # Casos de uso
│   └── dto/             # Data Transfer Objects
├── infrastructure/      # Capa de infraestructura (adaptadores)
│   ├── persistence/     # Implementaciones de repositorios
│   ├── external_services/ # Servicios externos
│   └── config/          # Configuración
└── presentation/        # Capa de presentación
    ├── api/             # Endpoints de API
    └── schemas/         # Schemas de Pydantic
```

## 🚀 Instalación

1. Clona el repositorio
2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita .env con tus configuraciones
```

## 🏃 Ejecución

```bash
python main.py
```

O con uvicorn directamente:
```bash
uvicorn src.presentation.api.main:app --reload
```

La aplicación estará disponible en: http://localhost:8000
Documentación interactiva en: http://localhost:8000/docs

## 🧪 Testing

```bash
pytest
```

Con cobertura:
```bash
pytest --cov=src --cov-report=html
```

## 📋 Principios de Clean Code

- **Single Responsibility Principle**: Cada clase tiene una única responsabilidad
- **Dependency Inversion**: Las capas externas dependen de las internas
- **Separation of Concerns**: Cada capa tiene responsabilidades bien definidas
- **Explicit is better than implicit**: Código claro y legible
- **Names should reveal intent**: Nombres descriptivos y significativos

## 🔌 Puertos y Adaptadores

- **Puertos**: Interfaces definidas en la capa de dominio
- **Adaptadores**: Implementaciones concretas en la capa de infraestructura

Esta arquitectura permite cambiar fácilmente las implementaciones sin afectar el núcleo del negocio.
