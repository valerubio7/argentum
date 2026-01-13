# Phase 2: Core Setup - Completed ✅

This phase establishes the foundation for API communication and state management.

## 📁 Structure Created

```
src/
├── lib/
│   ├── constants.ts         # Global constants and configuration
│   ├── utils.ts             # Utility functions (cn)
│   └── api/
│       ├── client.ts        # HTTP client with JWT support
│       └── queryClient.ts   # TanStack Query configuration
│
└── features/
    └── auth/
        ├── api/
        │   └── authApi.ts   # Auth API functions (login, register, getCurrentUser)
        ├── stores/
        │   └── authStore.ts # Zustand store for auth state
        ├── types/
        │   └── auth.types.ts # TypeScript interfaces
        └── index.ts         # Centralized exports
```

## 🔧 Key Components

### 1. API Client (`lib/api/client.ts`)

Type-safe HTTP client wrapper around `fetch`:

```typescript
// Usage examples
const user = await apiClient.get<User>('/api/auth/me', { token })
const response = await apiClient.post<TokenResponse>('/api/auth/login', { email, password })
```

**Features:**
- Automatic JWT token injection
- Centralized error handling
- Type-safe requests with generics
- Support for all HTTP methods (GET, POST, PUT, PATCH, DELETE)

### 2. TanStack Query Config (`lib/api/queryClient.ts`)

Configures caching and data fetching:

```typescript
// Data is fresh for 5 minutes
staleTime: 5 * 60 * 1000

// Retry logic: don't retry 4xx errors, retry 5xx once
retry: (failureCount, error) => { ... }
```

**Features:**
- Smart caching (5 min stale time)
- Auto-refetch on window focus
- Retry logic for server errors
- Query invalidation helpers

### 3. Auth Store (`features/auth/stores/authStore.ts`)

Global authentication state with Zustand:

```typescript
const { user, token, login, logout } = useAuthStore()

// Login
login(userData, jwtToken)

// Logout
logout()

// Check authentication
const isAuth = useAuthStore(state => state.isAuthenticated)
```

**Features:**
- Persists token to localStorage
- Type-safe state management
- Helper functions for easy access
- Reactive updates across components

### 4. Auth API (`features/auth/api/authApi.ts`)

Wrapper functions for backend endpoints:

```typescript
// Login
const tokenResponse = await authApi.login({ email, password })

// Register
const user = await authApi.register({ email, password, username })

// Get current user
const user = await authApi.getCurrentUser(token)
```

**Maps to backend routes:**
- `POST /api/auth/login`
- `POST /api/auth/register`
- `GET /api/auth/me`

### 5. TypeScript Types (`features/auth/types/auth.types.ts`)

Type definitions matching backend schemas:

```typescript
interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

interface LoginRequest {
  email: string
  password: string
}

interface TokenResponse {
  access_token: string
  token_type: string
  expires_at: string | null
}
```

### 6. Constants (`lib/constants.ts`)

Centralized configuration:

```typescript
// API routes
API_ROUTES.AUTH.LOGIN  // '/api/auth/login'
API_ROUTES.AUTH.REGISTER
API_ROUTES.AUTH.ME

// Storage keys
STORAGE_KEYS.AUTH_TOKEN  // 'auth-token'

// Query keys
QUERY_KEYS.AUTH.CURRENT_USER  // ['auth', 'currentUser']
```

## 🎯 How They Work Together

```
Component
   ↓
useAuthStore (Zustand)
   ↓
authApi.login()
   ↓
apiClient.post()
   ↓
fetch() with JWT token
   ↓
Backend API (FastAPI)
```

**Example flow:**

1. User submits login form
2. Component calls `authApi.login({ email, password })`
3. API client makes `POST /api/auth/login`
4. Backend returns JWT token
5. Component calls `authStore.login(user, token)`
6. Token is saved to localStorage
7. User is redirected to dashboard

## ✅ Best Practices Implemented

1. **Type Safety**: All API calls are typed with TypeScript
2. **Single Responsibility**: Each file has one clear purpose
3. **Centralized Config**: Constants in one place
4. **Error Handling**: Consistent error handling with ApiError class
5. **Code Reuse**: Generic API client used everywhere
6. **Persistence**: Token survives page refresh
7. **Security**: Only token is persisted, user data is re-fetched

## 🧪 Testing

All code compiles without errors:
- ✅ TypeScript compilation passes
- ✅ Biome linting passes
- ✅ Production build succeeds
- ✅ Tests pass (2/2)

## 🚀 Next Steps (Phase 3)

Now we can build:
1. Custom hooks (useLogin, useRegister, useCurrentUser)
2. Login and Register forms
3. Protected routes
4. Auth layouts and pages
