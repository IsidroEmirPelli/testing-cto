# Arquitectura Hexagonal (Puertos y Adaptadores)

## Descripción General

Este proyecto implementa una arquitectura hexagonal completa, también conocida como arquitectura de puertos y adaptadores. Esta arquitectura fue propuesta por Alistair Cockburn y tiene como objetivo aislar la lógica de negocio de las dependencias externas.

## Principios de Clean Code Aplicados

### 1. Single Responsibility Principle (SRP)
Cada clase tiene una única responsabilidad:
- **Entidades**: Encapsulan la lógica de negocio del dominio
- **Casos de Uso**: Orquestan un flujo específico de negocio
- **Repositorios**: Gestionan la persistencia
- **Controllers**: Manejan las peticiones HTTP

### 2. Dependency Inversion Principle (DIP)
Las capas externas dependen de las internas:
- Los casos de uso dependen de interfaces (puertos) no de implementaciones
- Las implementaciones (adaptadores) dependen de las interfaces definidas en el dominio

### 3. Open/Closed Principle (OCP)
El código está abierto a extensión pero cerrado a modificación:
- Nuevas implementaciones de repositorios pueden añadirse sin modificar el dominio
- Nuevos casos de uso pueden crearse sin modificar entidades existentes

### 4. Names Should Reveal Intent
Nombres claros y descriptivos:
- `CreateUserUseCase` describe claramente su propósito
- `UserRepository` indica que gestiona la persistencia de usuarios
- `Email` es un value object que encapsula validación

### 5. Functions Should Do One Thing
Cada función tiene una única responsabilidad:
- `create()`: Solo crea un usuario
- `_to_dto()`: Solo convierte entre tipos
- `_is_valid()`: Solo valida

## Capas de la Arquitectura

### 1. Domain (Dominio) - Núcleo de Negocio

**Responsabilidad**: Contiene las reglas de negocio puras, sin dependencias externas.

**Componentes**:
- **Entities**: Objetos con identidad única (User)
- **Value Objects**: Objetos inmutables sin identidad (Email)
- **Repository Interfaces**: Puertos que definen contratos

**Reglas**:
- ❌ NO debe depender de ninguna otra capa
- ❌ NO debe conocer frameworks o librerías externas
- ✅ Solo contiene lógica de negocio pura
- ✅ Define interfaces que otras capas implementarán

**Ejemplo**:
```python
class User:
    def create(cls, email: str, name: str) -> "User":
        # Lógica de negocio pura
        pass
```

### 2. Application (Aplicación) - Casos de Uso

**Responsabilidad**: Orquesta el flujo de datos entre el dominio y las capas externas.

**Componentes**:
- **Use Cases**: Implementan casos de uso específicos
- **DTOs**: Objetos de transferencia de datos

**Reglas**:
- ✅ Depende solo del dominio
- ✅ Define la lógica de aplicación
- ❌ NO contiene lógica de negocio del dominio
- ❌ NO conoce detalles de infraestructura

**Ejemplo**:
```python
class CreateUserUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository
    
    async def execute(self, dto: CreateUserDTO) -> UserDTO:
        # Orquesta el flujo
        pass
```

### 3. Infrastructure (Infraestructura) - Adaptadores

**Responsabilidad**: Implementa los detalles técnicos y las dependencias externas.

**Componentes**:
- **Persistence**: Implementaciones de repositorios
- **External Services**: Integraciones con APIs externas
- **Config**: Configuración de la aplicación

**Reglas**:
- ✅ Implementa las interfaces del dominio
- ✅ Maneja detalles técnicos (bases de datos, APIs, etc.)
- ✅ Puede depender de frameworks y librerías
- ❌ NO debe ser conocida por el dominio

**Ejemplo**:
```python
class InMemoryUserRepository(UserRepository):
    async def create(self, user: User) -> User:
        # Implementación específica
        pass
```

### 4. Presentation (Presentación) - API/UI

**Responsabilidad**: Expone la funcionalidad a través de interfaces (REST API, GraphQL, CLI, etc.).

**Componentes**:
- **API**: Endpoints y routers
- **Schemas**: Validación y serialización de datos
- **Dependencies**: Inyección de dependencias

