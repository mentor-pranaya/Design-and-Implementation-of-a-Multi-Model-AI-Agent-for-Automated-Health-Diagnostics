/**
 * API request and response type definitions
 */

import type {
  BloodReportData,
  UserProfile,
  UserPreferences,
  ReportComparison,
  ParameterTrend,
  AdminMetrics,
  ErrorLogEntry,
  ProviderPatientSummary,
  ReportAnnotation,
  ExportFormat,
} from './domain';

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

/**
 * Generic API error response
 */
export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  timestamp: string;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ============================================================================
// Authentication API Types
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  user: UserProfile;
  token: string;
  refreshToken: string;
  expiresIn: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  age?: number;
  sex?: 'M' | 'F';
  phone?: string;
}

export interface RegisterResponse {
  user: UserProfile;
  token: string;
  refreshToken: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface RefreshTokenResponse {
  token: string;
  refreshToken: string;
  expiresIn: number;
}

// ============================================================================
// Report API Types
// ============================================================================

export interface UploadReportRequest {
  file: File;
  patientId?: string;
  metadata?: {
    reportDate?: string;
    labName?: string;
    doctorName?: string;
    notes?: string;
  };
}

export interface UploadReportResponse {
  reportId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

export interface ReportStatusRequest {
  reportId: string;
}

export interface ReportStatusResponse {
  reportId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  error?: string;
  estimatedTimeRemaining?: number;
}

export interface GetReportDataRequest {
  reportId: string;
}

export interface GetReportDataResponse {
  report: BloodReportData;
}

export interface GetReportHistoryRequest {
  patientId?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
  sortBy?: 'date' | 'riskScore';
  sortOrder?: 'asc' | 'desc';
}

export interface GetReportHistoryResponse extends PaginatedResponse<BloodReportData> {}

export interface CompareReportsRequest {
  reportId1: string;
  reportId2: string;
}

export interface CompareReportsResponse {
  comparison: ReportComparison;
}

export interface ExportReportRequest {
  reportId: string;
  format: ExportFormat;
  options?: {
    includeParameters?: boolean;
    includeRecommendations?: boolean;
    includeCharts?: boolean;
    includeMetadata?: boolean;
  };
}

export interface ExportReportResponse {
  downloadUrl: string;
  fileName: string;
  fileSize: number;
  expiresAt: string;
}

export interface GetTrendDataRequest {
  patientId: string;
  parameterIds: string[];
  startDate?: string;
  endDate?: string;
}

export interface GetTrendDataResponse {
  trends: ParameterTrend[];
}

// ============================================================================
// User API Types
// ============================================================================

export interface UpdateProfileRequest {
  name?: string;
  age?: number;
  sex?: 'M' | 'F';
  phone?: string;
}

export interface UpdateProfileResponse {
  user: UserProfile;
}

export interface UpdatePreferencesRequest {
  preferences: Partial<UserPreferences>;
}

export interface UpdatePreferencesResponse {
  preferences: UserPreferences;
}

export interface GetPreferencesResponse {
  preferences: UserPreferences;
}

// ============================================================================
// Provider API Types
// ============================================================================

export interface GetProviderPatientsRequest {
  search?: string;
  filterBy?: {
    riskLevel?: 'low' | 'moderate' | 'high' | 'critical';
    hasAbnormalParameters?: boolean;
    dateRange?: {
      start: string;
      end: string;
    };
  };
  sortBy?: 'name' | 'date' | 'riskScore' | 'abnormalCount';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}

export interface GetProviderPatientsResponse extends PaginatedResponse<ProviderPatientSummary> {}

export interface AddAnnotationRequest {
  reportId: string;
  content: string;
  category?: string;
}

export interface AddAnnotationResponse {
  annotation: ReportAnnotation;
}

export interface GetAnnotationsRequest {
  reportId: string;
}

export interface GetAnnotationsResponse {
  annotations: ReportAnnotation[];
}

export interface BatchExportRequest {
  reportIds: string[];
  format: ExportFormat;
}

export interface BatchExportResponse {
  downloadUrl: string;
  fileName: string;
  fileSize: number;
  expiresAt: string;
}

// ============================================================================
// Admin API Types
// ============================================================================

export interface GetMetricsRequest {
  startDate?: string;
  endDate?: string;
  granularity?: 'hour' | 'day' | 'week' | 'month';
}

export interface GetMetricsResponse {
  metrics: AdminMetrics;
  timeSeries?: Array<{
    timestamp: string;
    value: number;
  }>;
}

export interface GetErrorLogsRequest {
  severity?: 'low' | 'medium' | 'high' | 'critical';
  category?: string;
  startDate?: string;
  endDate?: string;
  resolved?: boolean;
  page?: number;
  pageSize?: number;
}

export interface GetErrorLogsResponse extends PaginatedResponse<ErrorLogEntry> {}

export interface ExportMetricsRequest {
  startDate: string;
  endDate: string;
  format: 'csv' | 'json';
}

export interface ExportMetricsResponse {
  downloadUrl: string;
  fileName: string;
  expiresAt: string;
}

// ============================================================================
// Validation Types
// ============================================================================

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationErrorResponse extends ApiError {
  error: {
    code: 'VALIDATION_ERROR';
    message: string;
    details: {
      errors: ValidationError[];
    };
  };
}