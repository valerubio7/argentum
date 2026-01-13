/**
 * useCurrentUser Hook
 *
 * React Hook for fetching current authenticated user using TanStack Query.
 *
 * Features:
 * - Automatically fetches user data if token exists
 * - Caches user data (controlled by queryClient config)
 * - Updates auth store with fresh user data
 * - Handles token expiration/invalidity
 *
 * Usage:
 * ```tsx
 * const { data: user, isLoading, error } = useCurrentUser()
 *
 * if (isLoading) return <Spinner />
 * if (error) return <ErrorMessage />
 * if (user) return <p>Hello {user.username}</p>
 * ```
 */

import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { QUERY_KEYS } from '@/lib/constants'
import { authApi } from '../api/authApi'
import { useAuthStore } from '../stores/authStore'
import type { User } from '../types/auth.types'

/**
 * Current user query hook
 *
 * Fetches the authenticated user's data from GET /api/auth/me
 * Only runs if a token exists in the auth store.
 */
export function useCurrentUser() {
  const token = useAuthStore((state) => state.token)
  const setUser = useAuthStore((state) => state.setUser)
  const logout = useAuthStore((state) => state.logout)

  const query = useQuery<User>({
    queryKey: QUERY_KEYS.AUTH.CURRENT_USER,
    queryFn: async () => {
      if (!token) {
        throw new Error('No token available')
      }
      const user = await authApi.getCurrentUser(token)
      return user
    },
    enabled: !!token, // Only run if token exists
    retry: false, // Don't retry on 401 errors
    staleTime: 5 * 60 * 1000, // 5 minutes (from queryClient config)
  })

  // Update store when user data is fetched successfully
  useEffect(() => {
    if (query.data) {
      setUser(query.data)
    }
  }, [query.data, setUser])

  // Logout if token is invalid/expired
  useEffect(() => {
    if (query.error) {
      logout()
    }
  }, [query.error, logout])

  return query
}
