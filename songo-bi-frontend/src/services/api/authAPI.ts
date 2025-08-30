// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Authentication API service for Songo BI
 */

import { apiService } from './index';
import { APIResponse, User, LoginCredentials } from '../../types';

export const authAPI = {
  async login(credentials: LoginCredentials): Promise<APIResponse<{ user: User; token: string }>> {
    return apiService.post('/auth/login', credentials);
  },

  async logout(): Promise<APIResponse<void>> {
    return apiService.post('/auth/logout');
  },

  async getCurrentUser(): Promise<APIResponse<User>> {
    return apiService.get('/auth/me');
  },

  async refreshToken(): Promise<APIResponse<{ token: string }>> {
    return apiService.post('/auth/refresh');
  },

  async updateProfile(data: Partial<User>): Promise<APIResponse<User>> {
    return apiService.put('/auth/profile', data);
  },

  async changePassword(data: {
    current_password: string;
    new_password: string;
  }): Promise<APIResponse<void>> {
    return apiService.post('/auth/change-password', data);
  },
};
