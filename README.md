# ARGENTUM

Sistema de tracking de cotizaciones de acciones argentinas con autenticación JWT y dashboard en tiempo real.

> **Estado del Proyecto**: Backend completo con 125 tests ✅ | Frontend Fase 2 completada ✅

---

## Visión General

**Argentum** es una plataforma financiera para trackear cotizaciones de acciones argentinas en tiempo real. El proyecto está construido con tecnologías modernas siguiendo las mejores prácticas de arquitectura de software.

### Características Principales

✅ **Sistema de Autenticación JWT completo**
- Registro y login de usuarios
- Tokens JWT con expiración configurable
- Password hashing con bcrypt
- Sesión persistente en el cliente

✅ **Clean Architecture en Backend**
- Separación de concerns en 4 capas
- Dependency Inversion Principle
- 100% testeable
- Mantenible y escalable

✅ **Feature-first Frontend**
- React 19 con TypeScript estricto
- State management (Zustand + React Query)
- UI moderna con Tailwind CSS + shadcn/ui
- Rutas protegidas

⏳ **Próximamente**
- Dashboard de cotizaciones en tiempo real
- WebSockets para datos live
- Sistema de notificaciones
- Watchlists y favoritos

---

## Stack Tecnológico

### Backend
- **Framework**: FastAPI (Python 3.14+)
- **Database**: PostgreSQL 18.1
- **ORM**: SQLAlchemy (async)
- **Package Manager**: uv
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **Migrations**: Alembic
- **Testing**: pytest (125 tests)
- **Code Quality**: Ruff

### Frontend
- **Framework**: React 19
- **Language**: TypeScript 5.9
- **Build Tool**: Vite 7
- **Runtime**: Bun 1.3+
- **Routing**: React Router 7
- **State**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Testing**: Vitest
- **Code Quality**: Biome

### DevOps
- **Containerization**: Docker + Docker Compose
- **Database**: PostgreSQL en Docker

---

## Estructura del Proyecto

```
ARGENTUM/
├── backend/                     # API FastAPI
│   ├── domain/                 # Entidades, value objects, repositorios
│   ├── application/            # Use cases, DTOs, interfaces
│   ├── infrastructure/         # PostgreSQL, bcrypt, JWT
│   ├── presentation/           # FastAPI routes, schemas, middleware
│   ├── alembic/               # Migraciones de base de datos
│   ├── tests/                 # 125 tests (pytest)
│   └── README.md              # Documentación detallada del backend
│
├── frontend/                   # Aplicación React
│   ├── src/
│   │   ├── features/          # Features modulares (auth, ...)
│   │   ├── components/        # Componentes compartidos
│   │   ├── lib/              # HTTP client, utils, constants
│   │   └── pages/            # Páginas principales
│   ├── tests/                # Tests (Vitest)
│   └── README.md             # Documentación detallada del frontend
│
├── docker-compose.yml         # PostgreSQL containerizado
├── package.json              # Workspace root (Bun)
├── bun.lock                  # Lockfile de Bun
└── README.md                 # Este archivo (visión general)
```

---

## Quick Start

### Prerrequisitos

- **Backend**: Python 3.14+, uv, Docker
- **Frontend**: Bun 1.3+
- **Database**: Docker Compose

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd ARGENTUM

# 2. Iniciar PostgreSQL
docker compose up -d postgres

# 3. Instalar dependencias
bun install              # Frontend (con workspaces)
cd backend && uv sync    # Backend

# 4. Configurar variables de entorno
cd backend
cp .env.example .env     # Editar si es necesario (defaults funcionan con Docker)

cd ../frontend
cp .env.example .env     # VITE_API_BASE_URL=http://localhost:8000

# 5. Ejecutar migraciones
cd ../backend
uv run alembic upgrade head

# 6. Iniciar servidores (en terminales separadas)
# Terminal 1 - Backend
cd backend
uv run fastapi dev main.py     # http://localhost:8000

# Terminal 2 - Frontend
cd frontend
bun run dev                     # http://localhost:5173
```

### Acceder a la aplicación

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

---

## Scripts Disponibles

### Root (desde la raíz del proyecto)

```bash
# Desarrollo
bun run dev:frontend         # Iniciar frontend
bun run dev:backend          # Iniciar backend

# Instalación
bun run install:frontend     # Instalar deps del frontend
bun run install:backend      # Instalar deps del backend

# Testing
bun run test:frontend        # Tests del frontend
bun run test:backend         # Tests del backend (125 tests)

# Build
bun run build:frontend       # Build de producción del frontend
bun run build:backend        # Build de producción del backend
```

### Backend

```bash
cd backend

