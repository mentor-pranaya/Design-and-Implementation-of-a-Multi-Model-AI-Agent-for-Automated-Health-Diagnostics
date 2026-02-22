/**
 * Service interface definitions
 * Defines contracts for all API services
 */

import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  UploadReportRequest,
  UploadReportResponse,
  ReportStatusRequest,
  ReportStatusResponse,
  GetReportDataRequest,
  GetReportDataResponse,
  GetReportHistoryRequest,
  GetReportHistoryResponse,
  CompareReportsRequest,
  CompareReportsResponse,
  ExportReportRequest,
  ExportReportResponse,
  GetTrendDataRequest,
  GetTrendDataResponse,
  UpdateProfileRequest,
  UpdateProfileResponse,
  UpdatePreferencesRequest,
  UpdatePreferencesResponse,
  GetPreferencesResponse,
  GetProviderPatientsRequest,
  GetProviderPatientsResponse,
  AddAnnotationRequest,
  AddAnnotationResponse,
  GetAnnotationsRequest,
  GetAnnotationsResponse,
  BatchExportRequest,
  BatchExportResponse,
  GetMetricsRequest,
  GetMetricsResponse,
  GetErrorLogsRequest,
  GetErrorLogsResponse,
  ExportMetricsRequest,
  ExportMetricsResponse,
} from '@/types';

/**
 * Authentication Service Interface
 * Handles user authentication and session management
 */
export interface IAuthService {
  /**
   * Authenticate user with email and password
   */
  login(request: LoginRequest): Promise<LoginResponse>;

  /**
   * Register a new user account
   */
  register(request: RegisterRequest): Promise<RegisterResponse>;

  /**
   * Refresh authentication token
   */
  refreshToken(request: RefreshTokenRequest): Promise<RefreshTokenResponse>;

  /**
   * Logout current user
   */
  logout(): Promise<void>;

  /**
   * Get current authentication token
   */
  getToken(): string | null;

  /**
   * Set authentication token
   */
  setToken(token: string): void;

  /**
   * Clear authentication token
   */
  clearToken(): void;

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean;
}

/**
 * Report Service Interface
 * Handles blood report operations
 */
export interface IReportService {
  /**
   * Upload a blood report file
   * @param request Upload request with file and metadata
   * @param onProgress Optional callback for upload progress
   */
  uploadReport(
    request: UploadReportRequest,
    onProgress?: (progress: number) => void
  ): Promise<UploadReportResponse>;

  /**
   * Get processing status of a report
   */
  getReportStatus(request: ReportStatusRequest): Promise<ReportStatusResponse>;

  /**
   * Get complete report data
   */
  getReportData(request: GetReportDataRequest): Promise<GetReportDataResponse>;

  /**
   * Get report history for a patient
   */
  getReportHistory(
    request: GetReportHistoryRequest
  ): Promise<GetReportHistoryResponse>;

  /**
   * Compare two reports
   */
  compareReports(
    request: CompareReportsRequest
  ): Promise<CompareReportsResponse>;

  /**
   * Export report in specified format
   */
  exportReport(request: ExportReportRequest): Promise<ExportReportResponse>;

  /**
   * Get trend data for parameters
   */
  getTrendData(request: GetTrendDataRequest): Promise<GetTrendDataResponse>;
}

/**
 * User Service Interface
 * Handles user profile and preferences
 */
export interface IUserService {
  /**
   * Update user profile
   */
  updateProfile(request: UpdateProfileRequest): Promise<UpdateProfileResponse>;

  /**
   * Get user preferences
   */
  getPreferences(): Promise<GetPreferencesResponse>;

  /**
   * Update user preferences
   */
  updatePreferences(
    request: UpdatePreferencesRequest
  ): Promise<UpdatePreferencesResponse>;
}

/**
 * Provider Service Interface
 * Handles healthcare provider specific operations
 */
export interface IProviderService {
  /**
   * Get list of patients with their summaries
   */
  getPatients(
    request: GetProviderPatientsRequest
  ): Promise<GetProviderPatientsResponse>;

  /**
   * Add annotation to a patient report
   */
  addAnnotation(
    request: AddAnnotationRequest
  ): Promise<AddAnnotationResponse>;

  /**
   * Get annotations for a report
   */
  getAnnotations(
    request: GetAnnotationsRequest
  ): Promise<GetAnnotationsResponse>;

  /**
   * Export multiple reports in batch
   */
  batchExport(request: BatchExportRequest): Promise<BatchExportResponse>;
}

/**
 * Analytics Service Interface
 * Handles admin analytics and monitoring
 */
export interface IAnalyticsService {
  /**
   * Get system metrics
   */
  getMetrics(request: GetMetricsRequest): Promise<GetMetricsResponse>;

  /**
   * Get error logs
   */
  getErrorLogs(request: GetErrorLogsRequest): Promise<GetErrorLogsResponse>;

  /**
   * Export metrics data
   */
  exportMetrics(
    request: ExportMetricsRequest
  ): Promise<ExportMetricsResponse>;
}

/**
 * HTTP Client Configuration
 */
export interface HttpClientConfig {
  baseURL: string;
  timeout: number;
  headers?: Record<string, string>;
  withCredentials?: boolean;
}

/**
 * HTTP Client Interface
 * Low-level HTTP operations
 */
export interface IHttpClient {
  /**
   * Perform GET request
   */
  get<T>(url: string, config?: any): Promise<T>;

  /**
   * Perform POST request
   */
  post<T>(url: string, data?: any, config?: any): Promise<T>;

  /**
   * Perform PUT request
   */
  put<T>(url: string, data?: any, config?: any): Promise<T>;

  /**
   * Perform PATCH request
   */
  patch<T>(url: string, data?: any, config?: any): Promise<T>;

  /**
   * Perform DELETE request
   */
  delete<T>(url: string, config?: any): Promise<T>;

  /**
   * Set authorization header
   */
  setAuthToken(token: string): void;

  /**
   * Clear authorization header
   */
  clearAuthToken(): void;
}
