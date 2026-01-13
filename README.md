# ARGENTUM

Sistema de tracking de cotizaciones de acciones argentinas con autenticación JWT y dashboard en tiempo real.

> **Estado del Proyecto**: Backend completo con 125 tests ✅ | Frontend Fase 2 completada ✅

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Quick Start](#quick-start)
- [Scripts Disponibles](#scripts-disponibles)
- [Arquitectura](#arquitectura)
- [API Documentation](#api-documentation)
- [Base de Datos](#base-de-datos)
- [Testing](#testing)
- [Variables de Entorno](#variables-de-entorno)
- [Seguridad](#seguridad)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [Contribuir](#contribuir)

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

## Estructura del Proyecto

```text
ARGENTUM/
├── backend/                     # API FastAPI
│   ├── domain/                 # Entidades, value objects, repositorios
│   │   ├── entities/           # User, BaseEntity
│   │   ├── repositories/       # Interfaces (UserRepository)
│   │   ├── exceptions/         # Excepciones de dominio
│   │   └── value_objects/      # Email, HashedPassword, PlainPassword
│   ├── application/            # Use cases, DTOs, interfaces
│   │   ├── use_cases/          # RegisterUser, LoginUser
│   │   ├── dtos/               # RegisterUserDTO, UserResponseDTO, LoginDTO, TokenDTO
│   │   └── interfaces/         # HashService, TokenService
│   ├── infrastructure/         # PostgreSQL, bcrypt, JWT
│   │   ├── database/           # Conexión PostgreSQL + UserModel
│   │   ├── repositories/       # PostgresUserRepository
│   │   └── services/           # BcryptHashService, JWTTokenService
│   ├── presentation/           # FastAPI routes, schemas, middleware
│   │   ├── config.py           # Settings con pydantic-settings
│   │   └── api/
│   │       ├── routes/         # auth.py
│   │       ├── schemas/        # auth_schemas.py
│   │       └── dependencies/   # auth.py (dependency injection)
│   ├── alembic/               # Migraciones de base de datos
│   ├── tests/                 # 125 tests (pytest)
│   └── README.md              # Documentación detallada del backend
│
├── frontend/                   # Aplicación React
│   ├── src/
│   │   ├── features/          # Features modulares (auth, ...)
│   │   │   └── auth/         # Todo relacionado con auth junto
│   │   │       ├── api/
│   │   │       ├── components/
│   │   │       ├── hooks/
│   │   │       ├── pages/
│   │   │       ├── stores/
│   │   │       └── types/
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

- **Frontend**: <http://localhost:5173>
- **Backend API**: <http://localhost:8000>
- **API Docs (Swagger)**: <http://localhost:8000/docs>
- **API Docs (ReDoc)**: <http://localhost:8000/redoc>

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

### Scripts de Backend

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
./scripts/clean.sh               # Limpiar cache y archivos temporales
```

### Scripts de Frontend

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

## Arquitectura

### Backend: Clean Architecture

El backend sigue **Clean Architecture / Hexagonal Architecture** con 4 capas:

```text
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

```text
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

## API Documentation

### Endpoints Disponibles

#### Autenticación (`/api/v1/auth`)

| Método | Endpoint                | Descripción            | Auth |
| ------ | ----------------------- | ---------------------- | ---- |
| POST   | `/api/v1/auth/register` | Registrar usuario      | No   |
| POST   | `/api/v1/auth/login`    | Iniciar sesión         | No   |
| GET    | `/api/v1/auth/me`       | Obtener usuario actual | Sí   |

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

**Errors:**

- `401 Unauthorized`: Credenciales inválidas
- `403 Forbidden`: Usuario inactivo

#### GET /api/v1/auth/me

**Headers:**

```http
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

**Errors:**

- `401 Unauthorized`: Token inválido o expirado
- `404 Not Found`: Usuario no encontrado

**Ver documentación interactiva completa**: <http://localhost:8000/docs>

## Testing

### Tests de Backend

**125 tests** con pytest y alta cobertura:

```bash
cd backend
uv run pytest                # Ejecutar todos los tests
uv run pytest -v             # Verbose
uv run pytest --cov=.        # Con coverage report
```

**Distribución de tests:**

- Domain: 25 tests (entities, value objects)
- Infrastructure: 54 tests (services, repositories)
- Application: 17 tests (use cases)
- Presentation: 29 tests (endpoints, middleware)

### Tests de Frontend

**2 tests** (setup básico, más por implementar):

```bash
cd frontend
bun run test                 # Tests en modo watch
bun run test:ui              # UI interactiva de Vitest
bun run test:coverage        # Con coverage
```

## Base de Datos

### Schema Actual

#### Tabla `users`

| Campo           | Tipo              | Constraints       | Descripción                |
| --------------- | ----------------- | ----------------- | -------------------------- |
| id              | UUID              | PRIMARY KEY       | Identificador único        |
| email           | VARCHAR(255)      | UNIQUE, NOT NULL  | Email del usuario          |
| username        | VARCHAR(100)      | UNIQUE, NOT NULL  | Nombre de usuario          |
| hashed_password | VARCHAR(255)      | NOT NULL          | Password hasheado (bcrypt) |
| is_active       | BOOLEAN           | DEFAULT TRUE      | Estado de la cuenta        |
| is_verified     | BOOLEAN           | DEFAULT FALSE     | Email verificado           |
| created_at      | TIMESTAMP WITH TZ | NOT NULL          | Fecha de creación          |
| updated_at      | TIMESTAMP WITH TZ | NOT NULL          | Última actualización       |

**Índices:**

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

**Migraciones existentes:**

1. `f0886c6a3ba1` - Crear tabla users
2. `ca722952e486` - Agregar índice en username
3. `95584c0e0794` - Timestamps con timezone

## Variables de Entorno

### Configuración de Backend (`.env`)

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

### Configuración de Frontend (`.env`)

```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

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

## Troubleshooting

### Backend no se conecta a PostgreSQL

**Problema**: Error de conexión a la base de datos

**Solución:**

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

**Solución:**

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

**Solución:**

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

## Documentación Adicional

- **Backend**: [backend/README.md](backend/README.md) - Documentación técnica completa
- **Frontend**: [frontend/README.md](frontend/README.md) - Documentación técnica completa
- **Fase 2**: [frontend/PHASE2.md](frontend/PHASE2.md) - Detalles de implementación Fase 2

## Licencia

Propiedad de Argentum Platform.

## Contacto

Para preguntas o soporte, contactar al equipo de desarrollo.

---

**Última actualización**: Enero 2026
