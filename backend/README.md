# Backend - Argentum API

API REST construida con FastAPI siguiendo Clean Architecture para el sistema de tracking de cotizaciones de acciones argentinas.

## Stack Tecnológico

- **Framework**: FastAPI >= 0.124.4
- **Python**: 3.14+
- **Package Manager**: uv
- **ORM**: SQLAlchemy >= 2.0.45 (async)
- **Database**: PostgreSQL 18.1 (asyncpg driver)
- **Migrations**: Alembic >= 1.14.0
- **Authentication**: JWT (PyJWT >= 2.10.1)
- **Password Hashing**: bcrypt >= 5.0.0
- **Configuration**: pydantic-settings >= 2.12.0
- **Logging**: structlog >= 25.5.0
- **Testing**: pytest >= 9.0.2 + pytest-asyncio >= 1.3.0
- **Code Quality**: ruff >= 0.14.9

## Arquitectura

El backend implementa **Clean Architecture / Arquitectura Hexagonal**, separando el código en 4 capas principales:

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION                            │
│         FastAPI routes, schemas, middleware                 │
│              (main.py, api/routes/, api/schemas/)           │
├─────────────────────────────────────────────────────────────┤
│                     APPLICATION                             │
│         Use cases, DTOs, Service interfaces                 │
│        (use_cases/, dtos/, interfaces/)                     │
├─────────────────────────────────────────────────────────────┤
│                       DOMAIN                                │
│   Entities, Value Objects, Repository interfaces           │
│   (entities/, value_objects/, repositories/)                │
├─────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE                            │
│   PostgreSQL, SQLAlchemy, Repository implementations       │
│   (database/, repositories/, services/)                     │
└─────────────────────────────────────────────────────────────┘
```

### Principios de Clean Architecture

1. **Dependency Inversion**: Las capas externas dependen de las internas, nunca al revés
2. **Domain no tiene dependencias**: La lógica de negocio es independiente
3. **Interfaces en Application**: Los servicios se definen como interfaces
4. **Implementaciones en Infrastructure**: Las interfaces se implementan aquí
5. **Dependency Injection**: Todo se conecta en Presentation

### Estructura del Proyecto

```
backend/
├── domain/                          # Capa de dominio (lógica de negocio)
│   ├── entities/
│   │   ├── base.py                 # BaseEntity (UUID, timestamps)
│   │   └── user.py                 # User entity con lógica de negocio
│   ├── repositories/
│   │   └── user_repository.py      # Interface UserRepository (ABC)
│   ├── exceptions/
│   │   ├── user_exceptions.py      # UserAlreadyExistsError, UserNotFoundError
│   │   └── token_exceptions.py     # ExpiredTokenError, InvalidTokenError
│   └── value_objects/
│       ├── email.py                # Email value object con validación
│       └── password.py             # HashedPassword, PlainPassword
│
├── application/                     # Casos de uso
│   ├── use_cases/
│   │   ├── register_user.py        # RegisterUser use case
│   │   └── login_user.py           # LoginUser use case
│   ├── dtos/
│   │   └── auth_dtos.py            # RegisterUserDTO, UserResponseDTO, LoginDTO, TokenDTO
│   └── interfaces/
│       ├── hash_service.py         # Interface HashService (ABC)
│       └── token_service.py        # Interface TokenService (ABC)
│
├── infrastructure/                  # Implementaciones técnicas
│   ├── database/
│   │   ├── connection.py           # AsyncEngine + SessionLocal
│   │   └── models.py               # UserModel (SQLAlchemy)
│   ├── repositories/
│   │   └── postgres_user_repository.py  # Implementación PostgreSQL
│   ├── services/
│   │   ├── hash_service.py         # BcryptHashService
│   │   └── jwt_token_service.py    # JWTTokenService
│   └── logging/
│       └── setup.py                # Configuración structlog
│
├── presentation/                    # API REST
│   ├── config.py                   # Settings con pydantic-settings
│   └── api/
│       ├── routes/
│       │   └── auth.py             # Endpoints: /register, /login, /me
│       ├── schemas/
│       │   └── auth_schemas.py     # Pydantic schemas para validación
│       ├── dependencies/
│       │   └── auth.py             # Dependency injection
│       └── middleware/
│           └── request_id.py       # Request ID middleware
│
├── alembic/                         # Migraciones de base de datos
│   ├── versions/
│   │   ├── f0886c6a3ba1_create_users_table.py
│   │   ├── ca722952e486_add_index_on_username_field.py
│   │   └── 95584c0e0794_change_timestamps_to_timezone_aware.py
│   ├── env.py                      # Config Alembic async
│   └── script.py.mako
│
├── tests/                           # 125 tests totales
│   ├── conftest.py                 # Fixtures compartidos
│   ├── domain/
│   │   └── test_user_entity.py     # 25 tests
│   ├── application/
│   │   ├── test_register_user.py   # 8 tests
│   │   └── test_login_user.py      # 9 tests
│   ├── infrastructure/
│   │   ├── test_hash_service.py    # 16 tests
│   │   ├── test_jwt_token_service.py  # 21 tests
│   │   └── test_postgres_user_repository.py  # 17 tests
│   └── presentation/
│       └── api/
│           ├── test_auth_endpoints.py  # 17 tests
│           └── middleware/
│               └── test_request_id.py  # 12 tests
│
├── scripts/
│   ├── clean.sh                    # Limpiar cache
│   ├── format.sh                   # Formatear código
│   └── lint.sh                     # Linter
│
├── main.py                         # Entry point FastAPI
├── pyproject.toml                  # Dependencias y config
├── uv.lock                         # Lockfile
├── alembic.ini                     # Config Alembic
├── .env                            # Variables de entorno (no commiteado)
├── .env.example                    # Template de variables
├── .python-version                 # Python 3.14
└── README.md
```

## Setup

### Prerrequisitos

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) - Python package manager
- PostgreSQL 18+ (o Docker)

### Instalación

```bash
# 1. Instalar dependencias
cd backend
uv sync

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración

# 3. Iniciar PostgreSQL (opción Docker)
cd ..
docker compose up -d postgres

# 4. Ejecutar migraciones
uv run alembic upgrade head

# 5. Iniciar servidor de desarrollo
uv run fastapi dev main.py
```

El servidor estará disponible en `http://localhost:8000`

### Variables de Entorno

```bash
# Application
APP_NAME=Argentum
APP_VERSION=0.1.0
ENVIRONMENT=development
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/argentum_db

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Nota**: Cambiar `JWT_SECRET_KEY` en producción a un valor seguro aleatorio.

## API Documentation

Una vez iniciado el servidor:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints

### Autenticación

Base path: `/api/v1/auth`

#### POST /api/v1/auth/register

Registrar un nuevo usuario.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "john_doe"
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-13T12:00:00Z",
  "updated_at": "2024-01-13T12:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Email o username ya existe
- `422 Unprocessable Entity` - Validación fallida

#### POST /api/v1/auth/login

Iniciar sesión y obtener JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2024-01-13T12:30:00Z"
}
```

**Errors:**
- `401 Unauthorized` - Credenciales inválidas
- `403 Forbidden` - Usuario inactivo

#### GET /api/v1/auth/me

Obtener información del usuario autenticado.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-13T12:00:00Z",
  "updated_at": "2024-01-13T12:00:00Z"
}
```

**Errors:**
- `401 Unauthorized` - Token inválido o expirado
- `404 Not Found` - Usuario no encontrado

## Base de Datos

### Esquema

#### Tabla `users`

| Campo            | Tipo                  | Constraints        | Descripción                    |
|------------------|-----------------------|--------------------|--------------------------------|
| id               | UUID                  | PRIMARY KEY        | Identificador único            |
| email            | VARCHAR(255)          | UNIQUE, NOT NULL   | Email del usuario              |
| username         | VARCHAR(100)          | UNIQUE, NOT NULL   | Nombre de usuario              |
| hashed_password  | VARCHAR(255)          | NOT NULL           | Contraseña hasheada (bcrypt)   |
| is_active        | BOOLEAN               | DEFAULT TRUE       | Estado de la cuenta            |
| is_verified      | BOOLEAN               | DEFAULT FALSE      | Email verificado               |
| created_at       | TIMESTAMP WITH TZ     | NOT NULL           | Fecha de creación              |
| updated_at       | TIMESTAMP WITH TZ     | NOT NULL           | Última actualización           |

**Índices:**
- `ix_users_id` - Índice en id (primary key)
- `ix_users_email` - Índice único en email

### Migraciones con Alembic

```bash
# Ver estado actual
uv run alembic current

