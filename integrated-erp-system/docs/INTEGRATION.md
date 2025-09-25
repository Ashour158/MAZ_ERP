# 🔗 Integration Guide

This document provides comprehensive guidance on integrating the React frontend with the ERPNext backend in the Integrated ERP System.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Integration](#api-integration)
3. [Real-time Communication](#real-time-communication)
4. [Authentication & Authorization](#authentication--authorization)
5. [Data Synchronization](#data-synchronization)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Testing](#testing)
9. [Deployment](#deployment)

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATED ERP SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer (React/TypeScript)                         │
│  ├── Modern UI Components                                  │
│  ├── Real-time Dashboards                                  │
│  ├── AI-Powered Analytics                                  │
│  └── Mobile-Responsive Interface                           │
├─────────────────────────────────────────────────────────────┤
│  API Gateway & Integration Layer                            │
│  ├── RESTful APIs                                          │
│  ├── WebSocket Connections                                 │
│  ├── Authentication & Authorization                        │
│  └── Data Synchronization                                  │
├─────────────────────────────────────────────────────────────┤
│  Backend Layer (Python/Frappe)                             │
│  ├── ERPNext Core                                          │
│  ├── Enhanced Modules                                      │
│  ├── AI/ML Engines                                         │
│  └── Business Logic                                        │
├─────────────────────────────────────────────────────────────┤
│  Database Layer                                             │
│  ├── ERPNext Database                                      │
│  ├── Analytics Database                                    │
│  └── Cache Layer (Redis)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Interaction** → React Frontend
2. **API Calls** → API Gateway
3. **Authentication** → JWT Validation
4. **Business Logic** → ERPNext Backend
5. **Data Storage** → PostgreSQL
6. **Real-time Updates** → WebSocket
7. **Response** → Frontend Update

## 🔌 API Integration

### RESTful API Endpoints

#### Authentication
```typescript
// Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

// Response
{
  "success": true,
  "token": "jwt-token-here",
  "user": {
    "name": "user@example.com",
    "email": "user@example.com",
    "full_name": "John Doe",
    "roles": ["System Manager"]
  }
}
```

#### Maintenance Module
```typescript
// Get tickets
GET /api/maintenance/tickets?status=open&priority=high

// Create ticket
POST /api/maintenance/tickets
{
  "subject": "Server Issue",
  "description": "Server is not responding",
  "priority": "High",
  "customer": "Customer-001"
}

// Update ticket
PUT /api/maintenance/tickets/TKT-2024-001
{
  "status": "In Progress",
  "assigned_to": "user@example.com"
}
```

#### Supply Chain Module
```typescript
// Get inventory
GET /api/supply-chain/inventory?warehouse=Stores

// Get reorder recommendations
GET /api/supply-chain/reorder-recommendations?status=pending

// Approve recommendation
POST /api/supply-chain/reorder-recommendations/REC-001/approve
```

### API Client Implementation

```typescript
// frontend/src/lib/api/integratedApi.ts
import axios from 'axios';

class IntegratedAPIClient {
  private baseURL: string;
  private authToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.setupInterceptors();
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private setupInterceptors() {
    // Request interceptor
    axios.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle token expiration
          this.handleTokenExpiration();
        }
        return Promise.reject(error);
      }
    );
  }

  private handleTokenExpiration() {
    // Redirect to login or refresh token
    window.location.href = '/login';
  }

  // Maintenance APIs
  async getTickets(filters?: any): Promise<Ticket[]> {
    const response = await axios.get(`${this.baseURL}/api/maintenance/tickets`, {
      params: filters
    });
    return response.data.data;
  }

  async createTicket(ticketData: CreateTicketRequest): Promise<Ticket> {
    const response = await axios.post(`${this.baseURL}/api/maintenance/tickets`, ticketData);
    return response.data.data;
  }

  // Supply Chain APIs
  async getInventory(filters?: any): Promise<InventoryBalance[]> {
    const response = await axios.get(`${this.baseURL}/api/supply-chain/inventory`, {
      params: filters
    });
    return response.data.data;
  }

  async getReorderRecommendations(filters?: any): Promise<ReorderRecommendation[]> {
    const response = await axios.get(`${this.baseURL}/api/supply-chain/reorder-recommendations`, {
      params: filters
    });
    return response.data.data;
  }
}
```

## 🔄 Real-time Communication

### WebSocket Integration

```typescript
// frontend/src/lib/hooks/useRealtimeUpdates.ts
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface RealtimeUpdate {
  type: string;
  data: any;
  timestamp: string;
}

export const useRealtimeUpdates = (module: string) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [latestEvent, setLatestEvent] = useState<RealtimeUpdate | null>(null);

  useEffect(() => {
    const newSocket = io(process.env.REACT_APP_WS_URL || 'ws://localhost:8000', {
      auth: {
        token: localStorage.getItem('authToken')
      }
    });

    newSocket.on('connect', () => {
      setConnectionStatus('connected');
      newSocket.emit('subscribe', { module });
    });

    newSocket.on('disconnect', () => {
      setConnectionStatus('disconnected');
    });

    newSocket.on(`${module}:update`, (data) => {
      setLatestEvent({
        type: `${module}:update`,
        data,
        timestamp: new Date().toISOString()
      });
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [module]);

  return {
    socket,
    connectionStatus,
    latestEvent
  };
};
```

### Backend WebSocket Handler

```python
# backend/api_gateway/websocket_handler.py
from flask_socketio import SocketIO, emit, join_room, leave_room
import frappe
from frappe import auth

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect(auth_data=None):
    """Handle client connection"""
    try:
        # Validate authentication
        if auth_data and 'token' in auth_data:
            # Validate JWT token
            user = validate_token(auth_data['token'])
            if user:
                join_room(f"user_{user.name}")
                emit('connected', {'status': 'success'})
            else:
                emit('error', {'message': 'Invalid token'})
                return False
    except Exception as e:
        emit('error', {'message': str(e)})
        return False

@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle module subscription"""
    module = data.get('module')
    if module:
        join_room(f"module_{module}")
        emit('subscribed', {'module': module})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    pass

def emit_module_update(module, data):
    """Emit update to module subscribers"""
    socketio.emit(f"{module}:update", data, room=f"module_{module}")
```

## 🔐 Authentication & Authorization

### JWT Token Management

```typescript
// frontend/src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  name: string;
  email: string;
  full_name: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      // Validate token and get user info
      validateToken(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const validateToken = async (token: string) => {
    try {
      const response = await fetch('/api/auth/validate', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData.user);
      } else {
        // Token is invalid
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Token validation failed:', error);
      localStorage.removeItem('authToken');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('authToken', data.token);
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Role-based Access Control

```python
# backend/api_gateway/authentication.py
from functools import wraps
import jwt
import frappe

def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if not current_user.has_permission(permission):
                return {'error': 'Insufficient permissions'}, 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if role not in [r.role for r in current_user.roles]:
                return {'error': 'Required role not found'}, 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator
```

## 📊 Data Synchronization

### Optimistic Updates

```typescript
// frontend/src/contexts/OptimisticUpdatesContext.tsx
import React, { createContext, useContext, useState, useCallback } from 'react';

interface OptimisticUpdate {
  id: string;
  entityId: string;
  optimisticData: any;
  apiCall: () => Promise<any>;
  timestamp: number;
}

interface OptimisticUpdatesContextType {
  optimisticUpdates: OptimisticUpdate[];
  addOptimisticUpdate: (update: Omit<OptimisticUpdate, 'id' | 'timestamp'>) => string;
  removeOptimisticUpdate: (id: string) => void;
  executeOptimisticUpdate: (id: string) => Promise<void>;
}

const OptimisticUpdatesContext = createContext<OptimisticUpdatesContextType | undefined>(undefined);

export const OptimisticUpdatesProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [optimisticUpdates, setOptimisticUpdates] = useState<OptimisticUpdate[]>([]);

  const addOptimisticUpdate = useCallback((update: Omit<OptimisticUpdate, 'id' | 'timestamp'>) => {
    const id = `update_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const optimisticUpdate: OptimisticUpdate = {
      ...update,
      id,
      timestamp: Date.now()
    };

    setOptimisticUpdates(prev => [...prev, optimisticUpdate]);
    return id;
  }, []);

  const removeOptimisticUpdate = useCallback((id: string) => {
    setOptimisticUpdates(prev => prev.filter(update => update.id !== id));
  }, []);

  const executeOptimisticUpdate = useCallback(async (id: string) => {
    const update = optimisticUpdates.find(u => u.id === id);
    if (!update) return;

    try {
      await update.apiCall();
      removeOptimisticUpdate(id);
    } catch (error) {
      console.error('Optimistic update failed:', error);
      // Handle rollback
    }
  }, [optimisticUpdates, removeOptimisticUpdate]);

  return (
    <OptimisticUpdatesContext.Provider value={{
      optimisticUpdates,
      addOptimisticUpdate,
      removeOptimisticUpdate,
      executeOptimisticUpdate
    }}>
      {children}
    </OptimisticUpdatesContext.Provider>
  );
};

export const useOptimisticUpdates = () => {
  const context = useContext(OptimisticUpdatesContext);
  if (context === undefined) {
    throw new Error('useOptimisticUpdates must be used within an OptimisticUpdatesProvider');
  }
  return context;
};
```

## ⚠️ Error Handling

### Global Error Handler

```typescript
// frontend/src/lib/errorHandler.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export const handleAPIError = (error: any): APIError => {
  if (error.response) {
    // Server responded with error status
    return new APIError(
      error.response.data?.error || 'Server error',
      error.response.status,
      error.response.data?.code
    );
  } else if (error.request) {
    // Network error
    return new APIError('Network error - please check your connection', 0);
  } else {
    // Other error
    return new APIError(error.message || 'Unknown error', 0);
  }
};

// Error boundary component
export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## 🚀 Performance Optimization

### Caching Strategy

```typescript
// frontend/src/lib/cache.ts
class CacheManager {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();

  set(key: string, data: any, ttl: number = 300000) { // 5 minutes default
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  clear() {
    this.cache.clear();
  }

  delete(key: string) {
    this.cache.delete(key);
  }
}

export const cacheManager = new CacheManager();
```

### Virtual Scrolling

```typescript
// frontend/src/components/VirtualTable.tsx
import { FixedSizeList as List } from 'react-window';

interface VirtualTableProps {
  items: any[];
  height: number;
  itemHeight: number;
  renderItem: (props: { index: number; style: React.CSSProperties; data: any }) => React.ReactNode;
}

export const VirtualTable: React.FC<VirtualTableProps> = ({
  items,
  height,
  itemHeight,
  renderItem
}) => {
  return (
    <List
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      itemData={items}
    >
      {renderItem}
    </List>
  );
};
```

## 🧪 Testing

### API Testing

```typescript
// frontend/src/tests/api.test.ts
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { MaintenanceModule } from '../components/MaintenanceModule';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

describe('Maintenance Module', () => {
  test('renders tickets list', async () => {
    const queryClient = createTestQueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <MaintenanceModule />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Maintenance Management')).toBeInTheDocument();
    });
  });
});
```

### Integration Testing

```python
# backend/tests/test_integration.py
import pytest
import json
from flask import Flask
from api_gateway.routes import api

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(api)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_endpoint(client):
    response = client.post('/api/auth/login', 
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user' in data

def test_maintenance_tickets_endpoint(client):
    # Mock authentication
    headers = {'Authorization': 'Bearer mock-token'}
    
    response = client.get('/api/maintenance/tickets', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
```

## 🚀 Deployment

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/erpnext
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile.prod
    environment:
      - REACT_APP_API_URL=https://api.erpnext.com
      - REACT_APP_WS_URL=wss://api.erpnext.com
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
```

### Health Monitoring

```typescript
// frontend/src/lib/healthMonitor.ts
class HealthMonitor {
  private checkInterval: number = 30000; // 30 seconds
  private intervalId: NodeJS.Timeout | null = null;

  start() {
    this.intervalId = setInterval(() => {
      this.checkHealth();
    }, this.checkInterval);
  }

  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  private async checkHealth() {
    try {
      const response = await fetch('/api/health');
      if (!response.ok) {
        this.handleHealthFailure();
      }
    } catch (error) {
      this.handleHealthFailure();
    }
  }

  private handleHealthFailure() {
    // Show notification to user
    console.warn('Health check failed - system may be experiencing issues');
  }
}

export const healthMonitor = new HealthMonitor();
```

This integration guide provides comprehensive documentation for integrating the React frontend with the ERPNext backend, covering all aspects from API integration to deployment strategies.
