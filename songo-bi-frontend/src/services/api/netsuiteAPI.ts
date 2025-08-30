// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * NetSuite API service for Songo BI
 */

import { apiService } from './index';
import { APIResponse, NetSuiteConnection, NetSuiteDataSource, NetSuiteQuery } from '../../types';

export const netsuiteAPI = {
  // Connection management
  async getConnections(): Promise<APIResponse<NetSuiteConnection[]>> {
    return apiService.get('/netsuite/connections');
  },

  async createConnection(data: {
    name: string;
    account_id: string;
    consumer_key: string;
    consumer_secret: string;
    token_id: string;
    token_secret: string;
    description?: string;
  }): Promise<APIResponse<NetSuiteConnection>> {
    return apiService.post('/netsuite/connections', data);
  },

  async testConnection(connectionId: number): Promise<APIResponse<any>> {
    return apiService.post(`/netsuite/connections/${connectionId}/test`);
  },

  async getSchema(connectionId: number): Promise<APIResponse<any>> {
    return apiService.get(`/netsuite/connections/${connectionId}/schema`);
  },

  // Data source management
  async getDataSources(connectionId?: number): Promise<APIResponse<NetSuiteDataSource[]>> {
    const params = connectionId ? { connection_id: connectionId } : {};
    return apiService.get('/netsuite/data-sources', { params });
  },

  async createDataSource(data: {
    name: string;
    connection_id: number;
    record_type: string;
    fields: string[];
    filters?: any;
  }): Promise<APIResponse<NetSuiteDataSource>> {
    return apiService.post('/netsuite/data-sources', data);
  },

  async refreshDataSource(dataSourceId: number): Promise<APIResponse<any>> {
    return apiService.post(`/netsuite/data-sources/${dataSourceId}/refresh`);
  },

  // Query management
  async getQueries(connectionId?: number, dataSourceId?: number): Promise<APIResponse<NetSuiteQuery[]>> {
    const params: any = {};
    if (connectionId) params.connection_id = connectionId;
    if (dataSourceId) params.data_source_id = dataSourceId;
    
    return apiService.get('/netsuite/queries', { params });
  },

  async createQuery(data: {
    name: string;
    connection_id: number;
    data_source_id?: number;
    query_type: string;
    query_config: any;
  }): Promise<APIResponse<NetSuiteQuery>> {
    return apiService.post('/netsuite/queries', data);
  },

  async executeQuery(queryId: number): Promise<APIResponse<any>> {
    return apiService.post(`/netsuite/queries/${queryId}/execute`);
  },

  // Monitoring
  async getRefreshLogs(connectionId?: number): Promise<APIResponse<any[]>> {
    const params = connectionId ? { connection_id: connectionId } : {};
    return apiService.get('/netsuite/refresh-logs', { params });
  },
};
