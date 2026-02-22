/**
 * Auth Actions Hook
 * Provides convenient access to authentication actions
 */

import { useAuth } from '@/contexts/AuthContext';
import { useCallback } from 'react';
import type { LoginRequest, RegisterRequest } from '@/types';

export function useAuthActions() {
  const { login, register, logout, refreshAuth } = useAuth();

  const handleLogin = useCallback(
    async (email: string, password: string, rememberMe?: boolean) => {
      const request: LoginRequest = {
        email,
        password,
        ...(rememberMe !== undefined && { rememberMe }),
      };
      await login(request);
    },
    [login]
  );

  const handleRegister = useCallback(
    async (data: {
      email: string;
      password: string;
      name: string;
      age?: number;
      sex?: 'M' | 'F';
      phone?: string;
    }) => {
      const request: RegisterRequest = data;
      await register(request);
    },
    [register]
  );

  const handleLogout = useCallback(async () => {
    await logout();
  }, [logout]);

  const handleRefresh = useCallback(async () => {
    await refreshAuth();
  }, [refreshAuth]);

  return {
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    refresh: handleRefresh,
  };
}
