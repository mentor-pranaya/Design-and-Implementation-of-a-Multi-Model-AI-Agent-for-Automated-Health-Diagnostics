/**
 * Permissions Hook
 * Provides role-based permission checks
 */

import { useAuth } from '@/contexts/AuthContext';
import { useMemo } from 'react';
import type { UserRole } from '@/types';

export function usePermissions() {
  const { user, isAuthenticated } = useAuth();

  const permissions = useMemo(() => {
    if (!isAuthenticated || !user) {
      return {
        canUploadReports: false,
        canViewReports: false,
        canViewHistory: false,
        canExportReports: false,
        canViewProviderDashboard: false,
        canViewPatients: false,
        canAddAnnotations: false,
        canViewAdminDashboard: false,
        canViewMetrics: false,
        canViewErrorLogs: false,
        canManageUsers: false,
        isPatient: false,
        isProvider: false,
        isAdmin: false,
      };
    }

    const role = user.role;

    return {
      // Patient permissions
      canUploadReports: role === 'patient' || role === 'provider' || role === 'admin',
      canViewReports: true,
      canViewHistory: true,
      canExportReports: true,

      // Provider permissions
      canViewProviderDashboard: role === 'provider' || role === 'admin',
      canViewPatients: role === 'provider' || role === 'admin',
      canAddAnnotations: role === 'provider' || role === 'admin',

      // Admin permissions
      canViewAdminDashboard: role === 'admin',
      canViewMetrics: role === 'admin',
      canViewErrorLogs: role === 'admin',
      canManageUsers: role === 'admin',

      // Role checks
      isPatient: role === 'patient',
      isProvider: role === 'provider',
      isAdmin: role === 'admin',
    };
  }, [isAuthenticated, user]);

  const hasRole = (requiredRole: UserRole): boolean => {
    return user?.role === requiredRole;
  };

  const hasAnyRole = (roles: UserRole[]): boolean => {
    return user ? roles.includes(user.role) : false;
  };

  return {
    ...permissions,
    hasRole,
    hasAnyRole,
  };
}
