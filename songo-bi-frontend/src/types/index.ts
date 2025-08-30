// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * TypeScript type definitions for Songo BI
 */

// Auth types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  active: boolean;
  roles: string[];
  preferences: Record<string, any>;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// Dashboard types
export interface Dashboard {
  id: number;
  dashboard_title: string;
  description?: string;
  published: boolean;
  owner_id: number;
  created_on: string;
  changed_on: string;
  position_json: Record<string, any>;
  metadata: Record<string, any>;
  charts: Chart[];
  ai_generated?: boolean;
  ai_confidence?: number;
}

export interface Chart {
  id: number;
  slice_name: string;
  viz_type: string;
  description?: string;
  datasource_id: number;
  form_data: Record<string, any>;
  query_context: Record<string, any>;
  data?: any[];
  cache_timeout?: number;
}

// NetSuite types
export interface NetSuiteConnection {
  id: number;
  name: string;
  account_id: string;
  is_active: boolean;
  auto_refresh: boolean;
  refresh_interval: number;
  description?: string;
}

export interface NetSuiteDataSource {
  id: number;
  name: string;
  connection_id: number;
  record_type: string;
  fields: string[];
  filters: Record<string, any>;
  auto_refresh: boolean;
  last_refresh?: string;
  refresh_status: string;
  refresh_error?: string;
}

export interface NetSuiteQuery {
  id: number;
  name: string;
  connection_id: number;
  data_source_id?: number;
  query_type: string;
  query_config: Record<string, any>;
  is_active: boolean;
  auto_execute: boolean;
  last_execution?: string;
  execution_status: string;
  result_count: number;
  execution_time?: number;
}

// Chat types
export interface ChatSession {
  id: number;
  session_id: string;
  title: string;
  description?: string;
  is_active: boolean;
  started_at: string;
  last_activity: string;
  context_data: Record<string, any>;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  content_type: 'text' | 'chart' | 'data' | 'error';
  timestamp: string;
  chart_config?: Record<string, any>;
  query_sql?: string;
  data_preview?: any[];
  processing_time?: number;
}

export interface AIInsight {
  id: number;
  insight_type: string;
  title: string;
  description: string;
  confidence_score: number;
  is_featured: boolean;
  generated_at: string;
  insight_data: Record<string, any>;
}

// Data types
export interface Database {
  id: number;
  database_name: string;
  sqlalchemy_uri: string;
  expose_in_sqllab: boolean;
  allow_csv_upload: boolean;
  cache_timeout?: number;
}

export interface Table {
  id: number;
  table_name: string;
  database_id: number;
  schema?: string;
  description?: string;
  columns: TableColumn[];
  sample_data?: any[];
  row_count?: number;
}

export interface TableColumn {
  name: string;
  type: string;
  is_dttm: boolean;
  groupby: boolean;
  filterable: boolean;
  description?: string;
}

// API Response types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  count?: number;
}

// Chart configuration types
export interface ChartConfig {
  type: string;
  title?: string;
  subtitle?: string;
  data: any[];
  options: Record<string, any>;
  theme?: string;
}

// Filter types
export interface DashboardFilter {
  id: number;
  filter_name: string;
  filter_type: string;
  config: Record<string, any>;
  default_value?: any;
  is_required: boolean;
}

// UI state types
export interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  loading: boolean;
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}
