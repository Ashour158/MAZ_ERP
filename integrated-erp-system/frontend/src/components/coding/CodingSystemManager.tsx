// Coding System Manager - Advanced Contact and Account Coding

import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

interface CodingRule {
  territory_based: boolean;
  coding_format: 'numeric' | 'alphanumeric' | 'text' | 'mixed';
  auto_generation: boolean;
  prefix?: string;
  suffix?: string;
  sequence_length: number;
  min_length: number;
  max_length: number;
  territory_mapping?: Record<string, string>;
}

interface CodingSystem {
  id: string;
  name: string;
  type: 'Contact' | 'Account' | 'Customer' | 'Lead' | 'Opportunity' | 'Campaign' | 'Activity' | 'Custom';
  category: 'Territory Based' | 'Sequential' | 'Custom' | 'Auto Generated' | 'Manual';
  status: 'Active' | 'Inactive' | 'Testing' | 'Draft' | 'Maintenance';
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  target_doctype: string;
  filter_conditions: string;
  coding_rules: CodingRule;
  efficiency: number;
  accuracy: number;
  performance: number;
  coverage: number;
  is_auto_generation_enabled: boolean;
  created_date: string;
  modified_date: string;
}

interface CodingSystemManagerProps {
  onCodingSystemChange?: (system: CodingSystem) => void;
  onCodeGenerated?: (code: string, record: any) => void;
}

