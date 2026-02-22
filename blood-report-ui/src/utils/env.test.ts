import { describe, it, expect } from 'vitest';
import { env, validateEnvironment } from './env';

describe('Environment Configuration', () => {
  it('should have default values for all environment variables', () => {
    expect(env.API_BASE_URL).toBeDefined();
    expect(env.API_TIMEOUT).toBeGreaterThan(0);
    expect(env.MAX_FILE_SIZE).toBeGreaterThan(0);
    expect(Array.isArray(env.ALLOWED_FILE_TYPES)).toBe(true);
  });

  it('should validate environment successfully with defaults', () => {
    expect(() => validateEnvironment()).not.toThrow();
  });

  it('should have correct boolean values for feature flags', () => {
    expect(typeof env.ENABLE_ANALYTICS).toBe('boolean');
    expect(typeof env.ENABLE_EXPORT).toBe('boolean');
    expect(typeof env.ENABLE_PROVIDER_FEATURES).toBe('boolean');
    expect(typeof env.ENABLE_ADMIN_FEATURES).toBe('boolean');
  });
});