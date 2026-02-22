/**
 * Application constants
 */

// Classification types
export const CLASSIFICATION_TYPES = {
  NORMAL: 'Normal',
  HIGH: 'High',
  LOW: 'Low',
  UNKNOWN: 'Unknown',
} as const;

// User roles
export const USER_ROLES = {
  PATIENT: 'patient',
  PROVIDER: 'provider',
  ADMIN: 'admin',
} as const;

// File upload constants
export const UPLOAD_CONSTANTS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ['.pdf', '.png', '.jpg', '.jpeg'],
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks for large file uploads
} as const;

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    REGISTER: '/auth/register',
  },
  REPORTS: {
    UPLOAD: '/reports/upload',
    STATUS: '/reports/status',
    DATA: '/reports/data',
    HISTORY: '/reports/history',
    COMPARE: '/reports/compare',
    EXPORT: '/reports/export',
  },
  ADMIN: {
    METRICS: '/admin/metrics',
    LOGS: '/admin/logs',
    USERS: '/admin/users',
  },
} as const;

// Theme constants
export const THEME_CONSTANTS = {
  STORAGE_KEY: 'blood-report-theme',
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system',
} as const;

// Local storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'blood-report-auth-token',
  REFRESH_TOKEN: 'blood-report-refresh-token',
  USER_PREFERENCES: 'blood-report-user-preferences',
  THEME: 'blood-report-theme',
} as const;

// Export formats
export const EXPORT_FORMATS = {
  PDF: 'pdf',
  PNG: 'png',
  CSV: 'csv',
} as const;

// Chart colors for different classifications
export const CHART_COLORS = {
  NORMAL: '#22c55e',
  HIGH: '#ef4444',
  LOW: '#f59e0b',
  NEUTRAL: '#6b7280',
} as const;