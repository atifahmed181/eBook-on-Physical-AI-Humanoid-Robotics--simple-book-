// docs/src/utils/config.js
// Default configuration - can be overridden by setting window.API_CONFIG in HTML
export const API_CONFIG = {
  BACKEND_URL: (typeof window !== 'undefined' && window.API_CONFIG && window.API_CONFIG.BACKEND_URL)
    ? window.API_CONFIG.BACKEND_URL
    : 'http://localhost:8000'  // Default to localhost:8000
};