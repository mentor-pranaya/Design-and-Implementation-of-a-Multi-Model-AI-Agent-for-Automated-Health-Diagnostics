/**
 * Report Store
 * Zustand store for managing report state
 */

import { create } from 'zustand';
import type { BloodReportData } from '@/types';

interface ReportFilters {
  search: string;
  category?: string;
  classification?: 'Normal' | 'High' | 'Low' | 'Unknown';
  dateRange?: {
    start: string;
    end: string;
  };
}

interface ReportState {
  // Current report
  currentReport: BloodReportData | null;
  currentReportLoading: boolean;
  currentReportError: string | null;

  // Report history
  reportHistory: BloodReportData[];
  historyLoading: boolean;
  historyError: string | null;
  historyPage: number;
  historyTotalPages: number;

  // Filters
  filters: ReportFilters;

  // Selected reports for comparison
  selectedReports: string[];

  // Actions
  setCurrentReport: (report: BloodReportData | null) => void;
  setCurrentReportLoading: (loading: boolean) => void;
  setCurrentReportError: (error: string | null) => void;

  setReportHistory: (reports: BloodReportData[]) => void;
  addToHistory: (report: BloodReportData) => void;
  setHistoryLoading: (loading: boolean) => void;
  setHistoryError: (error: string | null) => void;
  setHistoryPage: (page: number) => void;
  setHistoryTotalPages: (totalPages: number) => void;

  setFilters: (filters: Partial<ReportFilters>) => void;
  resetFilters: () => void;

  toggleReportSelection: (reportId: string) => void;
  clearSelection: () => void;

  reset: () => void;
}

const initialFilters: ReportFilters = {
  search: '',
};

export const useReportStore = create<ReportState>((set) => ({
  // Initial state
  currentReport: null,
  currentReportLoading: false,
  currentReportError: null,

  reportHistory: [],
  historyLoading: false,
  historyError: null,
  historyPage: 1,
  historyTotalPages: 1,

  filters: initialFilters,

  selectedReports: [],

  // Actions
  setCurrentReport: (report) =>
    set({ currentReport: report, currentReportError: null }),

  setCurrentReportLoading: (loading) =>
    set({ currentReportLoading: loading }),

  setCurrentReportError: (error) =>
    set({ currentReportError: error, currentReportLoading: false }),

  setReportHistory: (reports) =>
    set({ reportHistory: reports, historyError: null }),

  addToHistory: (report) =>
    set((state) => ({
      reportHistory: [report, ...state.reportHistory],
    })),

  setHistoryLoading: (loading) =>
    set({ historyLoading: loading }),

  setHistoryError: (error) =>
    set({ historyError: error, historyLoading: false }),

  setHistoryPage: (page) =>
    set({ historyPage: page }),

  setHistoryTotalPages: (totalPages) =>
    set({ historyTotalPages: totalPages }),

  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),

  resetFilters: () =>
    set({ filters: initialFilters }),

  toggleReportSelection: (reportId) =>
    set((state) => {
      const isSelected = state.selectedReports.includes(reportId);
      return {
        selectedReports: isSelected
          ? state.selectedReports.filter((id) => id !== reportId)
          : [...state.selectedReports, reportId],
      };
    }),

  clearSelection: () =>
    set({ selectedReports: [] }),

  reset: () =>
    set({
      currentReport: null,
      currentReportLoading: false,
      currentReportError: null,
      reportHistory: [],
      historyLoading: false,
      historyError: null,
      historyPage: 1,
      historyTotalPages: 1,
      filters: initialFilters,
      selectedReports: [],
    }),
}));