const CodingSystemManager: React.FC<CodingSystemManagerProps> = ({ 
  onCodingSystemChange, 
  onCodeGenerated 
}) => {
  const [codingSystems, setCodingSystems] = useState<CodingSystem[]>([]);
  const [selectedSystem, setSelectedSystem] = useState<CodingSystem | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);

  useEffect(() => {
    loadCodingSystems();
  }, []);

  const loadCodingSystems = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/coding-systems');
      if (response.ok) {
        const systems = await response.json();
        setCodingSystems(systems);
      } else {
        throw new Error('Failed to load coding systems');
      }
    } catch (error) {
      console.error('Error loading coding systems:', error);
      toast.error('Failed to load coding systems');
    } finally {
      setIsLoading(false);
    }
  };

  const createCodingSystem = async (systemData: Partial<CodingSystem>) => {
    try {
      setIsSaving(true);
      const response = await fetch('/api/coding-systems', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(systemData)
      });

      if (response.ok) {
        const newSystem = await response.json();
        setCodingSystems([...codingSystems, newSystem]);
        setShowCreateModal(false);
        toast.success('Coding system created successfully');
        onCodingSystemChange?.(newSystem);
      } else {
        throw new Error('Failed to create coding system');
      }
    } catch (error) {
      console.error('Error creating coding system:', error);
      toast.error('Failed to create coding system');
    } finally {
      setIsSaving(false);
    }
  };

  const updateCodingSystem = async (systemId: string, systemData: Partial<CodingSystem>) => {
    try {
      setIsSaving(true);
      const response = await fetch(`/api/coding-systems/${systemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(systemData)
      });

      if (response.ok) {
        const updatedSystem = await response.json();
        setCodingSystems(codingSystems.map(system => 
          system.id === systemId ? updatedSystem : system
        ));
        setShowEditModal(false);
        toast.success('Coding system updated successfully');
        onCodingSystemChange?.(updatedSystem);
      } else {
        throw new Error('Failed to update coding system');
      }
    } catch (error) {
      console.error('Error updating coding system:', error);
      toast.error('Failed to update coding system');
    } finally {
      setIsSaving(false);
    }
  };

  const deleteCodingSystem = async (systemId: string) => {
    try {
      const response = await fetch(`/api/coding-systems/${systemId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setCodingSystems(codingSystems.filter(system => system.id !== systemId));
        toast.success('Coding system deleted successfully');
      } else {
        throw new Error('Failed to delete coding system');
      }
    } catch (error) {
      console.error('Error deleting coding system:', error);
      toast.error('Failed to delete coding system');
    }
  };

  const generateCode = async (systemId: string, recordData: any, territory?: string) => {
    try {
      const response = await fetch(`/api/coding-systems/${systemId}/generate-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ recordData, territory })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          toast.success('Code generated successfully');
          onCodeGenerated?.(result.code, recordData);
          return result.code;
        } else {
          throw new Error(result.message);
        }
      } else {
        throw new Error('Failed to generate code');
      }
    } catch (error) {
      console.error('Error generating code:', error);
      toast.error('Failed to generate code');
      return null;
    }
  };

  const testCodingSystem = async (systemId: string, testData: any) => {
    try {
      const response = await fetch(`/api/coding-systems/${systemId}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData)
      });

      if (response.ok) {
        const result = await response.json();
        return result;
      } else {
        throw new Error('Failed to test coding system');
      }
    } catch (error) {
      console.error('Error testing coding system:', error);
      toast.error('Failed to test coding system');
      return null;
    }
  };

  const exportCodedData = async (systemId: string, filters?: any) => {
    try {
      const response = await fetch(`/api/coding-systems/${systemId}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filters })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          // Download the exported data
          const dataStr = JSON.stringify(result.data, null, 2);
          const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
          
          const exportFileDefaultName = `coded-data-${systemId}-${new Date().toISOString().split('T')[0]}.json`;
          
          const linkElement = document.createElement('a');
          linkElement.setAttribute('href', dataUri);
          linkElement.setAttribute('download', exportFileDefaultName);
          linkElement.click();
          
          toast.success('Data exported successfully with codes');
        } else {
          throw new Error(result.message);
        }
      } else {
        throw new Error('Failed to export data');
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      toast.error('Failed to export data');
    }
  };

  const getCodingSystemInsights = async (systemId: string) => {
    try {
      const response = await fetch(`/api/coding-systems/${systemId}/insights`);
      if (response.ok) {
        const insights = await response.json();
        return insights;
      } else {
        throw new Error('Failed to get coding system insights');
      }
    } catch (error) {
      console.error('Error getting coding system insights:', error);
      return null;
    }
  };

  const getCodingSystemDashboard = async (systemId: string) => {
    try {
      const response = await fetch(`/api/coding-systems/${systemId}/dashboard`);
      if (response.ok) {
        const dashboard = await response.json();
        return dashboard;
      } else {
        throw new Error('Failed to get coding system dashboard');
      }
    } catch (error) {
      console.error('Error getting coding system dashboard:', error);
      return null;
    }
  };

  const validateCodingRules = (rules: CodingRule): string[] => {
    const errors: string[] = [];
    
    if (!rules.coding_format) {
      errors.push('Coding format is required');
    }
    
    if (rules.territory_based && !rules.territory_mapping) {
      errors.push('Territory mapping is required for territory-based coding');
    }
    
    if (rules.sequence_length < 1 || rules.sequence_length > 10) {
      errors.push('Sequence length must be between 1 and 10');
    }
    
    if (rules.min_length < 1 || rules.min_length > 20) {
      errors.push('Minimum length must be between 1 and 20');
    }
    
    if (rules.max_length < rules.min_length || rules.max_length > 50) {
      errors.push('Maximum length must be greater than minimum length and less than 50');
    }
    
    return errors;
  };

  const getCodingSystemStatus = (status: string) => {
    const statusConfig = {
      'Active': { color: 'green', text: 'Active' },
      'Inactive': { color: 'gray', text: 'Inactive' },
      'Testing': { color: 'yellow', text: 'Testing' },
      'Draft': { color: 'blue', text: 'Draft' },
      'Maintenance': { color: 'orange', text: 'Maintenance' }
    };
    
    return statusConfig[status] || { color: 'gray', text: status };
  };

  const getCodingSystemPriority = (priority: string) => {
    const priorityConfig = {
      'Low': { color: 'green', text: 'Low' },
      'Medium': { color: 'yellow', text: 'Medium' },
      'High': { color: 'orange', text: 'High' },
      'Critical': { color: 'red', text: 'Critical' }
    };
    
    return priorityConfig[priority] || { color: 'gray', text: priority };
  };

  const getCodingSystemMetrics = (system: CodingSystem) => {
    return {
      efficiency: system.efficiency,
      accuracy: system.accuracy,
      performance: system.performance,
      coverage: system.coverage,
      overall: (system.efficiency + system.accuracy + system.performance + system.coverage) / 4
    };
  };

  const getCodingSystemInsights = (system: CodingSystem) => {
    const metrics = getCodingSystemMetrics(system);
    const insights = [];
    
    if (metrics.efficiency < 80) {
      insights.push('Consider optimizing coding efficiency');
    }
    
    if (metrics.accuracy < 90) {
      insights.push('Improve coding accuracy');
    }
    
    if (metrics.performance < 80) {
      insights.push('Enhance coding performance');
    }
    
    if (metrics.coverage < 95) {
      insights.push('Increase coding coverage');
    }
    
    if (insights.length === 0) {
      insights.push('Coding system is performing well');
    }
    
    return insights;
  };

  return {
    // Coding System State
    codingSystems,
    selectedSystem,
    isLoading,
    isSaving,
    showCreateModal,
    showEditModal,
    showTestModal,

    // Coding System Actions
    createCodingSystem,
    updateCodingSystem,
    deleteCodingSystem,
    generateCode,
    testCodingSystem,
    exportCodedData,
    getCodingSystemInsights,
    getCodingSystemDashboard,

    // Coding System Utilities
    validateCodingRules,
    getCodingSystemStatus,
    getCodingSystemPriority,
    getCodingSystemMetrics,
    getCodingSystemInsights,

    // Modal Controls
    setShowCreateModal,
    setShowEditModal,
    setShowTestModal,
    setSelectedSystem,

    // Coding System Features
    features: {
      territoryBasedCoding: true,
      autoGeneration: true,
      customRules: true,
      validation: true,
      testing: true,
      export: true,
      analytics: true,
      insights: true,
      dashboard: true,
      monitoring: true
    }
  };
};

export default CodingSystemManager;
