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
- Docker y Docker Compose (próximamente)

### Instalación

```bash
# Instalar dependencias del backend
bun run install:backend

# Instalar dependencias del frontend (cuando esté disponible)
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
│   ├── database/       
│   ├── repositories/   
│   └── services/       
└── presentation/        # API REST
    └── api/
        ├── routes/     
        ├── schemas/    
        └── dependencies/
```

### Variables de entorno

Copia el archivo `.env.example` a `.env` en el directorio `backend/`:

```bash
cd backend
cp .env.example .env
```

Edita las variables según tu configuración local.

---
