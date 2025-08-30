// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Chat state management slice
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { ChatSession, ChatMessage } from '../../types/chat';
import { chatAPI } from '../../services/api/chatAPI';

interface ChatState {
  chatVisible: boolean;
  currentSessionId: string | null;
  sessions: ChatSession[];
  messages: ChatMessage[];
  isLoading: boolean;
  isSessionLoading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  chatVisible: false,
  currentSessionId: null,
  sessions: [],
  messages: [],
  isLoading: false,
  isSessionLoading: false,
  error: null,
};

// Async thunks
export const createChatSession = createAsyncThunk(
  'chat/createSession',
  async (payload: { userId: number; context?: any }) => {
    const response = await chatAPI.createSession(payload.userId, payload.context);
    return response.data;
  }
);

export const sendChatMessage = createAsyncThunk(
  'chat/sendMessage',
  async (payload: { sessionId: number; message: string }) => {
    const response = await chatAPI.sendMessage(payload.sessionId, payload.message);
    return response.data;
  }
);

export const loadChatMessages = createAsyncThunk(
  'chat/loadMessages',
  async (sessionId: number) => {
    const response = await chatAPI.getMessages(sessionId);
    return response.data;
  }
);

export const loadUserSessions = createAsyncThunk(
  'chat/loadUserSessions',
  async (userId: number) => {
    const response = await chatAPI.getUserSessions(userId);
    return response.data;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    toggleChat: (state) => {
      state.chatVisible = !state.chatVisible;
    },
    openChat: (state) => {
      state.chatVisible = true;
    },
    closeChat: (state) => {
      state.chatVisible = false;
    },
    setCurrentSession: (state, action: PayloadAction<string>) => {
      state.currentSessionId = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      // Create session
      .addCase(createChatSession.pending, (state) => {
        state.isSessionLoading = true;
        state.error = null;
      })
      .addCase(createChatSession.fulfilled, (state, action) => {
        state.isSessionLoading = false;
        state.currentSessionId = action.payload.session_id;
        state.sessions.unshift(action.payload);
      })
      .addCase(createChatSession.rejected, (state, action) => {
        state.isSessionLoading = false;
        state.error = action.error.message || 'Failed to create chat session';
      })
      
      // Send message
      .addCase(sendChatMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        // Messages are loaded separately to get the complete conversation
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to send message';
      })
      
      // Load messages
      .addCase(loadChatMessages.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(loadChatMessages.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages = action.payload;
      })
      .addCase(loadChatMessages.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to load messages';
      })
      
      // Load user sessions
      .addCase(loadUserSessions.fulfilled, (state, action) => {
        state.sessions = action.payload;
      });
  },
});

export const chatActions = chatSlice.actions;
export default chatSlice.reducer;
