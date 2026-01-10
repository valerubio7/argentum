# ARGENTUM

Sistema de tracking de cotizaciones de acciones argentinas con autenticación y dashboard en tiempo real.

> **✅ Backend funcional con autenticación JWT y 113 tests pasando**

---

## 🛠️ Stack Tecnológico

- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI
- **Base de datos**: PostgreSQL
- **Cache**: Redis
- **Deploy**: Docker

---

## 📁 Estructura del Proyecto

```
ARGENTUM/
├── frontend/                    # Aplicación React (próximamente)
├── backend/                     # API FastAPI
│   ├── domain/                  # Capa de dominio
│   │   ├── entities/
│   │   │   ├── base.py         # BaseEntity con UUID y timestamps
│   │   │   └── user.py         # Entidad User
│   │   ├── repositories/
│   │   │   └── user_repository.py  # Interfaz UserRepository
│   │   ├── exceptions/
│   │   │   ├── user_exceptions.py  # User domain errors
│   │   │   └── token_exceptions.py # Token domain errors
│   │   └── value_objects/
│   │       ├── email.py        # Email value object
│   │       └── password.py     # HashedPassword, PlainPassword
│   ├── application/             # Casos de uso
│   │   ├── use_cases/          # ✅ RegisterUser, LoginUser
│   │   ├── dtos/               # ✅ RegisterUserDTO, UserResponseDTO, LoginDTO, TokenDTO
│   │   └── interfaces/         # ✅ HashService, TokenService
│   ├── infrastructure/          # Implementaciones
│   │   ├── database/
│   │   │   ├── connection.py   # Conexión async PostgreSQL
│   │   │   └── models.py       # UserModel SQLAlchemy
│   │   ├── repositories/
│   │   │   └── postgres_user_repository.py  # Implementación PostgreSQL
│   │   └── services/
│   ├── presentation/            # API REST
│   │   └── api/
│   │       ├── routes/
│   │       ├── schemas/
│   │       └── dependencies/
│   ├── alembic/                 # Migraciones de BD
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/                   # Tests unitarios
│   │   ├── domain/
│   │   │   └── test_user_entity.py
│   │   └── infrastructure/
│   │       └── test_postgres_user_repository.py
│   ├── alembic.ini
│   └── pyproject.toml
├── docker-compose.yml
├── package.json                 # Workspace root
└── README.md
```

---

## 🚀 Setup

### Prerrequisitos

