/**
 * API Client Service
 * 
 * This service provides a wrapper around fetch for making API requests
 * to the backend. It handles common tasks like setting headers, handling
 * errors, and parsing responses.
 */

import { API_CONFIG } from '../config';

/**
 * HTTP request methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

/**
 * Options for API requests
 */
export interface ApiRequestOptions {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: any;
  params?: Record<string, string>;
  withCredentials?: boolean;
}

/**
 * API response with typed data
 */
export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
  headers: Headers;
}

/**
 * Error thrown by the API client
 */
export class ApiError extends Error {
  status: number;
  statusText: string;
  data: any;

  constructor(message: string, status: number, statusText: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
    this.data = data;
  }
}

/**
 * API Client for making requests to the backend
 */
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_CONFIG.API_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make a request to the API
   * 
   * @param endpoint - The API endpoint to request
   * @param options - Request options
   * @returns Promise with the response data
   * 
   * @example
   * // GET request
   * const data = await apiClient.request<UserData>('/users/123');
   * 
   * @example
   * // POST request with body
   * const data = await apiClient.request<CreateUserResponse>('/users', {
   *   method: 'POST',
   *   body: { name: 'John', email: 'john@example.com' }
   * });
   */
  async request<T = any>(endpoint: string, options: ApiRequestOptions = {}): Promise<ApiResponse<T>> {
    const {
      method = 'GET',
      headers = {},
      body,
      params,
      withCredentials = false,
    } = options;

    // Build URL with query parameters
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        queryParams.append(key, value);
      });
      url = `${url}?${queryParams.toString()}`;
    }

    // Prepare headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    };

    // Prepare request options
    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      credentials: withCredentials ? 'include' : 'same-origin',
    };

    // Add body for non-GET requests
    if (body && method !== 'GET') {
      requestOptions.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(url, requestOptions);
      
      // Parse response data
      let data: T;
      const contentType = response.headers.get('Content-Type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text() as unknown as T;
      }

      // Handle error responses
      if (!response.ok) {
        throw new ApiError(
          `API request failed: ${response.status} ${response.statusText}`,
          response.status,
          response.statusText,
          data
        );
      }

      return {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      };
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      throw new ApiError(
        `API request failed: ${error instanceof Error ? error.message : String(error)}`,
        0,
        'Unknown Error',
        null
      );
    }
  }

  /**
   * Make a GET request
   * 
   * @param endpoint - The API endpoint
   * @param options - Request options
   * @returns Promise with the response data
   * 
   * @example
   * const { data } = await apiClient.get<UserData>('/users/123');
   * console.log(data.name);
   */
  async get<T = any>(endpoint: string, options: Omit<ApiRequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  /**
   * Make a POST request
   * 
   * @param endpoint - The API endpoint
   * @param body - Request body
   * @param options - Additional request options
   * @returns Promise with the response data
   * 
   * @example
   * const { data } = await apiClient.post<CreateUserResponse>('/users', {
   *   name: 'John',
   *   email: 'john@example.com'
   * });
   */
  async post<T = any>(endpoint: string, body?: any, options: Omit<ApiRequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body });
  }

  /**
   * Make a PUT request
   * 
   * @param endpoint - The API endpoint
   * @param body - Request body
   * @param options - Additional request options
   * @returns Promise with the response data
   * 
   * @example
   * const { data } = await apiClient.put<UpdateUserResponse>('/users/123', {
   *   name: 'John Updated'
   * });
   */
  async put<T = any>(endpoint: string, body?: any, options: Omit<ApiRequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body });
  }

  /**
   * Make a DELETE request
   * 
   * @param endpoint - The API endpoint
   * @param options - Request options
   * @returns Promise with the response data
   * 
   * @example
   * const { status } = await apiClient.delete('/users/123');
   * if (status === 204) {
   *   console.log('User deleted successfully');
   * }
   */
  async delete<T = any>(endpoint: string, options: Omit<ApiRequestOptions, 'method'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  /**
   * Make a PATCH request
   * 
   * @param endpoint - The API endpoint
   * @param body - Request body
   * @param options - Additional request options
   * @returns Promise with the response data
   * 
   * @example
   * const { data } = await apiClient.patch<PatchUserResponse>('/users/123', {
   *   status: 'active'
   * });
   */
  async patch<T = any>(endpoint: string, body?: any, options: Omit<ApiRequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body });
  }
}

/**
 * Default API client instance
 */
export const apiClient = new ApiClient();

/**
 * Create a new API client with a custom base URL
 * 
 * @param baseUrl - Custom base URL for the API
 * @returns A new ApiClient instance
 * 
 * @example
 * const customApiClient = createApiClient('https://api.example.com/v2');
 */
export const createApiClient = (baseUrl: string): ApiClient => {
  return new ApiClient(baseUrl);
};