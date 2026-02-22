/**
 * Authentication Service
 * Handles user authentication, token management, and session handling
 */

import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  ApiResponse,
} from '@/types';
import { httpClient } from './httpClient';
import { API_ENDPOINTS, STORAGE_KEYS } from '@/utils/constants';

class AuthService {
  private tokenKey = STORAGE_KEYS.AUTH_TOKEN;
  private refreshTokenKey = STORAGE_KEYS.REFRESH_TOKEN;

  async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await httpClient.post<ApiResponse<LoginResponse>>(
      API_ENDPOINTS.AUTH.LOGIN,
      request
    );

    // Store tokens
    this.setToken(response.data.token);
    localStorage.setItem(this.refreshTokenKey, response.data.refreshToken);

    // Set auth header for subsequent requests
    httpClient.setAuthToken(response.data.token);

    return response.data;
  }

  async register(request: RegisterRequest): Promise<RegisterResponse> {
    const response = await httpClient.post<ApiResponse<RegisterResponse>>(
      API_ENDPOINTS.AUTH.REGISTER,
      request
    );

    // Store tokens
    this.setToken(response.data.token);
    localStorage.setItem(this.refreshTokenKey, response.data.refreshToken);

    // Set auth header for subsequent requests
    httpClient.setAuthToken(response.data.token);

    return response.data;
  }

  async refreshToken(
    request: RefreshTokenRequest
  ): Promise<RefreshTokenResponse> {
    const response = await httpClient.post<
      ApiResponse<RefreshTokenResponse>
    >(API_ENDPOINTS.AUTH.REFRESH, request);

    // Update stored tokens
    this.setToken(response.data.token);
    localStorage.setItem(this.refreshTokenKey, response.data.refreshToken);

    // Update auth header
    httpClient.setAuthToken(response.data.token);

    return response.data;
  }

  async logout(): Promise<void> {
    try {
      // Call logout endpoint
      await httpClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      // Continue with local cleanup even if API call fails
      console.error('Logout API call failed:', error);
    } finally {
      // Clear local storage
      this.clearToken();
      localStorage.removeItem(this.refreshTokenKey);

      // Clear auth header
      httpClient.clearAuthToken();
    }
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  clearToken(): void {
    localStorage.removeItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    // Check if token is expired
    try {
      const payload = this.parseJwt(token);
      const now = Date.now() / 1000;
      return payload.exp > now;
    } catch {
      return false;
    }
  }

  /**
   * Parse JWT token to extract payload
   */
  private parseJwt(token: string): any {
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
      throw new Error('Invalid token format');
    }
  }

  /**
   * Get refresh token from storage
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshTokenKey);
  }

  /**
   * Attempt to refresh the authentication token
   */
  async attemptTokenRefresh(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      await this.refreshToken({ refreshToken });
      return true;
    } catch (error) {
      // Refresh failed, clear tokens
      this.clearToken();
      localStorage.removeItem(this.refreshTokenKey);
      return false;
    }
  }
}

// Create and export singleton instance
export const authService = new AuthService();

export default authService;
