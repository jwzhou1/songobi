// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Chat API service for Songo BI
 */

import { apiService } from './index';
import { APIResponse, ChatSession, ChatMessage, AIInsight } from '../../types';

export const chatAPI = {
  // Session management
  async createSession(userId: number, context?: any): Promise<APIResponse<ChatSession>> {
    return apiService.post('/chatbot/sessions', {
      user_id: userId,
      context: context || {}
    });
  },

  async getSession(sessionId: number): Promise<APIResponse<ChatSession>> {
    return apiService.get(`/chatbot/sessions/${sessionId}`);
  },

  async getUserSessions(userId: number): Promise<APIResponse<ChatSession[]>> {
    return apiService.get('/chatbot/sessions', {
      params: { user_id: userId }
    });
  },

  // Message management
  async sendMessage(sessionId: number, message: string): Promise<APIResponse<any>> {
    return apiService.post(`/chatbot/sessions/${sessionId}/messages`, {
      message
    });
  },

  async getMessages(sessionId: number): Promise<APIResponse<ChatMessage[]>> {
    return apiService.get(`/chatbot/sessions/${sessionId}/messages`);
  },

  // AI insights
  async getInsights(sessionId?: number, type?: string): Promise<APIResponse<AIInsight[]>> {
    const params: any = {};
    if (sessionId) params.session_id = sessionId;
    if (type) params.type = type;
    
    return apiService.get('/chatbot/insights', { params });
  },

  // AI dashboard generation
  async generateDashboard(userId: number, prompt: string, dataSources: number[]): Promise<APIResponse<any>> {
    return apiService.post('/chatbot/generate-dashboard', {
      user_id: userId,
      prompt,
      data_sources: dataSources
    });
  },
};
