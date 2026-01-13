/**
 * useRegister Hook
 *
 * React Hook for user registration using TanStack Query mutation.
 *
 * Features:
 * - Handles registration API call
 * - Optionally auto-login after successful registration
 * - Returns loading, error, and success states
 *
 * Usage:
 * ```tsx
 * const { mutate: register, isPending, error } = useRegister()
 *
 * const handleSubmit = (data) => {
 *   register(data, {
 *     onSuccess: () => {
 *       // Show success message or redirect to login
 *       navigate('/login')
 *     }
 *   })
 * }
 * ```
 */

import { useMutation } from '@tanstack/react-query'
import { authApi } from '../api/authApi'
import type { RegisterRequest } from '../types/auth.types'

/**
 * Register mutation hook
 *
 * Handles user registration:
 * 1. Calls POST /api/auth/register
 * 2. Returns created user data
 *
 * Note: Does NOT auto-login. User should be redirected to login page.
 * This is a security best practice - requires explicit login after registration.
 */
export function useRegister() {
  return useMutation({
    mutationFn: async (data: RegisterRequest) => {
      // Call register endpoint
      const user = await authApi.register(data)
      return user
    },
  })
}