- Node.js 18+ / Bun 1.0+
- Python 3.14+
- Docker y Docker Compose
- [uv](https://docs.astral.sh/uv/) - Python package manager

### Instalación

```bash
# 1. Iniciar PostgreSQL con Docker
docker compose up -d postgres

# 2. Instalar dependencias del backend
bun run install:backend

# 3. Configurar variables de entorno
cd backend
cp .env.example .env
# Edita .env con tu configuración (por defecto funciona con Docker)

# 4. Instalar dependencias del frontend (cuando esté disponible)
bun run install:frontend
```

### Desarrollo

```bash
# Correr backend en desarrollo (✅ Disponible)
bun run dev:backend    # http://localhost:8000

# Correr frontend en desarrollo (⏳ Próximamente)
bun run dev:frontend   # http://localhost:5173
```

### Documentación API

Una vez iniciado el backend, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Endpoints disponibles

##### Autenticación (`/api/auth`)

- **POST /api/auth/register** - Registrar nuevo usuario
  - Body: `{ "email": "user@example.com", "password": "SecurePass123!", "username": "john_doe" }`
  - Response 201: `{ "id": "uuid", "email": "...", "username": "...", "is_active": true, "is_verified": false, "created_at": "..." }`
  - Errors: 400 (duplicate email/username), 422 (validation error)

- **POST /api/auth/login** - Iniciar sesión
  - Body: `{ "email": "user@example.com", "password": "SecurePass123!" }`
  - Response 200: `{ "access_token": "jwt_token", "token_type": "bearer", "expires_at": "..." }`
  - Errors: 401 (invalid credentials), 403 (inactive user)

- **GET /api/auth/me** - Obtener usuario actual (requiere autenticación)
  - Headers: `Authorization: Bearer <token>`
  - Response 200: `{ "id": "uuid", "email": "...", "username": "...", "is_active": true, "is_verified": false, "created_at": "..." }`
  - Errors: 401 (invalid/expired token), 404 (user not found)

---

## 📝 Scripts Disponibles

| Script | Descripción | Estado |
|--------|-------------|--------|
| `bun run dev:backend` | Corre backend en desarrollo | ✅ Disponible |
| `bun run build:backend` | Build de producción del backend | ✅ Disponible |
| `bun run install:backend` | Instala deps backend | ✅ Disponible |
| `bun run test:backend` | Ejecuta tests del backend | ✅ 113 tests |
| `bun run dev:frontend` | Corre frontend en desarrollo | ⏳ Requiere Issue #3 |
| `bun run install:frontend` | Instala deps frontend | ⏳ Requiere Issue #3 |
| `bun run build:frontend` | Build de producción | ⏳ Requiere Issue #3 |

---

## 🔧 Backend

El backend está desarrollado con **FastAPI** siguiendo los principios de **Clean Architecture**.

### Tecnologías

- **Framework**: FastAPI
- **ORM**: SQLAlchemy (async)
- **Database Driver**: asyncpg (PostgreSQL), aiosqlite (tests)
- **Migrations**: Alembic ✅
- **Password Hashing**: bcrypt ✅
- **JWT Authentication**: PyJWT ✅
- **Configuration**: pydantic-settings ✅
- **Testing**: pytest + pytest-asyncio + httpx
- **Code Quality**: ruff (linter + formatter)

### Arquitectura

El backend sigue los principios de **Clean Architecture / Arquitectura Hexagonal**, separando claramente las responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION                            │
│              (FastAPI routes, schemas)                      │
├─────────────────────────────────────────────────────────────┤
│                     APPLICATION                             │
│              (Use cases, DTOs, interfaces)                  │
├─────────────────────────────────────────────────────────────┤
│                       DOMAIN                                │
│         (Entities, Value Objects, Repository interfaces)    │
├─────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE                            │
│     (PostgreSQL, SQLAlchemy models, Repository impls)       │
└─────────────────────────────────────────────────────────────┘
```

**Principios:**
- **Domain** no depende de ninguna otra capa
- **Application** solo depende de Domain
- **Infrastructure** implementa las interfaces definidas en Domain
- **Presentation** orquesta todo usando dependency injection

### Sistema de Autenticación

El backend implementa un sistema completo de autenticación JWT con las siguientes características:

#### Funcionalidades Implementadas ✅

- **Registro de usuarios** (`POST /api/auth/register`)
  - Validación de email único y formato válido
  - Validación de username único (3-50 caracteres)
  - Validación de password (mínimo 8 caracteres)
  - Hash seguro de contraseñas con bcrypt (12 rounds)
  - Usuarios nuevos creados como no verificados

- **Login de usuarios** (`POST /api/auth/login`)
  - Autenticación con email y password
  - Verificación de usuario activo
  - Generación de JWT token con expiración configurable (default: 30 min)
  - Mensajes de error genéricos para prevenir enumeración de usuarios
  - Logging de seguridad (intentos fallidos, usuarios inactivos)

- **Autenticación con JWT** (`GET /api/auth/me`)
  - Validación de tokens JWT en cada request
  - Verificación de expiración de tokens
  - Verificación de usuario activo
  - Acceso a información del usuario autenticado

#### Seguridad

- Passwords hasheados con bcrypt (12 rounds configurables)
- Tokens JWT firmados con HS256 (algoritmo configurable)
- Secret key configurable via variables de entorno
- Validación de formato de tokens y payload
- Manejo apropiado de tokens expirados
- Status codes HTTP correctos (401, 403, 400)
- Headers WWW-Authenticate en respuestas 401

#### Testing

- **113 tests totales** con 100% de cobertura en autenticación:
  - 25 tests de entidades de dominio
  - 16 tests de hash service (bcrypt)
  - 21 tests de token service (JWT)
  - 17 tests de repositorio de usuarios
  - 8 tests de caso de uso de registro
  - 9 tests de caso de uso de login
  - 17 tests de integración de endpoints

### Estructura

```
backend/
├── domain/              # Lógica de negocio
│   ├── entities/        # User, BaseEntity
│   ├── repositories/    # Interfaces (UserRepository)
│   ├── exceptions/      # Excepciones de dominio
│   └── value_objects/   # Email, HashedPassword
├── application/         # Casos de uso
│   ├── use_cases/       # ✅ RegisterUser, LoginUser
│   ├── dtos/            # ✅ RegisterUserDTO, UserResponseDTO, LoginDTO, TokenDTO
│   └── interfaces/      # ✅ HashService, TokenService
├── infrastructure/      # Implementaciones
│   ├── database/        # ✅ Conexión PostgreSQL + UserModel
│   ├── repositories/    # ✅ PostgresUserRepository
│   └── services/        # ✅ BcryptHashService, JWTTokenService
└── presentation/        # API REST
    ├── config.py        # ✅ Settings con pydantic-settings
    └── api/
        ├── routes/      # ✅ auth.py
        ├── schemas/     # ✅ auth_schemas.py
        └── dependencies/ # ✅ auth.py (dependency injection)
```

### Servicios

#### RegisterUser Use Case

Caso de uso para el registro de nuevos usuarios:

```python
from application.use_cases import RegisterUser
from application.dtos import RegisterUserDTO

# Initialize use case
register_user = RegisterUser(
    user_repository=user_repo,
    hash_service=hash_service
)

# Execute registration
dto = RegisterUserDTO(
    email="user@example.com",
    password="SecurePassword123!",
    username="newuser"
)

user_response = await register_user.execute(dto)
# Returns: UserResponseDTO with id, email, username, is_active, is_verified, created_at
```

**Características:**
- ✅ Validación de email único
- ✅ Validación de username único
- ✅ Hashing automático de contraseñas
- ✅ Usuarios nuevos con is_verified=False
- ✅ Logging de registros exitosos
- ✅ Manejo de errores (UserAlreadyExistsError, ValueError)

#### LoginUser Use Case

Caso de uso para autenticación de usuarios:

```python
from application.use_cases import LoginUser
from application.dtos import LoginDTO

# Initialize use case
login_user = LoginUser(
    user_repository=user_repo,
    hash_service=hash_service,
    token_service=token_service
)

# Execute login
dto = LoginDTO(
    email="user@example.com",
    password="SecurePassword123!"
)

token_response = await login_user.execute(dto)
# Returns: TokenDTO with access_token, token_type, expires_at
```

**Características:**
- ✅ Verificación de email y password
- ✅ Validación de usuario activo
- ✅ Generación de JWT token
- ✅ Logging de seguridad (intentos fallidos, usuarios inactivos, logins exitosos)
- ✅ Mensajes de error genéricos (no revela si email o password es incorrecto)
- ✅ Manejo de errores (InvalidCredentialsError, UserNotActiveError)

#### HashService (Bcrypt)

Servicio para hashing seguro de passwords usando bcrypt:

```python
from infrastructure.services import BcryptHashService

hash_service = BcryptHashService(rounds=12)

# Hash password
hashed = hash_service.hash_password("my_password")

# Verify password
is_valid = hash_service.verify_password("my_password", hashed)
```

**Características:**
- ✅ Usa bcrypt con salt aleatorio
- ✅ Configurable número de rounds (default: 12)
- ✅ Validación de formato bcrypt
- ✅ Manejo de errores robusto

#### TokenService (JWT)

Servicio para generación y validación de tokens JWT para autenticación:

```python
from infrastructure.services import JWTTokenService
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
# Returns: {"user_id": "...", "email": "user@example.com"}

# Get token expiration
expiration = token_service.get_token_expiration(token)
```

**Características:**
- ✅ Generación de tokens JWT con PyJWT
- ✅ Algoritmo HS256 (configurable)
- ✅ Expiración configurable (default: 30 minutos)
- ✅ Validación de tokens con manejo de expiración
- ✅ Excepciones de dominio (ExpiredTokenError, InvalidTokenFormatError)
- ✅ Recuperación de fecha de expiración

### Base de Datos

La aplicación usa **PostgreSQL** con **SQLAlchemy async**. La conexión se configura automáticamente al iniciar.

#### Tabla `users`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `email` | VARCHAR(255) | Email único (índice único) |
| `username` | VARCHAR(100) | Username único |
| `hashed_password` | VARCHAR(255) | Contraseña hasheada |
| `is_active` | BOOLEAN | Estado de la cuenta (default: true) |
| `is_verified` | BOOLEAN | Email verificado (default: false) |
| `created_at` | TIMESTAMP WITH TZ | Fecha de creación |
| `updated_at` | TIMESTAMP WITH TZ | Última actualización |

**Índices:**
- `ix_users_email` - Índice único en email para búsquedas rápidas y unicidad
- `ix_users_id` - Índice en id para búsquedas por primary key

### Migraciones con Alembic

Alembic está configurado para trabajar con SQLAlchemy async.

```bash
cd backend

# Crear nueva migración automática
uv run alembic revision --autogenerate -m "descripción del cambio"

# Aplicar todas las migraciones pendientes
uv run alembic upgrade head

# Revertir última migración
uv run alembic downgrade -1

# Ver historial de migraciones
uv run alembic history

# Ver migración actual
uv run alembic current
```

**Configuración:**
- Las migraciones se guardan en `backend/alembic/versions/`
- La URL de la base de datos se lee de la variable de entorno `DATABASE_URL`
- El archivo `env.py` está configurado para async con `asyncpg`

### Tests

```bash
cd backend

# Ejecutar todos los tests
uv run pytest

# Ejecutar tests con verbose
uv run pytest -v

# Ejecutar solo tests de dominio
uv run pytest tests/domain/ -v

# Ejecutar solo tests de infraestructura
uv run pytest tests/infrastructure/ -v

# Ejecutar tests con coverage
uv run pytest --cov=.
```

**Configuración de tests:**
- Los tests usan SQLite file-based para testing (via `aiosqlite`)
- El archivo temporal se comparte entre test engine y app engine
- Para usar PostgreSQL de test, configurar `TEST_DATABASE_URL`
- Los fixtures compartidos están en `tests/conftest.py`
- **Total: 113 tests** (25 domain + 16 hash service + 21 JWT service + 17 repository + 8 register + 9 login + 17 integration)
- **Tests de integración**: 16 tests para endpoints de autenticación (register, login, get current user)

### Variables de entorno

El archivo `.env.example` contiene todas las variables necesarias:

```bash
cd backend
cp .env.example .env
```

**Variables principales:**

```env
# Database (configurado para Docker por defecto)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/argentum_db

# Database para tests (opcional, usa SQLite en memoria por defecto)
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/argentum_test_db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Password Hashing
BCRYPT_ROUNDS=12
```

**Formato de DATABASE_URL para async:**
```
postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
```

---
