// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Main API service for Songo BI Frontend
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { APIResponse } from '../../types';

class APIService {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('songo_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('songo_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    const response = await this.client.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    const response = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    const response = await this.client.put(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    const response = await this.client.delete(url, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    const response = await this.client.patch(url, data, config);
    return response.data;
  }
}

// Create singleton instance
export const apiService = new APIService();

// Specific API services
export * from './authAPI';
export * from './chatAPI';
export * from './dashboardAPI';
export * from './netsuiteAPI';
