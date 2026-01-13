/**
 * HTTP API Client
 *
 * Provides a type-safe wrapper around fetch with:
 * - Automatic JWT token injection
 * - Centralized error handling
 * - Request/response interceptors
 *
 * Usage:
 * ```ts
 * const data = await apiClient.get<User>('/api/auth/me')
 * const response = await apiClient.post<TokenResponse>('/api/auth/login', { email, password })
 * ```
 */

import { ApiError } from '@/features/auth/types/auth.types'
import { API_BASE_URL } from '@/lib/constants'

/**
 * HTTP request options
 */
interface RequestOptions extends Omit<RequestInit, 'body' | 'method'> {
  body?: unknown
  token?: string | null
}

/**
 * API Client class
 */
class ApiClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  /**
   * Generic request method
   * Handles all HTTP methods with automatic:
   * - Token injection
   * - JSON serialization
   * - Error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestOptions & { method: string }
  ): Promise<T> {
    const { body, token, method, headers: customHeaders, ...restOptions } = options

    // Build headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    // Add custom headers
    if (customHeaders) {
      Object.entries(customHeaders).forEach(([key, value]) => {
        if (typeof value === 'string') {
          headers[key] = value
        }
      })
    }

    // Add JWT token if provided
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    // Build request config
    const config: RequestInit = {
      method,
      headers,
      ...restOptions,
    }

    // Add body if present (for POST, PUT, PATCH)
    if (body !== undefined) {
      config.body = JSON.stringify(body)
    }

    try {
      // Make request
      const response = await fetch(`${this.baseURL}${endpoint}`, config)

      // Handle non-OK responses
      if (!response.ok) {
        await this.handleErrorResponse(response)
      }

      // Parse JSON response
      // Special case: 204 No Content returns null
      if (response.status === 204) {
        return null as T
      }

      const data: T = await response.json()
      return data
    } catch (error) {
      // Handle network errors or JSON parse errors
      if (error instanceof ApiError) {
        throw error
      }

      throw new ApiError(
        error instanceof Error ? error.message : 'Network error occurred',
        undefined,
        error
      )
    }
  }

  /**
   * Handle error responses from API
   * Converts HTTP errors into ApiError instances
   */
  private async handleErrorResponse(response: Response): Promise<never> {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`
    let errorDetails: unknown

    try {
      // Try to parse error details from response body
      const errorData = await response.json()
      errorMessage = errorData.detail || errorMessage
      errorDetails = errorData
    } catch {
      // If JSON parsing fails, use default error message
    }

    throw new ApiError(errorMessage, response.status, errorDetails)
  }

  /**
   * GET request
   * @param endpoint - API endpoint path
   * @param options - Request options
   * @returns Parsed response data
   */
  async get<T>(endpoint: string, options: Omit<RequestOptions, 'body'> = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  /**
   * POST request
   * @param endpoint - API endpoint path
   * @param body - Request body (will be JSON stringified)
   * @param options - Request options
   * @returns Parsed response data
   */
  async post<T>(endpoint: string, body?: unknown, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, body, method: 'POST' })
  }

  /**
   * PUT request
   * @param endpoint - API endpoint path
   * @param body - Request body (will be JSON stringified)
   * @param options - Request options
   * @returns Parsed response data
   */
  async put<T>(endpoint: string, body?: unknown, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, body, method: 'PUT' })
  }

  /**
   * PATCH request
   * @param endpoint - API endpoint path
   * @param body - Request body (will be JSON stringified)
   * @param options - Request options
   * @returns Parsed response data
   */
  async patch<T>(endpoint: string, body?: unknown, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, body, method: 'PATCH' })
  }

  /**
   * DELETE request
   * @param endpoint - API endpoint path
   * @param options - Request options
   * @returns Parsed response data
   */
  async delete<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }
}

/**
 * Singleton instance of API client
 * Use this throughout the application
 */
export const apiClient = new ApiClient(API_BASE_URL)

/**
 * Export class for testing purposes
 */
export { ApiClient }
