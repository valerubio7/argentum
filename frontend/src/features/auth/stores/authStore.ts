/**
 * Authentication Store (Zustand)
 *
 * Global state management for authentication:
 * - Current user data
 * - JWT token
 * - Authentication status
 *
 * Features:
 * - Persists token to localStorage
 * - Automatically hydrates on app load
 * - Type-safe with TypeScript
 *
 * Usage:
 * ```ts
 * const { user, token, login, logout } = useAuthStore()
 *
 * // Login
 * login(userData, jwtToken)
 *
 * // Logout
 * logout()
 *
 * // Check if authenticated
 * const isAuthenticated = useAuthStore(state => state.isAuthenticated)
 * ```
 */

import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import { STORAGE_KEYS } from '@/lib/constants'
import type { User } from '../types/auth.types'

/**
 * Auth store state interface
 */
interface AuthState {
  /**
   * Current authenticated user
   * null if not authenticated
   */
  user: User | null

  /**
   * JWT access token
   * null if not authenticated
   */
  token: string | null

  /**
   * Computed: whether user is authenticated
   */
  isAuthenticated: boolean

  /**
   * Login action
   * Sets user and token, marks as authenticated
   */
  login: (user: User, token: string) => void

  /**
   * Logout action
   * Clears user and token
   */
  logout: () => void

  /**
   * Update user data
   * Useful after profile updates
   */
  setUser: (user: User) => void

  /**
   * Update token
   * Useful for token refresh
   */
  setToken: (token: string) => void
}

/**
 * Auth store
 *
 * Uses Zustand with persist middleware to save token to localStorage
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,

      // Actions
      login: (user, token) =>
        set({
          user,
          token,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        }),

      setUser: (user) =>
        set({
          user,
        }),

      setToken: (token) =>
        set({
          token,
        }),
    }),
    {
      name: STORAGE_KEYS.AUTH_TOKEN, // localStorage key

      /**
       * Use localStorage for persistence
       */
      storage: createJSONStorage(() => localStorage),

      /**
       * Only persist token, not user data
       * User data will be fetched fresh from /api/auth/me on app load
       *
       * This is more secure: if user is deactivated on backend,
       * frontend will fetch and realize user is no longer valid
       */
      partialize: (state) => ({
        token: state.token,
      }),
    }
  )
)

/**
 * Helper: Get token from store
 * Useful for passing to API client
 */
export const getAuthToken = (): string | null => {
  return useAuthStore.getState().token
}

/**
 * Helper: Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return useAuthStore.getState().isAuthenticated
}
