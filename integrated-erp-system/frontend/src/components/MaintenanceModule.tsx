import React, { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { 
  TicketSystem, 
  CommunicationHub, 
  SLAManagement, 
  KnowledgeBase,
  TicketAnalytics 
} from './maintenance'
import { 
  Wrench, 
  MessageSquare, 
  Clock, 
  BookOpen, 
  BarChart3,
  Plus,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react'

interface MaintenanceModuleProps {}

export const MaintenanceModule: React.FC<MaintenanceModuleProps> = () => {
  const [activeTab, setActiveTab] = useState('tickets')
  const [refreshKey, setRefreshKey] = useState(0)

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1)
  }

  const getQuickStats = () => [
    {
      title: 'Open Tickets',
      value: '24',
      change: '+12%',
      trend: 'up',
      color: 'text-blue-600',
      icon: <Wrench className="h-4 w-4" />
    },
    {
      title: 'Avg Response Time',
      value: '2.3h',
      change: '-15%',
      trend: 'down',
      color: 'text-green-600',
      icon: <Clock className="h-4 w-4" />
    },
    {
      title: 'SLA Compliance',
      value: '94%',
      change: '+3%',
      trend: 'up',
      color: 'text-green-600',
      icon: <Clock className="h-4 w-4" />
    },
    {
      title: 'Customer Satisfaction',
      value: '4.7/5',
      change: '+0.2',
      trend: 'up',
      color: 'text-yellow-600',
      icon: <MessageSquare className="h-4 w-4" />
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Maintenance Management</h1>
          <p className="text-muted-foreground">
            Advanced ticket system with AI-powered features and real-time analytics
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
            New Ticket
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
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="tickets" className="flex items-center space-x-2">
            <Wrench className="h-4 w-4" />
            <span>Tickets</span>
          </TabsTrigger>
          <TabsTrigger value="communications" className="flex items-center space-x-2">
            <MessageSquare className="h-4 w-4" />
            <span>Communications</span>
          </TabsTrigger>
          <TabsTrigger value="sla" className="flex items-center space-x-2">
            <Clock className="h-4 w-4" />
            <span>SLA Management</span>
          </TabsTrigger>
          <TabsTrigger value="knowledge" className="flex items-center space-x-2">
            <BookOpen className="h-4 w-4" />
            <span>Knowledge Base</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Analytics</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tickets">
          <TicketSystem key={refreshKey} />
        </TabsContent>

        <TabsContent value="communications">
          <CommunicationHub key={refreshKey} />
        </TabsContent>

        <TabsContent value="sla">
          <SLAManagement key={refreshKey} />
        </TabsContent>

        <TabsContent value="knowledge">
          <KnowledgeBase key={refreshKey} />
        </TabsContent>

        <TabsContent value="analytics">
          <TicketAnalytics key={refreshKey} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
