/**
 * TanStack Query (React Query) Configuration
 *
 * Configures the QueryClient with:
 * - Default query options (stale time, retry logic)
 * - Global error handling
 * - Cache management
 *
 * Learn more: https://tanstack.com/query/latest/docs/react/overview
 */

import { type DefaultOptions, QueryClient } from '@tanstack/react-query'
import { ApiError } from '@/features/auth/types/auth.types'

/**
 * Default options for all queries and mutations
 */
const defaultOptions: DefaultOptions = {
  queries: {
    /**
     * Data is considered fresh for 5 minutes
     * During this time, no refetch happens automatically
     */
    staleTime: 5 * 60 * 1000, // 5 minutes

    /**
     * Failed queries retry 1 time before showing error
     */
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors (client errors)
      if (error instanceof ApiError && error.statusCode && error.statusCode < 500) {
        return false
      }
      // Retry once for 5xx errors (server errors)
      return failureCount < 1
    },

    /**
     * Refetch on window focus for fresh data
     */
    refetchOnWindowFocus: true,

    /**
     * Don't refetch on component mount if data is fresh
     */
    refetchOnMount: false,
  },
  mutations: {
    /**
     * Mutations don't retry by default
     * User should explicitly retry failed actions
     */
    retry: false,
  },
}

/**
 * Create QueryClient instance
 * This is the central cache manager for all API data
 */
export const queryClient = new QueryClient({
  defaultOptions,
})

/**
 * Helper to clear all cached data
 * Useful on logout
 */
export function clearQueryCache() {
  queryClient.clear()
}

/**
 * Helper to invalidate specific queries
 * Forces refetch of stale data
 *
 * Example:
 * ```ts
 * invalidateQueries(['auth', 'currentUser'])
 * ```
 */
export function invalidateQueries(queryKey: unknown[]) {
  return queryClient.invalidateQueries({ queryKey })
}
