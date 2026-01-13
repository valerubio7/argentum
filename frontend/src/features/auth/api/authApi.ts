/**
 * Auth API Functions
 *
 * Wrapper functions for authentication endpoints.
 * These functions use the apiClient to make type-safe requests.
 *
 * Endpoints:
 * - POST /api/auth/login
 * - POST /api/auth/register
 * - GET /api/auth/me
 */

import { apiClient } from '@/lib/api/client'
import { API_ROUTES } from '@/lib/constants'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth.types'

/**
 * Login user
 *
 * @param credentials - Email and password
 * @returns Token response with JWT
 * @throws ApiError if login fails
 *
 * Example:
 * ```ts
 * const response = await authApi.login({
 *   email: 'user@example.com',
 *   password: 'password123'
 * })
 * console.log(response.access_token)
 * ```
 */
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  return apiClient.post<TokenResponse>(API_ROUTES.AUTH.LOGIN, credentials)
}

/**
 * Register new user
 *
 * @param data - Email, password, and username
 * @returns Created user data
 * @throws ApiError if registration fails (e.g., duplicate email)
 *
 * Example:
 * ```ts
 * const user = await authApi.register({
 *   email: 'newuser@example.com',
 *   password: 'securepass123',
 *   username: 'john_doe'
 * })
 * console.log(user.id)
 * ```
 */
export async function register(data: RegisterRequest): Promise<User> {
  return apiClient.post<User>(API_ROUTES.AUTH.REGISTER, data)
}

/**
 * Get current authenticated user
 *
 * Requires valid JWT token in Authorization header
 *
 * @param token - JWT access token
 * @returns Current user data
 * @throws ApiError if token is invalid or expired
 *
 * Example:
 * ```ts
 * const user = await authApi.getCurrentUser('jwt-token-here')
 * console.log(user.email)
 * ```
 */
export async function getCurrentUser(token: string): Promise<User> {
  return apiClient.get<User>(API_ROUTES.AUTH.ME, { token })
}

/**
 * Auth API object
 * Export as namespace for cleaner imports
 */
export const authApi = {
  login,
  register,
  getCurrentUser,
}
