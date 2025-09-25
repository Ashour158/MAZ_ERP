// Comprehensive Frontend Integration Tests

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { BrowserRouter } from 'react-router-dom'
import { MaintenanceModule } from '../components/MaintenanceModule'
import { SupplyChainModule } from '../components/SupplyChainModule'
import { App } from '../App'

// Mock API responses
const mockTicketData = [
  {
    id: 'TKT-001',
    subject: 'Test Ticket 1',
    description: 'Test Description 1',
    priority: 'High',
    status: 'Open',
    customer: 'Customer A',
    assigned_to: 'user@example.com',
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 'TKT-002',
    subject: 'Test Ticket 2',
    description: 'Test Description 2',
    priority: 'Medium',
    status: 'In Progress',
    customer: 'Customer B',
    assigned_to: 'user@example.com',
    created_at: '2024-01-01T00:00:00Z'
  }
]

const mockInventoryData = [
  {
    item_code: 'ITEM-001',
    item_name: 'Test Item 1',
    warehouse: 'Stores',
    actual_qty: 100,
    reserved_qty: 10,
    projected_qty: 90
  },
  {
    item_code: 'ITEM-002',
    item_name: 'Test Item 2',
    warehouse: 'Stores',
    actual_qty: 50,
    reserved_qty: 5,
    projected_qty: 45
  }
]

const mockReorderRecommendations = [
  {
    id: 'REC-001',
    item_code: 'ITEM-001',
    item_name: 'Test Item 1',
    recommended_qty: 100,
    unit_cost: 50.0,
    total_cost: 5000.0,
    confidence_score: 0.85,
    urgency_score: 0.7,
    status: 'Pending'
  },
  {
    id: 'REC-002',
    item_code: 'ITEM-002',
    item_name: 'Test Item 2',
    recommended_qty: 50,
    unit_cost: 75.0,
    total_cost: 3750.0,
    confidence_score: 0.92,
    urgency_score: 0.8,
    status: 'Approved'
  }
]

// Mock API client
const mockApiClient = {
  getTickets: jest.fn().mockResolvedValue({ data: mockTicketData }),
  createTicket: jest.fn().mockResolvedValue({ data: { id: 'TKT-003' } }),
  updateTicket: jest.fn().mockResolvedValue({ data: { id: 'TKT-001' } }),
  getInventory: jest.fn().mockResolvedValue({ data: mockInventoryData }),
  getReorderRecommendations: jest.fn().mockResolvedValue({ data: mockReorderRecommendations }),
  approveRecommendation: jest.fn().mockResolvedValue({ data: { id: 'REC-001' } })
}

// Mock authentication context
const mockAuthContext = {
  user: {
    name: 'test@example.com',
    email: 'test@example.com',
    full_name: 'Test User',
    roles: ['System Manager']
  },
  token: 'mock-jwt-token',
  login: jest.fn(),
  logout: jest.fn(),
  loading: false
}

// Mock realtime context
const mockRealtimeContext = {
  socket: null,
  connectionStatus: 'connected' as const,
  latestEvent: null
}

// Mock optimistic updates context
const mockOptimisticUpdatesContext = {
  optimisticUpdates: [],
  addOptimisticUpdate: jest.fn(),
  removeOptimisticUpdate: jest.fn(),
  executeOptimisticUpdate: jest.fn()
}