# Desarrollo
uv run fastapi dev main.py       # Dev server con hot reload

# Testing
uv run pytest                    # Ejecutar todos los tests
uv run pytest -v                 # Verbose
uv run pytest --cov=.           # Con coverage

# Database
uv run alembic upgrade head      # Aplicar migraciones
uv run alembic revision --autogenerate -m "msg"  # Nueva migración

# Code Quality
./scripts/format.sh              # Formatear código
./scripts/lint.sh                # Linter
```

### Frontend

```bash
cd frontend

# Desarrollo
bun run dev                      # Dev server (http://localhost:5173)

# Testing
bun run test                     # Tests en modo watch
bun run test:ui                  # UI interactiva
bun run test:coverage            # Con coverage

# Build
bun run build                    # Build para producción
bun run preview                  # Preview del build

# Code Quality
bun run lint                     # Linter (Biome)
bun run lint:fix                 # Autofix
bun run format                   # Formatter
```

---

## Arquitectura

### Backend: Clean Architecture

El backend sigue **Clean Architecture / Hexagonal Architecture** con 4 capas:

```
┌─────────────────────────────────────────┐
│         PRESENTATION                    │
│    FastAPI routes, schemas              │
├─────────────────────────────────────────┤
│         APPLICATION                     │
│    Use cases, DTOs, interfaces          │
├─────────────────────────────────────────┤
│         DOMAIN                          │
│    Entities, value objects              │
├─────────────────────────────────────────┤
│         INFRASTRUCTURE                  │
│    PostgreSQL, bcrypt, JWT              │
└─────────────────────────────────────────┘
```

**Principios clave**:
- Domain no tiene dependencias externas
- Dependency Inversion en todas las capas
- Interfaces en Application, implementaciones en Infrastructure
- 100% testeable con pytest

**Ver documentación completa**: [backend/README.md](backend/README.md)

### Frontend: Feature-first Architecture

El frontend organiza el código por features de negocio:

```
src/
├── features/          # Módulos por funcionalidad
│   └── auth/         # Todo relacionado con auth junto
│       ├── api/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── stores/
│       └── types/
├── components/       # Compartidos
├── lib/             # Utilidades globales
└── pages/           # Páginas principales
```

**Principios clave**:
- Colocation: Todo relacionado está junto
- Type safety: TypeScript estricto
- Separation of concerns: API, UI, state separados
- Composición: Componentes pequeños y reutilizables

**Ver documentación completa**: [frontend/README.md](frontend/README.md)

---

## API Documentation

### Endpoints Disponibles

#### Autenticación (`/api/v1/auth`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Registrar usuario | No |
| POST | `/api/v1/auth/login` | Iniciar sesión | No |
| GET | `/api/v1/auth/me` | Obtener usuario actual | Sí |

#### POST /api/v1/auth/register

**Request:**
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
  "created_at": "2024-01-13T12:00:00Z"
}
```

#### POST /api/v1/auth/login

**Request:**
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

#### GET /api/v1/auth/me

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-13T12:00:00Z"
}
```

**Ver documentación interactiva completa**: http://localhost:8000/docs

---

## Testing

### Backend

**125 tests** con pytest y alta cobertura:

```bash
cd backend
uv run pytest                # Ejecutar todos los tests
uv run pytest -v             # Verbose
uv run pytest --cov=.        # Con coverage report
```

**Distribución de tests**:
- Domain: 25 tests (entities, value objects)
- Infrastructure: 54 tests (services, repositories)
- Application: 17 tests (use cases)
- Presentation: 29 tests (endpoints, middleware)

### Frontend

**2 tests** (setup básico, más por implementar):

```bash
cd frontend
bun run test                 # Tests en modo watch
bun run test:ui              # UI interactiva de Vitest
bun run test:coverage        # Con coverage
```

---

## Base de Datos

### Schema Actual

#### Tabla `users`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Identificador único |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email del usuario |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Nombre de usuario |
| hashed_password | VARCHAR(255) | NOT NULL | Password hasheado (bcrypt) |
| is_active | BOOLEAN | DEFAULT TRUE | Estado de la cuenta |
| is_verified | BOOLEAN | DEFAULT FALSE | Email verificado |
| created_at | TIMESTAMP WITH TZ | NOT NULL | Fecha de creación |
| updated_at | TIMESTAMP WITH TZ | NOT NULL | Última actualización |

**Índices**:
- `ix_users_id` - Primary key
- `ix_users_email` - Unique index para búsquedas

### Migraciones

```bash
cd backend

# Ver estado actual
uv run alembic current

