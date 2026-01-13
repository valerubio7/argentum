/**
 * Auth-related TypeScript types and interfaces
 * These match the backend API schemas
 */

/**
 * User entity - matches backend UserResponse schema
 */
export interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  is_verified: boolean
  created_at: string // ISO 8601 date string
}

/**
 * Login request payload
 * Matches backend LoginRequest schema
 */
export interface LoginRequest {
  email: string
  password: string
}

/**
 * Register request payload
 * Matches backend RegisterRequest schema
 */
export interface RegisterRequest {
  email: string
  password: string
  username: string
}

/**
 * Token response from login endpoint
 */
export interface TokenResponse {
  access_token: string
  token_type: string
  expires_at: string | null
}

/**
 * API Error response structure from backend
 */
export interface ApiErrorResponse {
  detail: string
}

/**
 * Generic API error class
 * Used throughout the application for API errors
 */
export class ApiError extends Error {
  statusCode?: number
  details?: unknown

  constructor(message: string, statusCode?: number, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.details = details
  }
}
