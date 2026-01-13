# Frontend - Argentum Client

Aplicación web React para el sistema de tracking de cotizaciones de acciones argentinas.

## Stack Tecnológico

- **React**: 19.2.0 - UI Framework con React 19
- **TypeScript**: 5.9.3 - Type safety estricto
- **Vite**: 7.2.4 - Build tool y dev server ultra-rápido
- **Bun**: 1.3.4+ - Runtime y package manager
- **React Router**: 7.12.0 - Client-side routing
- **TanStack Query**: 5.90.16 - Server state management y cache
- **Zustand**: 5.0.10 - Client state management
- **React Hook Form**: 7.71.0 - Form handling performante
- **Zod**: 4.3.5 - Schema validation
- **Tailwind CSS**: 4.1.18 - Utility-first CSS framework
- **shadcn/ui**: Componentes UI accesibles con Radix UI
- **Biome**: 2.3.11 - Linter y formatter ultra-rápido
- **Vitest**: 4.0.17 - Testing framework

## Arquitectura

El frontend sigue una **arquitectura feature-first** donde el código se organiza por funcionalidades de negocio en lugar de por tipo de archivo.

### Principios de Diseño

1. **Feature-first**: Cada feature es un módulo autónomo
2. **Colocation**: Todo relacionado con una feature está junto
3. **Separation of concerns**: API, UI, state y lógica separados
4. **Type safety**: TypeScript estricto en todo el proyecto
5. **Composición**: Componentes pequeños y reutilizables

### Estructura del Proyecto

```
frontend/
├── src/
│   ├── features/                    # Features modulares
│   │   └── auth/                   # Feature: Autenticación
│   │       ├── api/
│   │       │   └── authApi.ts      # API calls (login, register, getCurrentUser)
│   │       ├── components/
│   │       │   ├── LoginForm.tsx   # Form de login (106 líneas)
│   │       │   └── RegisterForm.tsx # Form de registro (168 líneas)
│   │       ├── hooks/
│   │       │   ├── useCurrentUser.ts # React Query hook para user actual
│   │       │   ├── useLogin.ts     # Mutation hook para login
│   │       │   ├── useLogout.ts    # Hook para logout
│   │       │   └── useRegister.ts  # Mutation hook para registro
│   │       ├── pages/
│   │       │   ├── LoginPage.tsx   # Página de login
│   │       │   └── RegisterPage.tsx # Página de registro
│   │       ├── stores/
│   │       │   └── authStore.ts    # Zustand store (token, user, persist)
│   │       ├── types/
│   │       │   └── auth.types.ts   # User, LoginRequest, TokenResponse, etc.
│   │       └── index.ts            # Barrel exports
│   │
│   ├── components/                  # Componentes compartidos
│   │   ├── auth/
│   │   │   └── ProtectedRoute.tsx  # HOC para rutas protegidas
│   │   └── ui/                     # shadcn/ui components
│   │       ├── button.tsx          # Button component
│   │       ├── card.tsx            # Card component
│   │       ├── form.tsx            # Form components (React Hook Form)
│   │       ├── input.tsx           # Input component
│   │       └── label.tsx           # Label component
│   │
│   ├── lib/                        # Utilidades y configuración
│   │   ├── api/
│   │   │   ├── client.ts           # HTTP client tipo-safe (196 líneas)
│   │   │   └── queryClient.ts      # TanStack Query config
│   │   ├── constants.ts            # API_ROUTES, QUERY_KEYS, STORAGE_KEYS
│   │   └── utils.ts                # cn() helper (Tailwind merge)
│   │
│   ├── pages/
│   │   └── DashboardPage.tsx       # Página principal (81 líneas)
│   │
│   ├── assets/
│   │   └── react.svg
│   │
│   ├── App.tsx                     # Router principal (26 líneas)
│   ├── App.css
│   ├── main.tsx                    # Entry point (17 líneas)
│   └── index.css                   # Tailwind directives
│
├── tests/
│   ├── setup.ts                    # Vitest setup
│   └── setup.test.ts               # Test básico
│
├── public/
│   └── vite.svg
│
├── dist/                           # Build output (gitignored)
│
├── package.json                    # Dependencias y scripts
├── tsconfig.json                   # TypeScript project references
├── tsconfig.app.json               # Config aplicación
├── tsconfig.bun.json               # Config Bun (vite.config.ts)
├── vite.config.ts                  # Vite config + alias @
├── vitest.config.ts                # Testing config
├── biome.json                      # Linter/formatter config
├── components.json                 # shadcn/ui config
├── tailwind.config.js              # Tailwind CSS config
├── postcss.config.js               # PostCSS config
├── .env                            # Variables de entorno (gitignored)
├── .env.example                    # Template de variables
├── index.html                      # HTML template
├── PHASE2.md                       # Documentación Fase 2
└── README.md
```

