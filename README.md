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

## 🚀 Setup (En Desarrollo)

### Prerrequisitos

- Node.js 18+
- Python 3.11+
- Docker y Docker Compose

### Instalación

**Estado actual:** La estructura base del monorepo está lista.

Cuando los issues #2 y #3 estén completos, podrás correr:

```bash
# Instalar dependencias
npm run install:frontend
npm run install:backend

# Desarrollo
npm run dev:frontend    # Puerto 5173
npm run dev:backend     # Puerto 8000
```

---

## 📝 Scripts Disponibles

| Script | Descripción | Estado |
|--------|-------------|--------|
| `npm run dev:frontend` | Corre frontend en desarrollo | ⏳ Requiere Issue #3 |
| `npm run dev:backend` | Corre backend en desarrollo | ⏳ Requiere Issue #2 |
| `npm run install:frontend` | Instala deps frontend | ⏳ Requiere Issue #3 |
| `npm run install:backend` | Instala deps backend | ⏳ Requiere Issue #2 |
| `npm run build:frontend` | Build de producción | ⏳ Requiere Issue #3 |
