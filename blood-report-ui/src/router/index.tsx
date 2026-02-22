/**
 * Router Configuration
 * Defines all application routes with lazy loading
 */

import { createBrowserRouter } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import type { UserRole } from '@/types';

// Lazy load pages for code splitting
const LandingPage = lazy(() => import('@/pages/LandingPage'));
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/RegisterPage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const UploadPage = lazy(() => import('@/pages/UploadPage'));
const HistoryPage = lazy(() => import('@/pages/HistoryPage'));
const ReportDetailsPage = lazy(() => import('@/pages/ReportDetailsPage'));
const ProviderDashboardPage = lazy(() => import('@/pages/ProviderDashboardPage'));
const AdminDashboardPage = lazy(() => import('@/pages/AdminDashboardPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));

// Loading component
function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Loading...</p>
      </div>
    </div>
  );
}

// Wrapper for lazy loaded components
function LazyWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingFallback />}>{children}</Suspense>;
}

/**
 * Create router with authentication state
 */
export function createAppRouter(
  isAuthenticated: boolean,
  userRole?: UserRole
) {
  return createBrowserRouter([
    // Public routes
    {
      path: '/',
      element: (
        <LazyWrapper>
          <LandingPage />
        </LazyWrapper>
      ),
    },
    {
      path: '/login',
      element: (
        <LazyWrapper>
          <LoginPage />
        </LazyWrapper>
      ),
    },
    {
      path: '/register',
      element: (
        <LazyWrapper>
          <RegisterPage />
        </LazyWrapper>
      ),
    },

    // Patient routes
    {
      path: '/dashboard',
      element: (
        <LazyWrapper>
          <ProtectedRoute
            isAuthenticated={isAuthenticated}
            userRole={userRole}
          >
            <DashboardPage />
          </ProtectedRoute>
        </LazyWrapper>
      ),
    },
    {
      path: '/upload',
      element: (
        <LazyWrapper>
          <ProtectedRoute
            isAuthenticated={isAuthenticated}
            userRole={userRole}
          >
            <UploadPage />
          </ProtectedRoute>
        </LazyWrapper>
      ),
    },
    {
      path: '/history',
      element: (
        <LazyWrapper>
          <ProtectedRoute
            isAuthenticated={isAuthenticated}
            userRole={userRole}
          >
            <HistoryPage />
          </ProtectedRoute>
        </LazyWrapper>
      ),
    },
    {
      path: '/report/:reportId',
      element: (
        <LazyWrapper>
          <ProtectedRoute
            isAuthenticated={isAuthenticated}
            userRole={userRole}
          >
            <ReportDetailsPage />
          </ProtectedRoute>
        </LazyWrapper>
      ),
    },

    // Provider routes
    {
      path: '/provider',
      element: (
        <LazyWrapper>
          <ProtectedRoute
            isAuthenticated={isAuthenticated}
            userRole={userRole}
            requiredRole="provider"
          >
            <ProviderDashboardPage />
          </ProtectedRoute>
        </LazyWrapper>
      ),
    },

    // Admin routes
    {
      path: '/admin',
      element: (
        <LazyWrapper>
          <ProtectedRoute
            isAuthenticated={isAuthenticated}
            userRole={userRole}
            requiredRole="admin"
          >
            <AdminDashboardPage />
          </ProtectedRoute>
        </LazyWrapper>
      ),
    },

    // 404 route
    {
      path: '*',
      element: (
        <LazyWrapper>
          <NotFoundPage />
        </LazyWrapper>
      ),
    },
  ]);
}
