/**
 * Report Details Page
 * Detailed view of a blood report with all parameters and visualizations
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Printer, Share2, Loader2 } from 'lucide-react';
import Layout from '@/components/Layout';
import ParameterCard from '@/components/ParameterCard';
import { useCurrentReport } from '@/hooks/useReportStore';
import { reportService } from '@/services/reportService';
import type { BloodReportData } from '@/types/domain';

export default function ReportDetailsPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const navigate = useNavigate();
  const { report: storeReport, setReport } = useCurrentReport();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setLocalReport] = useState<BloodReportData | null>(storeReport);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    // If report is not in store, fetch it
    if (!storeReport && reportId) {
      fetchReport(reportId);
    } else if (storeReport) {
      setLocalReport(storeReport);
    }
  }, [reportId, storeReport]);

  const fetchReport = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await reportService.getReportData(id);
      setLocalReport(response.report);
      setReport(response.report);
    } catch (err: any) {
      setError(err.message || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'pdf' | 'png' | 'csv') => {
    if (!reportId) return;
    try {
      const response = await reportService.exportReport(reportId, format);
      window.open(response.downloadUrl, '_blank');
    } catch (err: any) {
      alert('Export failed: ' + err.message);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Loading report...</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="mt-4 btn-secondary"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  if (!report) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <p className="text-gray-600 dark:text-gray-400">Report not found</p>
        </div>
      </Layout>
    );
  }

  // Get unique categories
  const categories = ['all', ...new Set(report.parameters.map(p => p.category).filter((c): c is string => Boolean(c)))];

  // Filter parameters by category
  const filteredParameters = selectedCategory === 'all'
    ? report.parameters
    : report.parameters.filter(p => p.category === selectedCategory);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/history')}
            className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to History</span>
          </button>

          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Blood Report Analysis
              </h1>
              <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                <span>Report Date: {new Date(report.reportDate).toLocaleDateString()}</span>
                <span>•</span>
                <span>Uploaded: {new Date(report.uploadDate).toLocaleDateString()}</span>
                {report.patientName && (
                  <>
                    <span>•</span>
                    <span>Patient: {report.patientName}</span>
                  </>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-2 mt-4 md:mt-0">
              <button
                onClick={() => handleExport('pdf')}
                className="btn-secondary flex items-center space-x-2"
                title="Export as PDF"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">PDF</span>
              </button>
              <button
                onClick={handlePrint}
                className="btn-secondary flex items-center space-x-2"
                title="Print"
              >
                <Printer className="w-4 h-4" />
                <span className="hidden sm:inline">Print</span>
              </button>
              <button
                className="btn-secondary flex items-center space-x-2"
                title="Share"
              >
                <Share2 className="w-4 h-4" />
                <span className="hidden sm:inline">Share</span>
              </button>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Parameters</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {report.summary.totalParameters}
            </p>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
            <p className="text-sm text-green-600 dark:text-green-400 mb-1">Normal</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {report.summary.normalCount}
            </p>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-600 dark:text-red-400 mb-1">High</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">
              {report.summary.highCount}
            </p>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
            <p className="text-sm text-orange-600 dark:text-orange-400 mb-1">Low</p>
            <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {report.summary.lowCount}
            </p>
          </div>
        </div>

        {/* Category Filter */}
        {categories.length > 1 && (
          <div className="mb-6">
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {category === 'all' ? 'All Parameters' : category}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Parameters Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredParameters.map((parameter) => (
            <ParameterCard
              key={parameter.id}
              parameter={parameter}
              showTrend={true}
            />
          ))}
        </div>

        {/* Health Risk Score */}
        {report.healthRiskScore && (
          <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Health Risk Assessment
            </h2>
            
            {/* Overall Risk Level */}
            <div className="mb-6 p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Overall Risk Level</p>
                  <p className={`text-3xl font-bold capitalize ${
                    report.healthRiskScore.level === 'low' ? 'text-green-600' :
                    report.healthRiskScore.level === 'moderate' ? 'text-yellow-600' :
                    report.healthRiskScore.level === 'high' ? 'text-orange-600' :
                    'text-red-600'
                  }`}>
                    {report.healthRiskScore.level}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Risk Score</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {report.healthRiskScore.overall}/100
                  </p>
                </div>
              </div>
            </div>
            
            {/* Category Scores */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Cardiovascular</p>
                <div className="flex items-baseline gap-1">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {report.healthRiskScore.cardiovascular}
                  </p>
                  <p className="text-sm text-gray-500">/100</p>
                </div>
              </div>
              <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Metabolic</p>
                <div className="flex items-baseline gap-1">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {report.healthRiskScore.metabolic}
                  </p>
                  <p className="text-sm text-gray-500">/100</p>
                </div>
              </div>
              <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Kidney</p>
                <div className="flex items-baseline gap-1">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {report.healthRiskScore.kidney}
                  </p>
                  <p className="text-sm text-gray-500">/100</p>
                </div>
              </div>
              <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Liver</p>
                <div className="flex items-baseline gap-1">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {report.healthRiskScore.liver}
                  </p>
                  <p className="text-sm text-gray-500">/100</p>
                </div>
              </div>
            </div>
            
            {/* Risk Level Legend */}
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Risk Levels:</p>
              <div className="flex flex-wrap gap-4 text-xs">
                <span className="text-green-600">● Low (0-25)</span>
                <span className="text-yellow-600">● Moderate (26-50)</span>
                <span className="text-orange-600">● High (51-75)</span>
                <span className="text-red-600">● Critical (76-100)</span>
              </div>
            </div>
          </div>
        )}

        {/* Recommendations */}
        {report.recommendations && report.recommendations.length > 0 && (
          <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Recommendations
            </h2>
            <div className="space-y-4">
              {report.recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="border-l-4 border-primary-600 pl-4 py-2"
                >
                  <div className="flex items-start justify-between">
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {rec.title}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        rec.priority === 'high'
                          ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
                          : rec.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400'
                          : 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                      }`}
                    >
                      {rec.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {rec.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
