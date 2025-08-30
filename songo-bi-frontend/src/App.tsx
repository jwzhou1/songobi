// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Main App component for Songo BI
 */

import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Spin } from 'antd';
import { useSelector } from 'react-redux';

import { AppLayout } from './components/Layout/AppLayout';
import { LoginPage } from './pages/Login/LoginPage';
import { DashboardList } from './pages/Dashboard/DashboardList';
import { DashboardView } from './pages/Dashboard/DashboardView';
import { SQLLab } from './pages/SQLLab/SQLLab';
import { NetSuiteManager } from './pages/NetSuite/NetSuiteManager';
import { ChatInterface } from './components/Chat/ChatInterface';
import { ErrorBoundary } from './components/Common/ErrorBoundary';
import { useAuth } from './hooks/useAuth';
import { RootState } from './store';

import './App.css';

const { Content } = Layout;

// Lazy load components for better performance
const Explore = React.lazy(() => import('./pages/Explore/Explore'));
const Settings = React.lazy(() => import('./pages/Settings/Settings'));

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const { chatVisible } = useSelector((state: RootState) => state.chat);

  if (isLoading) {
    return (
      <div className="app-loading">
        <Spin size="large" />
        <p>Loading Songo BI...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <ErrorBoundary>
      <AppLayout>
        <Content className="app-content">
          <Suspense fallback={<Spin size="large" />}>
            <Routes>
              {/* Dashboard routes */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardList />} />
              <Route path="/dashboard/:id" element={<DashboardView />} />

              {/* SQL Lab */}
              <Route path="/sql" element={<SQLLab />} />

              {/* Data Exploration */}
              <Route path="/explore" element={<Explore />} />
              <Route path="/explore/:datasourceId" element={<Explore />} />

              {/* NetSuite Management */}
              <Route path="/netsuite" element={<NetSuiteManager />} />

              {/* Settings */}
              <Route path="/settings" element={<Settings />} />

              {/* Catch all route */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Suspense>
        </Content>

        {/* AI Chatbot Interface */}
        {chatVisible && <ChatInterface />}
      </AppLayout>
    </ErrorBoundary>
  );
};

export default App;
