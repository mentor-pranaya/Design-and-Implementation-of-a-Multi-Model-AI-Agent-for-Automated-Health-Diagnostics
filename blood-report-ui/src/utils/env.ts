/**
 * Environment configuration utility
 * Provides type-safe access to environment variables
 */

export const env = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  API_TIMEOUT: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,

  // Authentication
  JWT_SECRET_KEY: import.meta.env.VITE_JWT_SECRET_KEY || 'dev-secret-key',
  SESSION_TIMEOUT: Number(import.meta.env.VITE_SESSION_TIMEOUT) || 1800000, // 30 minutes

  // Feature Flags
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_EXPORT: import.meta.env.VITE_ENABLE_EXPORT === 'true',
  ENABLE_PROVIDER_FEATURES: import.meta.env.VITE_ENABLE_PROVIDER_FEATURES === 'true',
  ENABLE_ADMIN_FEATURES: import.meta.env.VITE_ENABLE_ADMIN_FEATURES === 'true',

  // Upload Configuration
  MAX_FILE_SIZE: Number(import.meta.env.VITE_MAX_FILE_SIZE) || 10485760, // 10MB
  ALLOWED_FILE_TYPES: import.meta.env.VITE_ALLOWED_FILE_TYPES?.split(',') || ['.pdf', '.png', '.jpg', '.jpeg'],

  // Environment
  NODE_ENV: import.meta.env.VITE_NODE_ENV || 'development',
  IS_DEVELOPMENT: import.meta.env.VITE_NODE_ENV === 'development',
  IS_PRODUCTION: import.meta.env.VITE_NODE_ENV === 'production',
} as const;

// Type for environment variables
export type Environment = typeof env;

// Validation function to ensure required env vars are present
export function validateEnvironment(): void {
  const requiredVars = [
    'API_BASE_URL',
  ] as const;

  const missing = requiredVars.filter(key => !env[key]);
  
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}`
    );
  }
}