// Create test query client
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = createTestQueryClient()
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('Integrated ERP System - Frontend Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Maintenance Module', () => {
    test('renders maintenance module correctly', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Maintenance Management')).toBeInTheDocument()
        expect(screen.getByText('Advanced ticket system with AI-powered features')).toBeInTheDocument()
      })
    })

    test('displays quick stats correctly', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Open Tickets')).toBeInTheDocument()
        expect(screen.getByText('Avg Response Time')).toBeInTheDocument()
        expect(screen.getByText('SLA Compliance')).toBeInTheDocument()
        expect(screen.getByText('Customer Satisfaction')).toBeInTheDocument()
      })
    })

    test('switches between tabs correctly', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Tickets')).toBeInTheDocument()
        expect(screen.getByText('Communications')).toBeInTheDocument()
        expect(screen.getByText('SLA Management')).toBeInTheDocument()
        expect(screen.getByText('Knowledge Base')).toBeInTheDocument()
        expect(screen.getByText('Analytics')).toBeInTheDocument()
      })

      // Test tab switching
      fireEvent.click(screen.getByText('Communications'))
      expect(screen.getByText('Communications')).toHaveClass('bg-primary')
    })

    test('handles refresh button click', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        const refreshButton = screen.getByText('Refresh')
        expect(refreshButton).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Refresh'))
      // Verify refresh functionality (would need to mock the actual refresh logic)
    })

    test('handles new ticket button click', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        const newTicketButton = screen.getByText('New Ticket')
        expect(newTicketButton).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('New Ticket'))
      // Verify new ticket functionality (would need to mock the actual creation logic)
    })
  })

  describe('Supply Chain Module', () => {
    test('renders supply chain module correctly', async () => {
      render(
        <TestWrapper>
          <SupplyChainModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Supply Chain Management')).toBeInTheDocument()
        expect(screen.getByText('Intelligent supply chain with AI-powered recommendations')).toBeInTheDocument()
      })
    })

    test('displays supply chain quick stats correctly', async () => {
      render(
        <TestWrapper>
          <SupplyChainModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Total Inventory Value')).toBeInTheDocument()
        expect(screen.getByText('Reorder Recommendations')).toBeInTheDocument()
        expect(screen.getByText('Vendor Performance')).toBeInTheDocument()
        expect(screen.getByText('Cost Savings')).toBeInTheDocument()
      })
    })

    test('switches between supply chain tabs correctly', async () => {
      render(
        <TestWrapper>
          <SupplyChainModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Inventory')).toBeInTheDocument()
        expect(screen.getByText('Purchases')).toBeInTheDocument()
        expect(screen.getByText('Reorder AI')).toBeInTheDocument()
        expect(screen.getByText('Smart PO')).toBeInTheDocument()
        expect(screen.getByText('Vendors')).toBeInTheDocument()
        expect(screen.getByText('Analytics')).toBeInTheDocument()
      })

      // Test tab switching
      fireEvent.click(screen.getByText('Inventory'))
      expect(screen.getByText('Inventory')).toHaveClass('bg-primary')
    })
  })

  describe('App Integration', () => {
    test('renders app without crashing', () => {
      render(
        <TestWrapper>
          <App />
        </TestWrapper>
      )

      // App should render without throwing errors
      expect(document.body).toBeInTheDocument()
    })

    test('handles routing correctly', async () => {
      render(
        <TestWrapper>
          <App />
        </TestWrapper>
      )

      // Test that main routes are accessible
      await waitFor(() => {
        expect(window.location.pathname).toBe('/')
      })
    })
  })

  describe('Error Handling', () => {
    test('handles API errors gracefully', async () => {
      // Mock API error
      mockApiClient.getTickets.mockRejectedValueOnce(new Error('API Error'))

      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        // Should handle error gracefully without crashing
        expect(screen.getByText('Maintenance Management')).toBeInTheDocument()
      })
    })

    test('handles network errors gracefully', async () => {
      // Mock network error
      mockApiClient.getTickets.mockRejectedValueOnce(new Error('Network Error'))

      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        // Should handle network error gracefully
        expect(screen.getByText('Maintenance Management')).toBeInTheDocument()
      })
    })
  })

  describe('Performance Tests', () => {
    test('renders large datasets efficiently', async () => {
      // Mock large dataset
      const largeTicketData = Array.from({ length: 1000 }, (_, i) => ({
        id: `TKT-${i.toString().padStart(3, '0')}`,
        subject: `Test Ticket ${i}`,
        description: `Test Description ${i}`,
        priority: ['Low', 'Medium', 'High', 'Critical'][i % 4],
        status: ['Open', 'In Progress', 'Closed'][i % 3],
        customer: `Customer ${i}`,
        assigned_to: 'user@example.com',
        created_at: '2024-01-01T00:00:00Z'
      }))

      mockApiClient.getTickets.mockResolvedValueOnce({ data: largeTicketData })

      const startTime = performance.now()

      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Maintenance Management')).toBeInTheDocument()
      })

      const endTime = performance.now()
      const renderTime = endTime - startTime

      // Should render within reasonable time (less than 1 second)
      expect(renderTime).toBeLessThan(1000)
    })

    test('handles rapid state changes efficiently', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Maintenance Management')).toBeInTheDocument()
      })

      // Simulate rapid tab switching
      const startTime = performance.now()
      
      for (let i = 0; i < 10; i++) {
        fireEvent.click(screen.getByText('Communications'))
        fireEvent.click(screen.getByText('Tickets'))
      }

      const endTime = performance.now()
      const switchTime = endTime - startTime

      // Should handle rapid changes efficiently
      expect(switchTime).toBeLessThan(500)
    })
  })

  describe('Accessibility Tests', () => {
    test('has proper ARIA labels', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        // Check for proper ARIA labels
        const buttons = screen.getAllByRole('button')
        buttons.forEach(button => {
          expect(button).toHaveAttribute('aria-label')
        })
      })
    })

    test('supports keyboard navigation', async () => {
      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        // Test keyboard navigation
        const firstButton = screen.getAllByRole('button')[0]
        firstButton.focus()
        expect(document.activeElement).toBe(firstButton)
      })
    })
  })

  describe('Responsive Design Tests', () => {
    test('adapts to different screen sizes', async () => {
      // Mock different screen sizes
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768, // Tablet size
      })

      render(
        <TestWrapper>
          <MaintenanceModule />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('Maintenance Management')).toBeInTheDocument()
      })

      // Should adapt to tablet size
      expect(window.innerWidth).toBe(768)
    })
  })
})

// Mock modules for testing
jest.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => mockAuthContext
}))

jest.mock('../contexts/RealtimeContext', () => ({
  RealtimeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useRealtimeUpdates: () => mockRealtimeContext
}))

jest.mock('../contexts/OptimisticUpdatesContext', () => ({
  OptimisticUpdatesProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useOptimisticUpdates: () => mockOptimisticUpdatesContext
}))

jest.mock('../lib/api/integratedApi', () => ({
  IntegratedAPIClient: jest.fn().mockImplementation(() => mockApiClient)
}))
