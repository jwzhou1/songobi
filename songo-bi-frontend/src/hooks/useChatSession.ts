// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Chat session hook for Songo BI
 */

import { useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { 
  createChatSession, 
  sendChatMessage, 
  loadChatMessages,
  chatActions 
} from '../store/slices/chatSlice';

export const useChatSession = (sessionId: string | null) => {
  const dispatch = useDispatch();
  const { messages, isLoading, isSessionLoading, error } = useSelector(
    (state: RootState) => state.chat
  );

  // Load messages when session changes
  useEffect(() => {
    if (sessionId) {
      dispatch(loadChatMessages(parseInt(sessionId)));
    }
  }, [sessionId, dispatch]);

  const createSession = useCallback((userId: number, context?: any) => {
    return dispatch(createChatSession({ userId, context }));
  }, [dispatch]);

  const sendMessage = useCallback((message: string) => {
    if (!sessionId) return Promise.reject('No active session');
    
    return dispatch(sendChatMessage({ 
      sessionId: parseInt(sessionId), 
      message 
    })).then(() => {
      // Reload messages after sending
      dispatch(loadChatMessages(parseInt(sessionId)));
    });
  }, [sessionId, dispatch]);

  const clearError = useCallback(() => {
    dispatch(chatActions.clearError());
  }, [dispatch]);

  return {
    messages,
    isLoading,
    isSessionLoading,
    error,
    createSession,
    sendMessage,
    clearError,
  };
};