# Aplicar todas las migraciones
uv run alembic upgrade head

# Crear nueva migración (automática)
uv run alembic revision --autogenerate -m "descripción"

# Revertir última migración
uv run alembic downgrade -1

# Ver historial
uv run alembic history
```

**Migraciones existentes:**
1. `f0886c6a3ba1` - Crear tabla users
2. `ca722952e486` - Agregar índice en username
3. `95584c0e0794` - Timestamps con timezone

## Testing

El proyecto tiene **125 tests** con cobertura completa de la funcionalidad de autenticación.

```bash
# Ejecutar todos los tests
uv run pytest

# Tests con verbose
uv run pytest -v

# Tests con coverage
uv run pytest --cov=. --cov-report=html

# Ejecutar tests específicos
uv run pytest tests/domain/ -v
uv run pytest tests/application/ -v
uv run pytest tests/infrastructure/ -v
uv run pytest tests/presentation/ -v

# Ejecutar un archivo específico
uv run pytest tests/domain/test_user_entity.py -v

# Ejecutar un test específico
uv run pytest tests/domain/test_user_entity.py::TestEmailValidation::test_valid_email -v

# Stop en primer fallo
uv run pytest -x
```

### Distribución de Tests

- **Domain** (25 tests): Entidades y value objects
- **Infrastructure** (54 tests): Servicios y repositorios
  - Hash service: 16 tests
  - JWT token service: 21 tests
  - PostgreSQL repository: 17 tests
- **Application** (17 tests): Use cases
  - Register user: 8 tests
  - Login user: 9 tests
- **Presentation** (29 tests): API endpoints y middleware
  - Auth endpoints: 17 tests
  - Request ID middleware: 12 tests

### Fixtures

Los fixtures compartidos están en `tests/conftest.py`:

- `db_file` - Archivo SQLite temporal
- `db_engine` - Engine SQLAlchemy async
- `session` - Session de base de datos para tests
- `hash_service` - BcryptHashService
- `token_service` - JWTTokenService
- `user_repository` - PostgresUserRepository

## Code Quality

### Linting y Formatting con Ruff

```bash
# Formatear código
./scripts/format.sh
# o
uv run ruff format .

# Ejecutar linter
./scripts/lint.sh
# o
uv run ruff check .

# Autofix de problemas
uv run ruff check --fix .

# Limpiar cache
./scripts/clean.sh
```

**Configuración en `pyproject.toml`:**
- Line length: 100
- Target Python: 3.14
- Excluye: alembic/, .venv/, __pycache__/

## Servicios y Use Cases

### RegisterUser Use Case

**Ubicación**: `application/use_cases/register_user.py`

Caso de uso para registrar nuevos usuarios.

```python
from application.use_cases.register_user import RegisterUser
from application.dtos.auth_dtos import RegisterUserDTO

register_user = RegisterUser(
    user_repository=user_repo,
    hash_service=hash_service
)

dto = RegisterUserDTO(
    email="user@example.com",
    password="SecurePassword123!",
    username="newuser"
)

user_response = await register_user.execute(dto)
```

**Funcionalidades:**
- Valida email único
- Valida username único (3-50 caracteres)
- Hashea password con bcrypt
- Crea usuario con is_verified=False
- Logging estructurado
- Manejo de excepciones de dominio

### LoginUser Use Case

**Ubicación**: `application/use_cases/login_user.py`

Caso de uso para autenticación de usuarios.

```python
from application.use_cases.login_user import LoginUser
from application.dtos.auth_dtos import LoginDTO

login_user = LoginUser(
    user_repository=user_repo,
    hash_service=hash_service,
    token_service=token_service
)

dto = LoginDTO(
    email="user@example.com",
    password="SecurePassword123!"
)

token_response = await login_user.execute(dto)
```

**Funcionalidades:**
- Verifica email y password
- Valida usuario activo
- Genera JWT token
- Logging de seguridad (intentos fallidos, usuarios inactivos)
- Mensajes de error genéricos
- Manejo de excepciones de dominio

### BcryptHashService

**Ubicación**: `infrastructure/services/hash_service.py`

Servicio para hashing de passwords con bcrypt.

```python
from infrastructure.services.hash_service import BcryptHashService

