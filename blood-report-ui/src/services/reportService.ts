/**
 * Report Service
 * Handles all blood report related API operations with runtime validation
 */

import httpClient from './httpClient';
import type {
  UploadReportResponse,
  ReportStatusResponse,
  GetReportDataResponse,
  GetReportHistoryResponse,
  CompareReportsResponse,
  ExportReportResponse,
} from '@/types/api';
import {
  UploadReportResponseSchema,
  GetReportStatusResponseSchema,
  GetReportDataResponseSchema,
  GetReportHistoryResponseSchema,
  CompareReportsResponseSchema,
  ExportReportResponseSchema,
} from '@/schemas/api.schemas';
import { z } from 'zod';

class ReportService {
  /**
   * Validate API response against schema
   */
  private validate<T>(schema: z.ZodSchema<T>, data: unknown): T {
    try {
      return schema.parse(data);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('API response validation failed:', error.issues);
        console.error('Received data:', JSON.stringify(data, null, 2));
        throw new Error(`Invalid API response format: ${JSON.stringify(error.issues[0])}`);
      }
      throw error;
    }
  }

  /**
   * Upload a blood report file
   * @param file - The report file to upload
   * @param onProgress - Optional callback for upload progress
   */
  async uploadReport(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<UploadReportResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await httpClient.post<UploadReportResponse>('/reports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    return this.validate(UploadReportResponseSchema, response);
  }

  /**
   * Get the processing status of a report
   * @param reportId - The ID of the report
   */
  async getReportStatus(reportId: string): Promise<ReportStatusResponse> {
    const response = await httpClient.get<any>(`/reports/${reportId}/status`);
    return this.validate(GetReportStatusResponseSchema, response) as ReportStatusResponse;
  }

  /**
   * Get the full data of a processed report
   * @param reportId - The ID of the report
   */
  async getReportData(reportId: string): Promise<GetReportDataResponse> {
    const response = await httpClient.get<any>(`/reports/${reportId}`);
    return this.validate(GetReportDataResponseSchema, response) as GetReportDataResponse;
  }

  /**
   * Get the history of all reports for the current user
   * @param page - Page number (optional)
   * @param pageSize - Number of items per page (optional)
   */
  async getReportHistory(
    page?: number,
    pageSize?: number
  ): Promise<GetReportHistoryResponse> {
    const params: Record<string, any> = {};
    if (page !== undefined) params.page = page;
    if (pageSize !== undefined) params.pageSize = pageSize;

    const response = await httpClient.get<any>('/reports/history', {
      params,
    });
    return this.validate(GetReportHistoryResponseSchema, response) as GetReportHistoryResponse;
  }

  /**
   * Compare multiple reports
   * @param reportId1 - First report ID
   * @param reportId2 - Second report ID
   */
  async compareReports(
    reportId1: string,
    reportId2: string
  ): Promise<CompareReportsResponse> {
    const response = await httpClient.post<CompareReportsResponse>('/reports/compare', {
      reportId1,
      reportId2,
    });
    return this.validate(CompareReportsResponseSchema, response);
  }

  /**
   * Export a report in the specified format
   * @param reportId - The ID of the report
   * @param format - Export format (pdf, png, csv)
   * @param options - Export options
   */
  async exportReport(
    reportId: string,
    format: 'pdf' | 'png' | 'csv',
    options?: {
      includeRecommendations?: boolean;
      includeMetadata?: boolean;
    }
  ): Promise<ExportReportResponse> {
    const response = await httpClient.post<ExportReportResponse>(
      `/reports/${reportId}/export`,
      {
        format,
        options,
      }
    );
    return this.validate(ExportReportResponseSchema, response);
  }

  /**
   * Delete a report
   * @param reportId - The ID of the report to delete
   */
  async deleteReport(reportId: string): Promise<{ success: boolean }> {
    return httpClient.delete<{ success: boolean }>(`/reports/${reportId}`);
  }

  /**
   * Poll for report processing completion
   * @param reportId - The ID of the report
   * @param maxAttempts - Maximum number of polling attempts
   * @param interval - Interval between polls in ms
   */
  async pollReportStatus(
    reportId: string,
    maxAttempts: number = 60,
    interval: number = 2000
  ): Promise<ReportStatusResponse> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const status = await this.getReportStatus(reportId);
      
      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, interval));
    }

    throw new Error('Report processing timeout');
  }
}

// Create and export singleton instance
export const reportService = new ReportService();
export default reportService;
