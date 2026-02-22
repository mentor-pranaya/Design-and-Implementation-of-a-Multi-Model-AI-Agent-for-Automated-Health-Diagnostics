/**
 * Zod schemas for API response validation
 * Provides runtime type checking for all API responses
 */

import { z } from 'zod';

// Base schemas
export const ClassificationSchema = z.enum(['Normal', 'High', 'Low', 'Unknown']);

export const ReferenceRangeSchema = z.object({
  min: z.number(),
  max: z.number(),
  unit: z.string(),
  ageMin: z.number().optional(),
  ageMax: z.number().optional(),
  sex: z.enum(['M', 'F', 'All']).optional(),
  context: z.string().optional(),
});

export const BloodParameterSchema = z.object({
  id: z.string(),
  name: z.string(),
  value: z.union([z.number(), z.string()]),
  unit: z.string(),
  classification: ClassificationSchema,
  referenceRange: ReferenceRangeSchema,
  category: z.string().optional(),
  description: z.string().optional(),
  trend: z.enum(['increasing', 'decreasing', 'stable']).optional(),
  previousValue: z.union([z.number(), z.string()]).optional(),
  percentChange: z.number().optional(),
});

export const RecommendationSchema = z.object({
  id: z.string(),
  priority: z.enum(['high', 'medium', 'low']),
  category: z.string(),
  title: z.string(),
  description: z.string(),
  relatedParameters: z.array(z.string()),
  actionable: z.boolean(),
});

export const HealthRiskScoreSchema = z.object({
  overall: z.number().min(0).max(100),
  cardiovascular: z.number().min(0).max(100),
  metabolic: z.number().min(0).max(100),
  kidney: z.number().min(0).max(100),
  liver: z.number().min(0).max(100),
  level: z.enum(['low', 'moderate', 'high', 'critical']),
});

export const BloodReportDataSchema = z.object({
  id: z.string(),
  reportDate: z.string(),
  uploadDate: z.string(),
  patientId: z.string(),
  patientName: z.string().optional(),
  patientAge: z.number().optional(),
  patientSex: z.enum(['M', 'F']).optional(),
  parameters: z.array(BloodParameterSchema),
  healthRiskScore: HealthRiskScoreSchema,
  recommendations: z.array(RecommendationSchema),
  summary: z.object({
    totalParameters: z.number(),
    normalCount: z.number(),
    highCount: z.number(),
    lowCount: z.number(),
    unknownCount: z.number(),
  }),
  metadata: z.object({
    labName: z.string().optional(),
    doctorName: z.string().optional(),
    notes: z.string().optional(),
  }).optional(),
});

// API Response schemas
export const ApiResponseSchema = z.object({
  success: z.boolean(),
  timestamp: z.string(),
});

export const ApiErrorSchema = z.object({
  success: z.literal(false),
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.any().optional(),
  }),
  timestamp: z.string(),
});

export const UploadReportResponseSchema = z.object({
  reportId: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  message: z.string(),
});

export const GetReportStatusResponseSchema = z.object({
  reportId: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  progress: z.number().min(0).max(100),
  message: z.string().optional().nullable(),
  error: z.string().optional().nullable(),
  estimatedTimeRemaining: z.number().optional(),
}).passthrough(); // Allow additional properties

export const GetReportDataResponseSchema = z.object({
  report: BloodReportDataSchema,
});

export const ReportSummarySchema = z.object({
  reportId: z.string(),
  reportDate: z.string(),
  uploadDate: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  summary: z.object({
    totalParameters: z.number(),
    normalCount: z.number(),
    highCount: z.number(),
    lowCount: z.number(),
    criticalCount: z.number(),
  }).optional(),
});

export const ParameterTrendSchema = z.object({
  parameterName: z.string(),
  values: z.array(z.object({
    date: z.string(),
    value: z.number(),
    classification: ClassificationSchema,
  })),
  referenceRange: ReferenceRangeSchema,
});

export const GetReportHistoryResponseSchema = z.object({
  items: z.array(BloodReportDataSchema),
  total: z.number(),
  page: z.number(),
  pageSize: z.number(),
  totalPages: z.number(),
});

export const CompareReportsResponseSchema = z.object({
  comparison: z.object({
    reportId1: z.string(),
    reportId2: z.string(),
    date1: z.string(),
    date2: z.string(),
    parameterChanges: z.array(z.object({
      parameterId: z.string(),
      name: z.string(),
      value1: z.union([z.number(), z.string()]),
      value2: z.union([z.number(), z.string()]),
      change: z.number(),
      percentChange: z.number(),
      classification1: ClassificationSchema,
      classification2: ClassificationSchema,
      significant: z.boolean(),
    })),
  }),
});

export const ExportReportResponseSchema = z.object({
  downloadUrl: z.string(),
  fileName: z.string(),
  fileSize: z.number(),
  expiresAt: z.string(),
});

// Type exports
export type Classification = z.infer<typeof ClassificationSchema>;
export type ReferenceRange = z.infer<typeof ReferenceRangeSchema>;
export type BloodParameter = z.infer<typeof BloodParameterSchema>;
export type Recommendation = z.infer<typeof RecommendationSchema>;
export type HealthRiskScore = z.infer<typeof HealthRiskScoreSchema>;
export type BloodReportData = z.infer<typeof BloodReportDataSchema>;
export type UploadReportResponse = z.infer<typeof UploadReportResponseSchema>;
export type GetReportStatusResponse = z.infer<typeof GetReportStatusResponseSchema>;
export type GetReportDataResponse = z.infer<typeof GetReportDataResponseSchema>;
export type ReportSummary = z.infer<typeof ReportSummarySchema>;
export type GetReportHistoryResponse = z.infer<typeof GetReportHistoryResponseSchema>;
export type ParameterTrend = z.infer<typeof ParameterTrendSchema>;
export type CompareReportsResponse = z.infer<typeof CompareReportsResponseSchema>;
export type ExportReportResponse = z.infer<typeof ExportReportResponseSchema>;
