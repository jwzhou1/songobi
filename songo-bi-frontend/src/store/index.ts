// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Redux store configuration for Songo BI
 */

import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';

import authSlice from './slices/authSlice';
import chatSlice from './slices/chatSlice';
import dashboardSlice from './slices/dashboardSlice';
import netsuiteSlice from './slices/netsuiteSlice';
import uiSlice from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    chat: chatSlice,
    dashboard: dashboardSlice,
    netsuite: netsuiteSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
