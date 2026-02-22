/**
 * Protected Route Component
 * Wrapper for routes that require authentication
 * 
 * NOTE: Authentication is temporarily disabled for development
 */

import type { UserRole } from '@/types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  isAuthenticated: boolean;
  userRole?: UserRole | undefined;
}

export default function ProtectedRoute({
  children,
}: ProtectedRouteProps) {
  // TEMPORARY: Disable authentication for development
  // TODO: Re-enable authentication when backend is ready
  // Unused parameters: requiredRole, isAuthenticated, userRole
  
  // Check if user is authenticated
  // if (!isAuthenticated) {
  //   return <Navigate to="/login" replace />;
  // }

  // Check if user has required role
  // if (requiredRole && userRole !== requiredRole) {
  //   // Redirect to appropriate dashboard based on role
  //   if (userRole === 'admin') {
  //     return <Navigate to="/admin" replace />;
  //   } else if (userRole === 'provider') {
  //     return <Navigate to="/provider" replace />;
  //   } else {
  //     return <Navigate to="/dashboard" replace />;
  //   }
  // }

  return <>{children}</>;
}