## Setup

### Prerrequisitos

- Bun 1.3.4+
- Node.js 18+ (opcional, Bun es suficiente)

### Instalación

```bash
# 1. Instalar dependencias (desde la raíz del proyecto)
bun install

# 2. Configurar variables de entorno
cd frontend
cp .env.example .env
# Editar .env si es necesario

# 3. Iniciar dev server
bun run dev
```

La aplicación estará disponible en `http://localhost:5173`

### Variables de Entorno

```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

**Nota**: Todas las variables de entorno en Vite deben comenzar con `VITE_`

## Desarrollo

### Scripts Disponibles

```bash
# Desarrollo
bun run dev              # Dev server con hot reload (http://localhost:5173)

# Build
bun run build            # Build para producción (dist/)
bun run preview          # Preview del build de producción

# Testing
bun run test             # Ejecutar tests en modo watch
bun run test:ui          # Vitest UI interactiva
bun run test:coverage    # Tests con coverage report

# Code Quality
bun run lint             # Ejecutar linter (Biome)
bun run lint:fix         # Autofix de problemas
bun run format           # Formatear código (Biome)
```

### Dev Server

El dev server de Vite tiene:
- **Hot Module Replacement (HMR)**: Cambios instantáneos sin recargar
- **Fast Refresh**: Preserva el estado de React
- **Instant startup**: Gracias a ESM nativo
- **Optimized dependencies**: Pre-bundling inteligente

## Features

### Autenticación (Fase 2 - Completada ✅)

Sistema completo de autenticación con JWT.

#### Componentes

**LoginForm** (`features/auth/components/LoginForm.tsx`)
- Form con React Hook Form + Zod
- Validación en tiempo real
- Manejo de errores de API
- Loading states
- Integración con TanStack Query mutation

**RegisterForm** (`features/auth/components/RegisterForm.tsx`)
- Form con validación completa
- Confirmación de password
- Validación de formato de email
- Username único
- Feedback visual de errores

**ProtectedRoute** (`components/auth/ProtectedRoute.tsx`)
- HOC para proteger rutas
- Redirección automática a /login
- Verificación de token

#### Hooks

**useLogin** (`features/auth/hooks/useLogin.ts`)
```typescript
import { useLogin } from '@/features/auth'

const LoginComponent = () => {
  const { mutate: login, isPending, isError } = useLogin()
  
  const handleLogin = (data: LoginRequest) => {
    login(data, {
      onSuccess: () => navigate('/dashboard'),
      onError: (error) => console.error(error)
    })
  }
  
  return // ...
}
```

**useRegister** (`features/auth/hooks/useRegister.ts`)
```typescript
import { useRegister } from '@/features/auth'

const RegisterComponent = () => {
  const { mutate: register, isPending } = useRegister()
  
  const handleRegister = (data: RegisterRequest) => {
    register(data, {
      onSuccess: () => navigate('/login')
    })
  }
  
  return // ...
}
```

**useCurrentUser** (`features/auth/hooks/useCurrentUser.ts`)
```typescript
import { useCurrentUser } from '@/features/auth'

