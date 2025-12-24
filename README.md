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

```plain text
stock-tracker-arg/
├── frontend/          # Aplicación React
├── backend/           # API FastAPI
├── package.json       # Workspace root
├── .gitignore
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
- **Migrations**: Alembic (próximamente)
- **Testing**: pytest + pytest-asyncio

### Estructura

```
backend/
├── domain/              # Lógica de negocio
│   ├── entities/       
│   ├── repositories/   
│   ├── exceptions/     
│   └── value_objects/  
├── application/         # Casos de uso
│   ├── use_cases/      
│   ├── dtos/           
│   └── interfaces/     
├── infrastructure/      # Implementaciones
│   ├── database/       # ✅ Conexión PostgreSQL configurada
│   ├── repositories/   
│   └── services/       
└── presentation/        # API REST
    └── api/
        ├── routes/     
        ├── schemas/    
        └── dependencies/
```

### Base de Datos

La aplicación usa **PostgreSQL** con **SQLAlchemy async**. La conexión se configura automáticamente al iniciar:

```python
# Conexión configurada en infrastructure/database/connection.py
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/argentum_db
```

**Características:**
- ✅ Conexión async con asyncpg
- ✅ Session management con dependency injection
- ✅ Logs de conexión en startup
- ✅ BaseModel con timestamps automáticos

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

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---