hash_service = BcryptHashService(rounds=12)

# Hash password
hashed = hash_service.hash_password("my_password")

# Verify password
is_valid = hash_service.verify_password("my_password", hashed)
```

**Características:**
- Bcrypt con salt aleatorio
- Configurable rounds (default: 12)
- Validación de formato
- Thread-safe

### JWTTokenService

**Ubicación**: `infrastructure/services/jwt_token_service.py`

Servicio para generación y validación de JWT tokens.

```python
from infrastructure.services.jwt_token_service import JWTTokenService
from uuid import UUID

token_service = JWTTokenService(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30
)

# Generate token
user_id = UUID("...")
token, expires_at = token_service.generate_token(user_id, "user@example.com")

# Validate token
payload = token_service.validate_token(token)
# Returns: {"user_id": "...", "email": "..."}

# Get expiration
expiration = token_service.get_token_expiration(token)
```

**Características:**
- PyJWT con algoritmo configurable (default: HS256)
- Expiración configurable
- Validación de tokens
- Manejo de tokens expirados
- Excepciones de dominio

## Seguridad

### Password Hashing

- Algoritmo: bcrypt
- Rounds: 12 (configurable)
- Salt aleatorio por password

### JWT Authentication

- Algoritmo: HS256 (configurable)
- Secret key: Configurable vía env
- Expiración: 30 minutos (configurable)
- Header: `Authorization: Bearer <token>`

### CORS

Configurado para permitir orígenes específicos:
- http://localhost:5173 (Vite dev server)
- http://localhost:3000 (alternativo)

Modificar `CORS_ORIGINS` en `.env` para producción.

### Logging de Seguridad

Eventos loggeados con structlog:
- Registros exitosos
- Logins exitosos
- Intentos de login fallidos
- Usuarios inactivos intentando login
- Tokens expirados o inválidos

## Desarrollo

### Scripts Disponibles

```bash
# Desarrollo
uv run fastapi dev main.py          # Dev server con hot reload

# Producción
uv run fastapi run main.py          # Production server

# Testing
uv run pytest                       # Ejecutar tests
uv run pytest -v                    # Verbose
uv run pytest --cov=.              # Con coverage

# Code Quality
./scripts/format.sh                 # Formatear código
./scripts/lint.sh                   # Linter
./scripts/clean.sh                  # Limpiar cache

# Database
uv run alembic upgrade head         # Aplicar migraciones
uv run alembic revision --autogenerate -m "msg"  # Nueva migración
```

### Convenciones de Código

- **Nombres de archivos**: snake_case
- **Clases**: PascalCase
- **Funciones/variables**: snake_case
- **Constantes**: UPPER_SNAKE_CASE
- **Type hints**: Obligatorios en todas las funciones
- **Docstrings**: Estilo Google para clases y funciones públicas
- **Imports**: Agrupados en stdlib, third-party, local
- **Async**: Preferir async/await para operaciones I/O

### Agregar Nuevas Features

Para agregar nuevas funcionalidades siguiendo Clean Architecture:

1. **Domain**: Crear entidades, value objects y excepciones
2. **Application**: Crear DTOs, interfaces y use cases
3. **Infrastructure**: Implementar interfaces (servicios, repositorios)
4. **Presentation**: Crear schemas, routes y dependencies
5. **Tests**: Escribir tests en cada capa
6. **Migrations**: Crear migraciones si hay cambios en DB

## Roadmap

### Implementado ✅

- Clean Architecture con 4 capas bien definidas
- Autenticación JWT completa
- Registro y login de usuarios
- Password hashing con bcrypt
- Base de datos PostgreSQL async
- Migraciones con Alembic
- 125 tests con alta cobertura
- Logging estructurado
- CORS configurado
- Documentación OpenAPI

### Próximas Features

- [ ] Verificación de email
- [ ] Reset de password
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] Redis para cache
- [ ] WebSockets para cotizaciones en tiempo real
- [ ] Tracking de acciones argentinas
- [ ] Sistema de notificaciones
- [ ] Admin panel

## Licencia

Propiedad de Argentum Platform.