const ProfileComponent = () => {
  const { data: user, isLoading, isError } = useCurrentUser()
  
  if (isLoading) return <div>Loading...</div>
  if (isError) return <div>Error loading user</div>
  
  return <div>Welcome {user.username}</div>
}
```

**useLogout** (`features/auth/hooks/useLogout.ts`)
```typescript
import { useLogout } from '@/features/auth'

const NavBar = () => {
  const logout = useLogout()
  
  return <button onClick={logout}>Logout</button>
}
```

#### State Management

**authStore** (`features/auth/stores/authStore.ts`)

Zustand store con persistencia en localStorage:

```typescript
import { useAuthStore } from '@/features/auth'

// En componentes
const { token, user, setAuth, clearAuth } = useAuthStore()

// State shape
{
  token: string | null,
  user: User | null,
  setAuth: (token: string, user: User) => void,
  clearAuth: () => void
}
```

**Características:**
- Persistencia automática en localStorage
- Type-safe con TypeScript
- Shallow comparison para optimizar renders
- Integrado con React Query

#### API Client

**HTTP Client** (`lib/api/client.ts`)

Cliente HTTP tipo-safe con interceptors:

```typescript
import { apiClient } from '@/lib/api/client'

// GET request
const user = await apiClient.get<User>('/api/v1/auth/me')

// POST request
const response = await apiClient.post<TokenResponse, LoginRequest>(
  '/api/v1/auth/login',
  { email, password }
)
```

**Características:**
- Interceptores de request (inyecta token automáticamente)
- Interceptores de response (maneja 401, refresh tokens)
- Type-safe con genéricos
- Manejo de errores centralizado
- Base URL configurable
- Logging en desarrollo

#### Rutas

```
/                    → Redirige a /dashboard
/login               → LoginPage (público)
/register            → RegisterPage (público)
/dashboard           → DashboardPage (protegido)
```

### UI Components (shadcn/ui)

Componentes accesibles construidos con Radix UI primitives:

- **Button**: Variantes (default, destructive, outline, ghost)
- **Card**: Header, Title, Description, Content, Footer
- **Form**: Integrado con React Hook Form
- **Input**: Tipo-safe con ref forwarding
- **Label**: Accesibilidad automática

**Instalación de nuevos componentes:**
```bash
bunx shadcn@latest add <component-name>
```

## Testing

El proyecto usa **Vitest** + **Testing Library**.

### Configuración

- **Framework**: Vitest 4.0.17
- **Environment**: jsdom (DOM simulation)
- **Setup**: `tests/setup.ts`
- **Config**: `vitest.config.ts`

### Ejecutar Tests

```bash
# Modo watch (recomendado para desarrollo)
bun run test

# Modo watch con patron
bun run test -- auth

# Single run
bun run test -- --run

# UI interactiva
bun run test:ui

# Coverage
bun run test:coverage
```

### Tests Actuales

- **setup.test.ts**: 2 tests básicos de configuración

### Escribir Tests

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

## Code Quality

### Biome (Linter + Formatter)

Configuración en `biome.json`:

```json
{
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "semicolons": "asNeeded"
    }
  }
}
```

**Comandos:**
```bash
# Check issues
bun run lint

# Autofix
bun run lint:fix

# Format
bun run format
```

### Convenciones de Código

**Nombres de archivos:**
- Componentes: `PascalCase.tsx` (ej: `LoginForm.tsx`)
- Hooks: `camelCase.ts` (ej: `useLogin.ts`)
- Utilities: `camelCase.ts` (ej: `constants.ts`)
- Types: `camelCase.types.ts` (ej: `auth.types.ts`)
- Stores: `camelCase.ts` (ej: `authStore.ts`)

**Código:**
- Componentes: `PascalCase`
- Functions/Variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types/Interfaces: `PascalCase`
- Hooks: Prefijo `use` + `PascalCase` (ej: `useLogin`)

**Imports:**
- Preferir named exports sobre default exports
- Usar alias `@` para imports absolutos
- Agrupar imports: React → third-party → local

**TypeScript:**
- Mode estricto habilitado
- Type annotations explícitas en funciones públicas
- Evitar `any`, usar `unknown` si es necesario
- Preferir interfaces sobre types para objetos

## Configuración

### TypeScript

**Tres archivos de configuración:**

1. **tsconfig.json**: Project references
2. **tsconfig.app.json**: Configuración de la app
3. **tsconfig.bun.json**: Configuración para Vite (usa Bun types)

**Configuración estricta:**
- `strict: true`
- `noUncheckedIndexedAccess: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`

### Vite

**Path alias:**
```typescript
// vite.config.ts
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
}
```

**Uso:**
```typescript
// ❌ Imports relativos
import { Button } from '../../../components/ui/button'

