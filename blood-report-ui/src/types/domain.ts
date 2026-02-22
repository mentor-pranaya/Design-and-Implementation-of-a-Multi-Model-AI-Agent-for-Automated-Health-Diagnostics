/**
 * Domain model type definitions
 * Core business entities for the blood report application
 */

// Classification types
export type ClassificationType = 'Normal' | 'High' | 'Low' | 'Unknown';

// User roles
export type UserRole = 'patient' | 'provider' | 'admin';

// Export formats
export type ExportFormat = 'pdf' | 'png' | 'csv';

// Theme types
export type ThemeMode = 'light' | 'dark' | 'system';

/**
 * Reference range for a blood parameter
 */
export interface ReferenceRange {
  min: number;
  max: number;
  unit: string;
  ageMin?: number;
  ageMax?: number;
  sex?: 'M' | 'F' | 'All';
  context?: string;
}

/**
 * Blood parameter with value and classification
 */
export interface BloodParameter {
  id: string;
  name: string;
  value: number | string;
  unit: string;
  classification: ClassificationType;
  referenceRange: ReferenceRange;
  category?: string;
  description?: string;
  trend?: 'increasing' | 'decreasing' | 'stable';
  previousValue?: number | string;
  percentChange?: number;
}

/**
 * Health recommendation
 */
export interface Recommendation {
  id: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  title: string;
  description: string;
  relatedParameters: string[];
  actionable: boolean;
}

/**
 * Health risk score
 */
export interface HealthRiskScore {
  overall: number;
  cardiovascular: number;
  metabolic: number;
  kidney: number;
  liver: number;
  level: 'low' | 'moderate' | 'high' | 'critical';
}

/**
 * Complete blood report data
 */
export interface BloodReportData {
  id: string;
  reportDate: string;
  uploadDate: string;
  patientId: string;
  patientName?: string;
  patientAge?: number;
  patientSex?: 'M' | 'F';
  parameters: BloodParameter[];
  healthRiskScore: HealthRiskScore;
  recommendations: Recommendation[];
  summary: {
    totalParameters: number;
    normalCount: number;
    highCount: number;
    lowCount: number;
    unknownCount: number;
  };
  metadata?: {
    labName?: string;
    doctorName?: string;
    notes?: string;
  };
}

/**
 * User profile
 */
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  age?: number;
  sex?: 'M' | 'F';
  phone?: string;
  createdAt: string;
  lastLogin?: string;
}

/**
 * User preferences
 */
export interface UserPreferences {
  theme: ThemeMode;
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  defaultExportFormat: ExportFormat;
  showTrends: boolean;
  showRecommendations: boolean;
}

/**
 * Authentication state
 */
export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  expiresAt: number | null;
  loading: boolean;
  error: string | null;
}

/**
 * Report comparison data
 */
export interface ReportComparison {
  reportId1: string;
  reportId2: string;
  date1: string;
  date2: string;
  parameterChanges: Array<{
    parameterId: string;
    name: string;
    value1: number | string;
    value2: number | string;
    change: number;
    percentChange: number;
    classification1: ClassificationType;
    classification2: ClassificationType;
    significant: boolean;
  }>;
}

/**
 * Upload progress state
 */
export interface UploadProgress {
  fileId: string;
  fileName: string;
  fileSize: number;
  uploadedBytes: number;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  error?: string;
  estimatedTimeRemaining?: number;
}

/**
 * Trend data point
 */
export interface TrendDataPoint {
  date: string;
  value: number;
  classification: ClassificationType;
  reportId: string;
}

/**
 * Parameter trend
 */
export interface ParameterTrend {
  parameterId: string;
  parameterName: string;
  unit: string;
  dataPoints: TrendDataPoint[];
  referenceRange: ReferenceRange;
  trend: 'increasing' | 'decreasing' | 'stable';
  averageValue: number;
  minValue: number;
  maxValue: number;
}

/**
 * Admin metrics
 */
export interface AdminMetrics {
  reportsProcessed: number;
  successRate: number;
  averageProcessingTime: number;
  extractionAccuracy: number;
  classificationAccuracy: number;
  activeUsers: number;
  storageUsed: number;
  errorRate: number;
  period: {
    start: string;
    end: string;
  };
}

/**
 * Error log entry
 */
export interface ErrorLogEntry {
  id: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  message: string;
  stackTrace?: string;
  userId?: string;
  reportId?: string;
  resolved: boolean;
}

/**
 * Provider patient summary
 */
export interface ProviderPatientSummary {
  patientId: string;
  patientName: string;
  lastReportDate: string;
  reportCount: number;
  riskLevel: 'low' | 'moderate' | 'high' | 'critical';
  abnormalParameterCount: number;
  hasAnnotations: boolean;
}

/**
 * Report annotation
 */
export interface ReportAnnotation {
  id: string;
  reportId: string;
  providerId: string;
  providerName: string;
  timestamp: string;
  content: string;
  category?: string;
}