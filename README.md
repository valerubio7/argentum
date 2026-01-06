# ARGENTUM

Sistema de tracking de cotizaciones de acciones argentinas con autenticación y dashboard en tiempo real.

> **⚠️ Proyecto en desarrollo activo - Setup en progreso**

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
│   │   │   └── user_exceptions.py
│   │   └── value_objects/
│   │       ├── email.py        # Email value object
│   │       └── password.py     # HashedPassword, PlainPassword
│   ├── application/             # Casos de uso
│   │   ├── use_cases/
│   │   ├── dtos/
│   │   └── interfaces/
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

---

## 📝 Scripts Disponibles

| Script | Descripción | Estado |
|--------|-------------|--------|
| `bun run dev:backend` | Corre backend en desarrollo | ✅ Disponible |
| `bun run build:backend` | Build de producción del backend | ✅ Disponible |
| `bun run install:backend` | Instala deps backend | ✅ Disponible |
| `bun run dev:frontend` | Corre frontend en desarrollo | ⏳ Requiere Issue #3 |
| `bun run install:frontend` | Instala deps frontend | ⏳ Requiere Issue #3 |
| `bun run build:frontend` | Build de producción | ⏳ Requiere Issue #3 |

---

## 🔧 Backend

El backend está desarrollado con **FastAPI** siguiendo los principios de **Clean Architecture**.

### Tecnologías

- **Framework**: FastAPI
- **ORM**: SQLAlchemy (async)
- **Database Driver**: asyncpg
- **Migrations**: Alembic ✅
- **Testing**: pytest + pytest-asyncio

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

### Estructura

```
backend/
├── domain/              # Lógica de negocio
│   ├── entities/        # User, BaseEntity
│   ├── repositories/    # Interfaces (UserRepository)
│   ├── exceptions/      # Excepciones de dominio
│   └── value_objects/   # Email, HashedPassword
├── application/         # Casos de uso
│   ├── use_cases/      
│   ├── dtos/           
│   └── interfaces/     
├── infrastructure/      # Implementaciones
│   ├── database/        # ✅ Conexión PostgreSQL + UserModel
│   ├── repositories/    # ✅ PostgresUserRepository
│   └── services/       
└── presentation/        # API REST
    └── api/
        ├── routes/     
        ├── schemas/    
        └── dependencies/
```

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
- Los tests usan SQLite en memoria por defecto (via `aiosqlite`)
- Para usar PostgreSQL de test, configurar `TEST_DATABASE_URL`
- Los fixtures compartidos están en `tests/conftest.py`

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
```

**Formato de DATABASE_URL para async:**
```
postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
```

---
