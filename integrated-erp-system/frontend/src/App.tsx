import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { RealtimeProvider } from './contexts/RealtimeContext'
import { OptimisticUpdatesProvider } from './contexts/OptimisticUpdatesContext'

// Layout Components
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { LoadingSpinner } from './components/ui/LoadingSpinner'

// Module Components
import { MaintenanceModule } from './components/MaintenanceModule'
import { SupplyChainModule } from './components/SupplyChainModule'
import { EnhancedCRMModule } from './components/EnhancedCRMModule'
import { AIAnalyticsModule } from './components/AIAnalyticsModule'

// Pages
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { NotFoundPage } from './pages/NotFoundPage'

// Styles
import './index.css'

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

// Main App Layout
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100">
          <div className="container mx-auto px-6 py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Main App Component
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RealtimeProvider>
          <OptimisticUpdatesProvider>
            <Router>
              <div className="App">
                <Routes>
                  {/* Public Routes */}
                  <Route path="/login" element={<LoginPage />} />
                  
                  {/* Protected Routes */}
                  <Route path="/" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <DashboardPage />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  
                  <Route path="/maintenance/*" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <MaintenanceModule />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  
                  <Route path="/supply-chain/*" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <SupplyChainModule />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  
                  <Route path="/crm/*" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <EnhancedCRMModule />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  
                  <Route path="/analytics/*" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <AIAnalyticsModule />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  
                  {/* 404 Route */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
                
                {/* Global Toast Notifications */}
                <Toaster
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: '#363636',
                      color: '#fff',
                    },
                    success: {
                      duration: 3000,
                      iconTheme: {
                        primary: '#4ade80',
                        secondary: '#fff',
                      },
                    },
                    error: {
                      duration: 5000,
                      iconTheme: {
                        primary: '#ef4444',
                        secondary: '#fff',
                      },
                    },
                  }}
                />
              </div>
            </Router>
          </OptimisticUpdatesProvider>
        </RealtimeProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
