/**
 * Application Configuration
 * 
 * This file centralizes all configuration values used throughout the application.
 * Environment variables are accessed through import.meta.env with fallback values
 * for development.
 */

/**
 * API Configuration
 */
export const API_CONFIG = {
  /**
   * Base URL for the API
   * 
   * In development: Defaults to http://localhost:8000
   * In production: Must be set via VITE_API_BASE_URL environment variable
   * 
   * @example
   * // .env file
   * VITE_API_BASE_URL=https://api.example.com
   */
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',

  /**
   * API version path
   * 
   * This is appended to the BASE_URL to form the complete API endpoint
   */
  API_PATH: '/api/v1',

  /**
   * Returns the complete API URL including the base URL and API path
   */
  get API_URL() {
    return `${this.BASE_URL}${this.API_PATH}`;
  }
};

/**
 * Environment Configuration
 */
export const ENV_CONFIG = {
  /**
   * Current environment (development, production, test)
   */
  NODE_ENV: import.meta.env.MODE || 'development',
  
  /**
   * Whether the application is running in development mode
   */
  IS_DEV: (import.meta.env.MODE || 'development') === 'development',
  
  /**
   * Whether the application is running in production mode
   */
  IS_PROD: import.meta.env.MODE === 'production',
};