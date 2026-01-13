/**
 * Global constants for the application
 */

/**
 * API Base URL - reads from environment variable
 * Defaults to http://localhost:8000 if not set
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * API endpoint paths
 */
export const API_ROUTES = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    ME: '/api/auth/me',
  },
} as const

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth-token',
} as const

/**
 * Query keys for TanStack Query
 * Used for caching and invalidation
 */
export const QUERY_KEYS = {
  AUTH: {
    CURRENT_USER: ['auth', 'currentUser'] as const,
  },
} as const
