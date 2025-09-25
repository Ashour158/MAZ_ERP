import React, { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { 
  InventoryTable, 
  PurchaseAnalytics, 
  ReorderIntelligence, 
  SmartPOGenerator,
  VendorPerformance,
  SupplyChainAnalytics
} from './supply-chain'
import { 
  Package, 
  ShoppingCart, 
  Brain, 
  Zap, 
  Building2, 
  BarChart3,
  Plus,
  Download,
  RefreshCw
} from 'lucide-react'

interface SupplyChainModuleProps {}

export const SupplyChainModule: React.FC<SupplyChainModuleProps> = () => {
  const [activeTab, setActiveTab] = useState('inventory')
  const [refreshKey, setRefreshKey] = useState(0)

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1)
  }

  const getQuickStats = () => [
    {
      title: 'Total Inventory Value',
      value: '$2.4M',
      change: '+8%',
      trend: 'up',
      color: 'text-green-600',
      icon: <Package className="h-4 w-4" />
    },
    {
      title: 'Reorder Recommendations',
      value: '47',
      change: '+23%',
      trend: 'up',
      color: 'text-blue-600',
      icon: <Brain className="h-4 w-4" />
    },
    {
      title: 'Vendor Performance',
      value: '92%',
      change: '+5%',
      trend: 'up',
      color: 'text-green-600',
      icon: <Building2 className="h-4 w-4" />
    },
    {
      title: 'Cost Savings',
      value: '$45K',
      change: '+12%',
      trend: 'up',
      color: 'text-yellow-600',
      icon: <Zap className="h-4 w-4" />
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Supply Chain Management</h1>
          <p className="text-muted-foreground">
            Intelligent supply chain with AI-powered recommendations and real-time analytics
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Order
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {getQuickStats().map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <div className="flex items-center space-x-1 mt-1">
                    <Badge 
                      variant={stat.trend === 'up' ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {stat.change}
                    </Badge>
                    <span className="text-xs text-muted-foreground">vs last month</span>
                  </div>
                </div>
                <div className={`p-2 rounded-lg ${stat.color} bg-opacity-10`}>
                  {stat.icon}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="inventory" className="flex items-center space-x-2">
            <Package className="h-4 w-4" />
            <span>Inventory</span>
          </TabsTrigger>
          <TabsTrigger value="purchases" className="flex items-center space-x-2">
            <ShoppingCart className="h-4 w-4" />
            <span>Purchases</span>
          </TabsTrigger>
          <TabsTrigger value="reorder" className="flex items-center space-x-2">
            <Brain className="h-4 w-4" />
            <span>Reorder AI</span>
          </TabsTrigger>
          <TabsTrigger value="smart-po" className="flex items-center space-x-2">
            <Zap className="h-4 w-4" />
            <span>Smart PO</span>
          </TabsTrigger>
          <TabsTrigger value="vendors" className="flex items-center space-x-2">
            <Building2 className="h-4 w-4" />
            <span>Vendors</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Analytics</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="inventory">
          <InventoryTable key={refreshKey} />
        </TabsContent>

        <TabsContent value="purchases">
          <PurchaseAnalytics key={refreshKey} />
        </TabsContent>

        <TabsContent value="reorder">
          <ReorderIntelligence key={refreshKey} />
        </TabsContent>

        <TabsContent value="smart-po">
          <SmartPOGenerator key={refreshKey} />
        </TabsContent>

        <TabsContent value="vendors">
          <VendorPerformance key={refreshKey} />
        </TabsContent>

        <TabsContent value="analytics">
          <SupplyChainAnalytics key={refreshKey} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