// ✅ Imports absolutos con alias
import { Button } from '@/components/ui/button'
```

### Tailwind CSS

**Versión 4** con nuevas features:
- Tailwind v4 syntax
- PostCSS plugin: `@tailwindcss/postcss`
- Oxide engine (ultra-rápido)
- CSS-first configuration

**Configuración en `tailwind.config.js`:**
```javascript
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  // ...
}
```

## Estructura de Features

Cada feature sigue esta estructura:

```
features/
└── feature-name/
    ├── api/              # API calls
    ├── components/       # UI components específicos
    ├── hooks/           # React Query hooks y custom hooks
    ├── pages/           # Páginas de la feature
    ├── stores/          # Zustand stores (si aplica)
    ├── types/           # TypeScript types
    ├── utils/           # Utilidades específicas
    └── index.ts         # Barrel export
```

**Ejemplo de barrel export:**
```typescript
// features/auth/index.ts
export * from './api/authApi'
export * from './hooks/useLogin'
export * from './hooks/useRegister'
export * from './components/LoginForm'
export * from './components/RegisterForm'
export * from './types/auth.types'
```

## Performance

### Optimizaciones Implementadas

1. **Code Splitting**: Automático por Vite
2. **Tree Shaking**: Elimina código no usado
3. **Lazy Loading**: React.lazy para rutas
4. **React Query Cache**: Reduce requests redundantes
5. **Zustand**: State management ligero y performante
6. **Bun**: Runtime ultra-rápido

### Best Practices

- Usar `React.memo` para componentes pesados
- Lazy load de rutas con `React.lazy`
- Virtualización para listas largas
- Debounce en inputs de búsqueda
- Optimistic updates con React Query

## Build

### Producción

```bash
# Build
bun run build

# Output en dist/
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   └── index-[hash].css
└── ...
```

**Características del build:**
- Minificación de JS y CSS
- Tree shaking
- Code splitting automático
- Source maps (opcional)
- Gzip compression

### Preview

```bash
bun run preview
```

Sirve el build de producción en http://localhost:4173

## Roadmap

### Implementado ✅

- Feature-first architecture
- Autenticación completa (login/register)
- Persistencia de sesión
- HTTP client tipo-safe con interceptors
- State management (Zustand + React Query)
- Forms con validación (React Hook Form + Zod)
- UI components (shadcn/ui)
- Routing con React Router 7
- Protected routes
- TypeScript estricto
- Linter y formatter (Biome)
- Testing setup (Vitest)

### Próximas Features

- [ ] Dashboard en tiempo real
- [ ] Tracking de cotizaciones de acciones
- [ ] Gráficos de precios (Chart.js o Recharts)
- [ ] WebSockets para datos en tiempo real
- [ ] Sistema de notificaciones
- [ ] Filtros y búsqueda de acciones
- [ ] Favoritos y watchlists
- [ ] Dark mode
- [ ] PWA capabilities
- [ ] Tests E2E (Playwright)
- [ ] Storybook para componentes

## Troubleshooting

### Error: Cannot find module '@/...'

**Solución**: Reiniciar el dev server
```bash
# Ctrl+C para detener
bun run dev
```

### Error: Type error en imports de shadcn/ui

**Solución**: Regenerar tipos
```bash
bun run build
```

### Tests no encuentran módulos

**Solución**: Verificar `vitest.config.ts` tiene el alias `@` configurado

## Licencia

Propiedad de Argentum Platform.