# Aplicar todas las migraciones
uv run alembic upgrade head

# Crear nueva migración
uv run alembic revision --autogenerate -m "descripción"

# Revertir última migración
uv run alembic downgrade -1
```

**Migraciones existentes**:
1. `f0886c6a3ba1` - Crear tabla users
2. `ca722952e486` - Agregar índice en username
3. `95584c0e0794` - Timestamps con timezone

---

## Variables de Entorno

### Backend (`.env`)

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

### Frontend (`.env`)

```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

---

## Seguridad

### Password Hashing
- **Algoritmo**: bcrypt
- **Rounds**: 12 (configurable)
- **Salt**: Aleatorio por password

### JWT Authentication
- **Algoritmo**: HS256 (configurable)
- **Expiración**: 30 minutos (configurable)
- **Secret**: Configurable vía variable de entorno

### CORS
Configurado para orígenes específicos (localhost en desarrollo)

### Logging
- Structlog en backend
- Logging de eventos de seguridad (logins, fallos, tokens expirados)

---

## Roadmap

### Fase 1: Fundamentos ✅
- [x] Setup inicial del proyecto
- [x] Configuración de PostgreSQL con Docker
- [x] Clean Architecture en backend
- [x] Sistema de migraciones con Alembic

### Fase 2: Autenticación ✅
- [x] Entidades de dominio (User, Email, Password)
- [x] Use cases (RegisterUser, LoginUser)
- [x] Servicios (BcryptHashService, JWTTokenService)
- [x] Repositorio PostgreSQL
- [x] Endpoints REST de autenticación
- [x] 125 tests en backend
- [x] Frontend React con TypeScript
- [x] HTTP client tipo-safe
- [x] State management (Zustand + React Query)
- [x] Forms de login y registro
- [x] Rutas protegidas

### Fase 3: Dashboard (En Planificación)
- [ ] WebSockets para datos en tiempo real
- [ ] Integración con API de cotizaciones argentinas
- [ ] Dashboard con gráficos de precios
- [ ] Sistema de notificaciones
- [ ] Watchlists y favoritos

### Fase 4: Features Avanzadas (Futuro)
- [ ] Verificación de email
- [ ] Reset de password
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] Redis para cache
- [ ] Admin panel
- [ ] Dark mode
- [ ] PWA capabilities
- [ ] Mobile app (React Native)

---

## Troubleshooting

### Backend no se conecta a PostgreSQL

**Problema**: Error de conexión a la base de datos

**Solución**:
```bash
# Verificar que PostgreSQL esté corriendo
docker compose ps

# Iniciar PostgreSQL si no está corriendo
docker compose up -d postgres

# Ver logs de PostgreSQL
docker compose logs postgres
```

### Frontend no puede hacer requests al backend

**Problema**: CORS errors o network errors

**Solución**:
```bash
# Verificar que backend esté corriendo
curl http://localhost:8000/docs

# Verificar VITE_API_BASE_URL en frontend/.env
cat frontend/.env

# Verificar CORS_ORIGINS en backend/.env
cat backend/.env
```

### Migraciones fallan

**Problema**: Error al ejecutar migraciones

**Solución**:
```bash
# Ver estado actual
cd backend
uv run alembic current

# Ver historial
uv run alembic history

# Si hay inconsistencias, recrear la base de datos
docker compose down -v
docker compose up -d postgres
uv run alembic upgrade head
```

---

## Contribuir

### Setup para Desarrollo

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/amazing-feature`)
3. Hacer commits con mensajes descriptivos
4. Ejecutar tests (`bun run test:backend && bun run test:frontend`)
5. Ejecutar linters (`cd backend && ./scripts/lint.sh && cd ../frontend && bun run lint`)
6. Push a tu branch (`git push origin feature/amazing-feature`)
7. Abrir Pull Request

### Convenciones

- **Commits**: Formato conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **Branches**: `feature/`, `bugfix/`, `hotfix/`, `docs/`
- **Code style**: Seguir configuraciones de Ruff (backend) y Biome (frontend)
- **Tests**: Agregar tests para nuevas features

---

## Documentación Adicional

- **Backend**: [backend/README.md](backend/README.md) - Documentación técnica completa
- **Frontend**: [frontend/README.md](frontend/README.md) - Documentación técnica completa
- **Fase 2**: [frontend/PHASE2.md](frontend/PHASE2.md) - Detalles de implementación Fase 2

---

## Licencia

Propiedad de Argentum Platform.

---

## Contacto

Para preguntas o soporte, contactar al equipo de desarrollo.

---

**Última actualización**: Enero 2025

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