**Reglas**:
- ✅ Traduce peticiones externas a DTOs
- ✅ Traduce respuestas del dominio a schemas
- ✅ Maneja aspectos HTTP (status codes, headers)
- ❌ NO contiene lógica de negocio

**Ejemplo**:
```python
@router.post("/users")
async def create_user(
    data: UserCreateSchema,
    use_case: CreateUserUseCase = Depends()
):
    dto = CreateUserDTO(email=data.email, name=data.name)
    return await use_case.execute(dto)
```

## Flujo de Datos

```
1. Request HTTP → 2. API Endpoint → 3. Use Case → 4. Domain Entity → 5. Repository
                                                                            ↓
6. Response HTTP ← 7. Schema ← 8. DTO ← 9. Domain Entity ← 10. Repository Implementation
```

### Ejemplo Completo: Crear Usuario

```
1. POST /users
   ↓
2. users.create_user(UserCreateSchema)
   ↓
3. CreateUserUseCase.execute(CreateUserDTO)
   ↓
4. User.create(email, name)
   ↓
5. user_repository.create(user)
   ↓
6. InMemoryUserRepository.create(user)
   ↓
7. Return User entity
   ↓
8. Convert to UserDTO
   ↓
9. Convert to UserResponseSchema
   ↓
10. Return HTTP 201 + JSON
```

## Ventajas de esta Arquitectura

### 1. Testabilidad
- Cada capa puede testearse independientemente
- Los mocks son fáciles de crear gracias a las interfaces
- Tests unitarios rápidos sin dependencias externas

### 2. Mantenibilidad
- Cambios en la UI no afectan la lógica de negocio
- Cambios en la base de datos no afectan el dominio
- Código organizado y fácil de navegar

### 3. Flexibilidad
- Fácil cambiar de base de datos (SQL → NoSQL)
- Fácil cambiar de framework (FastAPI → Flask)
- Fácil añadir nuevas interfaces (REST → GraphQL)

### 4. Independencia
- La lógica de negocio no depende de frameworks
- El dominio es completamente portable
- Las decisiones técnicas se posponen

## Patrones Utilizados

### 1. Repository Pattern
Abstrae la persistencia de datos:
```python
class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
```

### 2. Dependency Injection
Las dependencias se inyectan, no se crean:
```python
def __init__(self, repository: UserRepository):
    self._repository = repository
```

### 3. DTO Pattern
Transfiere datos entre capas:
```python
@dataclass
class CreateUserDTO:
    email: str
    name: str
```

### 4. Factory Pattern
Crea instancias con lógica compleja:
```python
@classmethod
def create(cls, email: str, name: str) -> "User":
    return cls(id=uuid4(), email=email, name=name, ...)
```

## Testing Strategy

### Unit Tests
Testean componentes individuales:
- Entidades del dominio
- Value objects
- Casos de uso (con repositorios mockeados)

### Integration Tests
Testean la integración entre capas:
- API endpoints
- Flujos completos
- Repositorios con base de datos real

## Extensibilidad

### Añadir una nueva entidad
1. Crear entidad en `domain/entities/`
2. Crear repositorio interface en `domain/repositories/`
3. Crear casos de uso en `application/use_cases/`
4. Implementar repositorio en `infrastructure/persistence/`
5. Crear endpoints en `presentation/api/routes/`

### Cambiar implementación de repositorio
1. Crear nueva clase en `infrastructure/persistence/`
2. Implementar interface `UserRepository`
3. Actualizar `dependencies.py` para usar nueva implementación
4. ¡El resto del código no cambia!

## Mejores Prácticas

1. **Nunca saltarse capas**: Siempre seguir el flujo correcto
2. **Interfaces sobre implementaciones**: Depender de abstracciones
3. **Un caso de uso, una responsabilidad**: Cada use case hace una cosa
4. **DTOs para transferencia**: No exponer entidades del dominio
5. **Validación en múltiples niveles**: Value objects, schemas, use cases
6. **Nombres descriptivos**: El código debe ser auto-documentado
7. **Tests primero**: TDD cuando sea posible
8. **Commits atómicos**: Un cambio, un commit
