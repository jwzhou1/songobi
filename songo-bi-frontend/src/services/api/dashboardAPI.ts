// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Dashboard API service for Songo BI
 */

import { apiService } from './index';
import { APIResponse, Dashboard, Chart } from '../../types';

export const dashboardAPI = {
  // Dashboard management
  async getDashboards(userId?: number): Promise<APIResponse<Dashboard[]>> {
    const params = userId ? { user_id: userId } : {};
    return apiService.get('/dashboards', { params });
  },

  async getDashboard(dashboardId: number, filters?: any): Promise<APIResponse<Dashboard>> {
    const params = filters ? { filters: JSON.stringify(filters) } : {};
    return apiService.get(`/dashboards/${dashboardId}`, { params });
  },

  async createDashboard(data: {
    user_id: number;
    title: string;
    description?: string;
  }): Promise<APIResponse<Dashboard>> {
    return apiService.post('/dashboards', data);
  },

  async updateDashboard(dashboardId: number, data: Partial<Dashboard>): Promise<APIResponse<Dashboard>> {
    return apiService.put(`/dashboards/${dashboardId}`, data);
  },

  async deleteDashboard(dashboardId: number): Promise<APIResponse<void>> {
    return apiService.delete(`/dashboards/${dashboardId}`);
  },

  // Chart management
  async createChart(data: {
    dashboard_id: number;
    chart_config: any;
  }): Promise<APIResponse<Chart>> {
    return apiService.post('/charts', data);
  },

  async updateChart(chartId: number, data: Partial<Chart>): Promise<APIResponse<Chart>> {
    return apiService.put(`/charts/${chartId}`, data);
  },

  async deleteChart(chartId: number): Promise<APIResponse<void>> {
    return apiService.delete(`/charts/${chartId}`);
  },

  // Data operations
  async executeSQL(data: {
    database_id: number;
    sql: string;
    limit?: number;
  }): Promise<APIResponse<any>> {
    return apiService.post('/sql/execute', data);
  },
};
