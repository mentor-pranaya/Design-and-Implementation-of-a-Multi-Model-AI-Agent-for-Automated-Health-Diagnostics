/**
 * HTTP Client implementation using Axios
 * Provides low-level HTTP operations with interceptors and retry logic
 */

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios';
import { env } from '@/utils/env';

interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  retryableStatuses: number[];
}

class HttpClient {
  private client: AxiosInstance;
  private retryConfig: RetryConfig = {
    maxRetries: 3,
    retryDelay: 1000, // Initial delay in ms
    retryableStatuses: [408, 429, 500, 502, 503, 504],
  };

  constructor(config: {
    baseURL: string;
    timeout: number;
    headers?: Record<string, string>;
    withCredentials?: boolean;
  }) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
      withCredentials: config.withCredentials ?? false,
    });

    this.setupInterceptors();
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private calculateBackoff(attempt: number): number {
    // Exponential backoff: delay * 2^attempt with jitter
    const exponentialDelay = this.retryConfig.retryDelay * Math.pow(2, attempt);
    const jitter = Math.random() * 0.3 * exponentialDelay; // Add up to 30% jitter
    return exponentialDelay + jitter;
  }

  private shouldRetry(error: AxiosError, attempt: number): boolean {
    if (attempt >= this.retryConfig.maxRetries) {
      return false;
    }

    // Retry on network errors
    if (!error.response) {
      return true;
    }

    // Retry on specific status codes
    const status = error.response.status;
    return this.retryConfig.retryableStatuses.includes(status);
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      config => {
        // Add timestamp to prevent caching
        if (config.params) {
          config.params._t = Date.now();
        } else {
          config.params = { _t: Date.now() };
        }
        return config;
      },
      error => Promise.reject(error)
    );

    // Response interceptor with retry logic
    this.client.interceptors.response.use(
      response => response.data,
      async error => {
        const config = error.config;
        
        // Initialize retry count
        if (!config._retryCount) {
          config._retryCount = 0;
        }

        // Check if we should retry
        if (this.shouldRetry(error, config._retryCount)) {
          config._retryCount += 1;
          
          // Calculate backoff delay
          const delay = this.calculateBackoff(config._retryCount - 1);
          
          // Wait before retrying
          await this.sleep(delay);
          
          // Retry the request
          return this.client(config);
        }

        // No more retries, format and reject error
        if (error.response) {
          // Server responded with error status
          const apiError = {
            success: false,
            error: {
              code: error.response.data?.error?.code || 'SERVER_ERROR',
              message:
                error.response.data?.error?.message ||
                'An error occurred on the server',
              details: error.response.data?.error?.details,
            },
            timestamp: new Date().toISOString(),
          };
          return Promise.reject(apiError);
        } else if (error.request) {
          // Request made but no response
          return Promise.reject({
            success: false,
            error: {
              code: 'NETWORK_ERROR',
              message: 'Network error. Please check your connection.',
            },
            timestamp: new Date().toISOString(),
          });
        } else {
          // Error in request setup
          return Promise.reject({
            success: false,
            error: {
              code: 'REQUEST_ERROR',
              message: error.message || 'Failed to make request',
            },
            timestamp: new Date().toISOString(),
          });
        }
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.client.get<T, T>(url, config);
  }

  async post<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.client.post<T, T>(url, data, config);
  }

  async put<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.client.put<T, T>(url, data, config);
  }

  async patch<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.client.patch<T, T>(url, data, config);
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.client.delete<T, T>(url, config);
  }

  setAuthToken(token: string): void {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  clearAuthToken(): void {
    delete this.client.defaults.headers.common['Authorization'];
  }
}

// Create and export singleton instance
export const httpClient = new HttpClient({
  baseURL: env.API_BASE_URL,
  timeout: env.API_TIMEOUT,
});

export default httpClient;
