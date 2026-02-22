/**
 * Report Store Hooks
 * Convenient hooks for accessing report store with selectors
 */

import { useReportStore as useStore } from '@/stores/reportStore';
import { useMemo } from 'react';

/**
 * Hook to access the full report store
 * Use specific hooks below for better performance
 */
export function useReportStore() {
  return useStore();
}

/**
 * Hook to get current report state
 */
export function useCurrentReport() {
  const report = useStore((state) => state.currentReport);
  const loading = useStore((state) => state.currentReportLoading);
  const error = useStore((state) => state.currentReportError);
  const setReport = useStore((state) => state.setCurrentReport);
  const setLoading = useStore((state) => state.setCurrentReportLoading);
  const setError = useStore((state) => state.setCurrentReportError);

  return {
    report,
    loading,
    error,
    setReport,
    setLoading,
    setError,
  };
}

/**
 * Hook to get report history state
 */
export function useReportHistory() {
  const history = useStore((state) => state.reportHistory);
  const loading = useStore((state) => state.historyLoading);
  const error = useStore((state) => state.historyError);
  const page = useStore((state) => state.historyPage);
  const totalPages = useStore((state) => state.historyTotalPages);
  const setHistory = useStore((state) => state.setReportHistory);
  const addToHistory = useStore((state) => state.addToHistory);
  const setLoading = useStore((state) => state.setHistoryLoading);
  const setError = useStore((state) => state.setHistoryError);
  const setPage = useStore((state) => state.setHistoryPage);
  const setTotalPages = useStore((state) => state.setHistoryTotalPages);

  return {
    history,
    loading,
    error,
    page,
    totalPages,
    setHistory,
    addToHistory,
    setLoading,
    setError,
    setPage,
    setTotalPages,
  };
}

/**
 * Hook to get filtered report history
 */
export function useFilteredReports() {
  const history = useStore((state) => state.reportHistory);
  const filters = useStore((state) => state.filters);

  const filteredReports = useMemo(() => {
    let filtered = [...history];

    // Apply search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(
        (report) =>
          report.patientName?.toLowerCase().includes(searchLower) ||
          report.id.toLowerCase().includes(searchLower)
      );
    }

    // Apply category filter
    if (filters.category) {
      filtered = filtered.filter((report) =>
        report.parameters.some((param) => param.category === filters.category)
      );
    }

    // Apply classification filter
    if (filters.classification) {
      filtered = filtered.filter((report) =>
        report.parameters.some(
          (param) => param.classification === filters.classification
        )
      );
    }

    // Apply date range filter
    if (filters.dateRange) {
      const { start, end } = filters.dateRange;
      filtered = filtered.filter((report) => {
        const reportDate = new Date(report.reportDate);
        const startDate = new Date(start);
        const endDate = new Date(end);
        return reportDate >= startDate && reportDate <= endDate;
      });
    }

    return filtered;
  }, [history, filters]);

  return filteredReports;
}

/**
 * Hook to manage report filters
 */
export function useReportFilters() {
  const filters = useStore((state) => state.filters);
  const setFilters = useStore((state) => state.setFilters);
  const resetFilters = useStore((state) => state.resetFilters);

  return {
    filters,
    setFilters,
    resetFilters,
  };
}

/**
 * Hook to manage report selection
 */
export function useReportSelection() {
  const selectedReports = useStore((state) => state.selectedReports);
  const toggleSelection = useStore((state) => state.toggleReportSelection);
  const clearSelection = useStore((state) => state.clearSelection);

  const isSelected = (reportId: string) => selectedReports.includes(reportId);
  const selectionCount = selectedReports.length;
  const canCompare = selectionCount === 2;

  return {
    selectedReports,
    toggleSelection,
    clearSelection,
    isSelected,
    selectionCount,
    canCompare,
  };
}
