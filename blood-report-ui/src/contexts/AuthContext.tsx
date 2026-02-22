/**
 * Authentication Context
 * Provides authentication state and methods throughout the app
 */

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import type { AuthState, UserProfile, LoginRequest, RegisterRequest } from '@/types';
import { authService } from '@/services/authService';
import { httpClient } from '@/services/httpClient';
import { env } from '@/utils/env';

interface AuthContextValue extends AuthState {
  login: (request: LoginRequest) => Promise<void>;
  register: (request: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    refreshToken: null,
    expiresAt: null,
    loading: true,
    error: null,
  });

  // Session timeout timer
  const [timeoutId, setTimeoutId] = useState<ReturnType<typeof setTimeout> | null>(null);

  /**
   * Clear session timeout
   */
  const clearSessionTimeout = useCallback(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      setTimeoutId(null);
    }
  }, [timeoutId]);

  /**
   * Set session timeout (30 minutes of inactivity)
   */
  const setSessionTimeout = useCallback(() => {
    clearSessionTimeout();
    
    const timeout = setTimeout(async () => {
      console.log('Session timeout - logging out');
      await logout();
    }, env.SESSION_TIMEOUT);
    
    setTimeoutId(timeout);
  }, [clearSessionTimeout]);

  /**
   * Reset session timeout on user activity
   */
  const resetSessionTimeout = useCallback(() => {
    if (state.isAuthenticated) {
      setSessionTimeout();
    }
  }, [state.isAuthenticated, setSessionTimeout]);

  /**
   * Initialize authentication state
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = authService.getToken();
        
        if (token && authService.isAuthenticated()) {
          // Set auth header
          httpClient.setAuthToken(token);
          
          // TODO: Fetch user profile from API
          // For now, parse user from token
          const payload = parseJwt(token);
          const user: UserProfile = {
            id: payload.sub || payload.userId,
            email: payload.email,
            name: payload.name || 'User',
            role: payload.role || 'patient',
            createdAt: new Date().toISOString(),
          };
          
          setState({
            isAuthenticated: true,
            user,
            token,
            refreshToken: authService.getRefreshToken(),
            expiresAt: payload.exp * 1000,
            loading: false,
            error: null,
          });
          
          // Set session timeout
          setSessionTimeout();
        } else {
          setState(prev => ({ ...prev, loading: false }));
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        setState(prev => ({ ...prev, loading: false }));
      }
    };

    initAuth();
  }, [setSessionTimeout]);

  /**
   * Set up activity listeners for session timeout
   */
  useEffect(() => {
    if (state.isAuthenticated) {
      const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
      
      events.forEach(event => {
        document.addEventListener(event, resetSessionTimeout);
      });
      
      return () => {
        events.forEach(event => {
          document.removeEventListener(event, resetSessionTimeout);
        });
      };
    }
    return undefined;
  }, [state.isAuthenticated, resetSessionTimeout]);

  /**
   * Login user
   */
  const login = useCallback(async (request: LoginRequest) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await authService.login(request);
      
      setState({
        isAuthenticated: true,
        user: response.user,
        token: response.token,
        refreshToken: response.refreshToken,
        expiresAt: Date.now() + response.expiresIn * 1000,
        loading: false,
        error: null,
      });
      
      // Set session timeout
      setSessionTimeout();
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.error?.message || 'Login failed',
      }));
      throw error;
    }
  }, [setSessionTimeout]);

  /**
   * Register new user
   */
  const register = useCallback(async (request: RegisterRequest) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await authService.register(request);
      
      setState({
        isAuthenticated: true,
        user: response.user,
        token: response.token,
        refreshToken: response.refreshToken,
        expiresAt: Date.now() + 3600 * 1000, // 1 hour default
        loading: false,
        error: null,
      });
      
      // Set session timeout
      setSessionTimeout();
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.error?.message || 'Registration failed',
      }));
      throw error;
    }
  }, [setSessionTimeout]);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearSessionTimeout();
      setState({
        isAuthenticated: false,
        user: null,
        token: null,
        refreshToken: null,
        expiresAt: null,
        loading: false,
        error: null,
      });
    }
  }, [clearSessionTimeout]);

  /**
   * Refresh authentication
   */
  const refreshAuth = useCallback(async () => {
    try {
      const refreshToken = authService.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await authService.refreshToken({ refreshToken });
      
      setState(prev => ({
        ...prev,
        token: response.token,
        refreshToken: response.refreshToken,
        expiresAt: Date.now() + response.expiresIn * 1000,
      }));
      
      // Reset session timeout
      setSessionTimeout();
    } catch (error) {
      console.error('Token refresh error:', error);
      await logout();
    }
  }, [logout, setSessionTimeout]);

  const value: AuthContextValue = {
    ...state,
    login,
    register,
    logout,
    refreshAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Parse JWT token
 */
function parseJwt(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    return {};
  }
}
