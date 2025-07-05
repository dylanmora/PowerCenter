/**
 * API configuration for PowerCenter application
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  MEET_ANALYZE: `${API_BASE_URL}/meet/analyze`,
  LIFTER_SEARCH: `${API_BASE_URL}/lifter/search`,
} as const;

export const API_CONFIG = {
  TIMEOUT: 60000, // 60 seconds for search operations
  RETRY_ATTEMPTS: 3,
} as const; 