// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Main entry point for Songo BI Frontend
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { QueryClient, QueryClientProvider } from 'react-query';

import App from './App';
import { store } from './store';
import { songoTheme } from './theme';
import './styles/index.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Get root element
const container = document.getElementById('root');
if (!container) {
  throw new Error('Root element not found');
}

const root = createRoot(container);

// Render application
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider theme={songoTheme}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ConfigProvider>
      </QueryClientProvider>
    </Provider>
  </React.StrictMode>
);
