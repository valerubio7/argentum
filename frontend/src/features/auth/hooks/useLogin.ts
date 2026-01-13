/**
 * useLogin Hook
 *
 * React Hook for user login using TanStack Query mutation.
 *
 * Features:
 * - Handles login API call
 * - Fetches user data after successful login
 * - Stores user and token in auth store
 * - Returns loading, error, and success states
 *
 * Usage:
 * ```tsx
 * const { mutate: login, isPending, error } = useLogin()
 *
 * const handleSubmit = (data) => {
 *   login(data, {
 *     onSuccess: () => {
 *       navigate('/dashboard')
 *     }
 *   })
 * }
 * ```
 */

import { useMutation } from '@tanstack/react-query'
import { authApi } from '../api/authApi'
import { useAuthStore } from '../stores/authStore'
import type { LoginRequest } from '../types/auth.types'

/**
 * Login mutation hook
 *
 * Handles the complete login flow:
 * 1. Calls POST /api/auth/login
 * 2. Gets JWT token
 * 3. Fetches user data with token
 * 4. Stores both in auth store
 */
export function useLogin() {
  const login = useAuthStore((state) => state.login)

  return useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      // Step 1: Login and get token
      const tokenResponse = await authApi.login(credentials)

      // Step 2: Fetch user data with token
      const user = await authApi.getCurrentUser(tokenResponse.access_token)

      return { user, token: tokenResponse.access_token }
    },
    onSuccess: ({ user, token }) => {
      // Step 3: Store in auth store (also persists to localStorage)
      login(user, token)
    },
  })
}
