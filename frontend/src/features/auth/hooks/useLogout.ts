/**
 * useLogout Hook
 *
 * React Hook for user logout.
 *
 * Features:
 * - Clears auth store (user and token)
 * - Clears all cached queries
 * - Removes token from localStorage
 *
 * Usage:
 * ```tsx
 * const logout = useLogout()
 *
 * <button onClick={logout}>
 *   Logout
 * </button>
 * ```
 */

import { useCallback } from 'react'
import { clearQueryCache } from '@/lib/api/queryClient'
import { useAuthStore } from '../stores/authStore'

/**
 * Logout hook
 *
 * Returns a callback function that:
 * 1. Clears auth store (user, token, isAuthenticated)
 * 2. Clears all TanStack Query cache
 * 3. Token is automatically removed from localStorage (Zustand persist)
 */
export function useLogout() {
  const logout = useAuthStore((state) => state.logout)

  return useCallback(() => {
    // Clear auth store
    logout()

    // Clear all cached queries (user data, etc.)
    clearQueryCache()
  }, [logout])
}
