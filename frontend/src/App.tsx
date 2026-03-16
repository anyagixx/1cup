import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import { AuthProvider } from '@/auth';
import { PrivateRoute } from '@/auth';
import { Login } from '@/auth';
import { MainLayout } from '@/layout';
import { Dashboard, Servers, Databases, Sessions, Logs, Settings } from '@/pages';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={ruRU}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <MainLayout>
                    <Dashboard />
                  </MainLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/servers"
              element={
                <PrivateRoute>
                  <MainLayout>
                    <Servers />
                  </MainLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/databases"
              element={
                <PrivateRoute>
                  <MainLayout>
                    <Databases />
                  </MainLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/sessions"
              element={
                <PrivateRoute>
                  <MainLayout>
                    <Sessions />
                  </MainLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/logs"
              element={
                <PrivateRoute>
                  <MainLayout>
                    <Logs />
                  </MainLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <PrivateRoute requiredRole="admin">
                  <MainLayout>
                    <Settings />
                  </MainLayout>
                </PrivateRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
