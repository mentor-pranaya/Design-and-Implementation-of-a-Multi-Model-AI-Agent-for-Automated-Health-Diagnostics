/**
 * Upload Page
 * Blood report upload page with drag-and-drop functionality
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { reportService } from '@/services/reportService';
import { useReportStore } from '@/hooks/useReportStore';

export default function UploadPage() {
  const navigate = useNavigate();
  const { setCurrentReport } = useReportStore();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string>('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    
    if (!selectedFile) return;

    // Validate file type
    const validTypes = [
      'application/pdf', 
      'image/png', 
      'image/jpeg', 
      'image/jpg',
      'application/json',
      'text/csv'
    ];
    if (!validTypes.includes(selectedFile.type)) {
      setError('Invalid file type. Please upload a PDF, image (PNG, JPG), JSON, or CSV file.');
      return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setError('File size exceeds 10MB limit.');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setSuccess(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'application/json': ['.json'],
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    multiple: false,
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setProgress(0);
    setProcessingStatus('Uploading file...');

    try {
      // Upload the file with progress tracking
      const uploadResponse = await reportService.uploadReport(file, (uploadProgress) => {
        setProgress(uploadProgress);
      });

      if (uploadResponse.status === 'failed') {
        throw new Error(uploadResponse.message || 'Upload failed');
      }

      const reportId = uploadResponse.reportId;
      setProcessingStatus('Processing report...');

      // Poll for processing completion
      const statusResponse = await reportService.pollReportStatus(reportId, 60, 2000);

      if (statusResponse.status === 'failed') {
        throw new Error(statusResponse.error || 'Report processing failed');
      }

      // Fetch the complete report data
      setProcessingStatus('Loading results...');
      const reportData = await reportService.getReportData(reportId);

      // Store in global state
      setCurrentReport(reportData.report);
      
      setProgress(100);
      setSuccess(true);
      setUploading(false);
      setProcessingStatus('Complete!');

      // Navigate to results
      setTimeout(() => {
        navigate(`/report/${reportId}`);
      }, 1000);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'Upload failed. Please try again.');
      setUploading(false);
      setProgress(0);
      setProcessingStatus('');
    }
  };

  const handleRemove = () => {
    setFile(null);
    setError(null);
    setSuccess(false);
    setProgress(0);
    setProcessingStatus('');
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Upload Blood Report
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Upload your blood test report for instant analysis
          </p>
        </div>

        {/* Upload Area */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          {!file ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              {isDragActive ? (
                <p className="text-lg text-primary-600 dark:text-primary-400">
                  Drop your file here...
                </p>
              ) : (
                <>
                  <p className="text-lg text-gray-700 dark:text-gray-300 mb-2">
                    Drag and drop your blood report here
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                    or click to browse files
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500">
                    Supported formats: PDF, PNG, JPG, JSON, CSV (Max 10MB)
                  </p>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* File Preview */}
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-primary-600 dark:text-primary-400" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                {!uploading && !success && (
                  <button
                    onClick={handleRemove}
                    className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                )}
              </div>

              {/* Processing Status */}
              {uploading && processingStatus && (
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>{processingStatus}</span>
                </div>
              )}

              {/* Progress Bar */}
              {uploading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Success Message */}
              {success && (
                <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span>Upload successful! Redirecting to results...</span>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
                  <AlertCircle className="w-5 h-5" />
                  <span>{error}</span>
                </div>
              )}

              {/* Upload Button */}
              {!uploading && !success && (
                <button
                  onClick={handleUpload}
                  className="w-full btn-primary py-3 text-lg"
                  disabled={uploading}
                >
                  Upload and Analyze
                </button>
              )}

              {/* Retry Button */}
              {error && !uploading && (
                <button
                  onClick={handleUpload}
                  className="w-full btn-secondary py-3 text-lg"
                >
                  Retry Upload
                </button>
              )}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-3">
            Tips for best results:
          </h3>
          <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-400">
            <li>• Ensure the report is clear and readable</li>
            <li>• All parameter values should be visible</li>
            <li>• Upload the complete report (all pages if multiple)</li>
            <li>• Supported formats: PDF, PNG, JPG, JSON, CSV</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}
