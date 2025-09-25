// Personalization Manager - Advanced User Personalization

import React, { useState, useEffect, useContext } from 'react';
import { toast } from 'react-toastify';

interface PersonalizationConfig {
  userId: string;
  preferences: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    timezone: string;
    dateFormat: string;
    currency: string;
    notifications: {
      email: boolean;
      push: boolean;
      sms: boolean;
      inApp: boolean;
    };
    dashboard: {
      layout: 'grid' | 'list' | 'compact';
      widgets: string[];
      columns: number;
    };
    views: {
      customers: {
        defaultView: string;
        columns: string[];
        filters: any[];
        sortBy: string;
        sortOrder: 'asc' | 'desc';
      };
      opportunities: {
        defaultView: string;
        columns: string[];
        filters: any[];
        sortBy: string;
        sortOrder: 'asc' | 'desc';
      };
      contacts: {
        defaultView: string;
        columns: string[];
        filters: any[];
        sortBy: string;
        sortOrder: 'asc' | 'desc';
      };
    };
    automation: {
      autoSave: boolean;
      autoRefresh: boolean;
      autoSync: boolean;
      smartSuggestions: boolean;
    };
    accessibility: {
      fontSize: 'small' | 'medium' | 'large';
      contrast: 'normal' | 'high';
      animations: boolean;
      keyboardNavigation: boolean;
    };
  };
  customizations: {
    customFields: any[];
    customViews: any[];
    customReports: any[];
    customWorkflows: any[];
    customDashboards: any[];
  };
  lastUpdated: string;
}

interface PersonalizationManagerProps {
  userId: string;
  onPersonalizationChange?: (config: PersonalizationConfig) => void;
}

const PersonalizationManager: React.FC<PersonalizationManagerProps> = ({ 
  userId, 
  onPersonalizationChange 
}) => {
  const [personalizationConfig, setPersonalizationConfig] = useState<PersonalizationConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadPersonalizationConfig();
  }, [userId]);

  const loadPersonalizationConfig = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/personalization/${userId}`);
      if (response.ok) {
        const config = await response.json();
        setPersonalizationConfig(config);
      } else {
        // Create default configuration
        const defaultConfig = createDefaultConfig();
        setPersonalizationConfig(defaultConfig);
      }
    } catch (error) {
      console.error('Error loading personalization config:', error);
      const defaultConfig = createDefaultConfig();
      setPersonalizationConfig(defaultConfig);
    } finally {
      setIsLoading(false);
    }
  };

  const createDefaultConfig = (): PersonalizationConfig => {
    return {
      userId,
      preferences: {
        theme: 'light',
        language: 'en',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        dateFormat: 'MM/DD/YYYY',
        currency: 'USD',
        notifications: {
          email: true,
          push: true,
          sms: false,
          inApp: true
        },
        dashboard: {
          layout: 'grid',
          widgets: ['customers', 'opportunities', 'activities', 'reports'],
          columns: 3
        },
        views: {
          customers: {
            defaultView: 'list',
            columns: ['name', 'email', 'phone', 'status', 'last_activity'],
            filters: [],
            sortBy: 'name',
            sortOrder: 'asc'
          },
          opportunities: {
            defaultView: 'list',
            columns: ['name', 'customer', 'value', 'stage', 'close_date'],
            filters: [],
            sortBy: 'close_date',
            sortOrder: 'desc'
          },
          contacts: {
            defaultView: 'list',
            columns: ['name', 'email', 'phone', 'company', 'last_contact'],
            filters: [],
            sortBy: 'name',
            sortOrder: 'asc'
          }
        },
        automation: {
          autoSave: true,
          autoRefresh: true,
          autoSync: true,
          smartSuggestions: true
        },
        accessibility: {
          fontSize: 'medium',
          contrast: 'normal',
          animations: true,
          keyboardNavigation: true
        }
      },
      customizations: {
        customFields: [],
        customViews: [],
        customReports: [],
        customWorkflows: [],
        customDashboards: []
      },
      lastUpdated: new Date().toISOString()
    };
  };

  const savePersonalizationConfig = async (config: PersonalizationConfig) => {
    try {
      setIsSaving(true);
      const response = await fetch(`/api/personalization/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        setPersonalizationConfig(config);
        onPersonalizationChange?.(config);
        toast.success('Personalization settings saved successfully');
      } else {
        throw new Error('Failed to save personalization settings');
      }
    } catch (error) {
      console.error('Error saving personalization config:', error);
      toast.error('Failed to save personalization settings');
    } finally {
      setIsSaving(false);
    }
  };

  const updatePreference = (path: string, value: any) => {
    if (!personalizationConfig) return;

    const newConfig = { ...personalizationConfig };
    const keys = path.split('.');
    let current = newConfig.preferences;

    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }

    current[keys[keys.length - 1]] = value;
    newConfig.lastUpdated = new Date().toISOString();

    setPersonalizationConfig(newConfig);
    savePersonalizationConfig(newConfig);
  };

  const updateCustomization = (type: string, item: any) => {
    if (!personalizationConfig) return;

    const newConfig = { ...personalizationConfig };
    newConfig.customizations[type].push(item);
    newConfig.lastUpdated = new Date().toISOString();

    setPersonalizationConfig(newConfig);
    savePersonalizationConfig(newConfig);
  };

  const removeCustomization = (type: string, index: number) => {
    if (!personalizationConfig) return;

    const newConfig = { ...personalizationConfig };
    newConfig.customizations[type].splice(index, 1);
    newConfig.lastUpdated = new Date().toISOString();

    setPersonalizationConfig(newConfig);
    savePersonalizationConfig(newConfig);
  };

  const resetToDefaults = () => {
    const defaultConfig = createDefaultConfig();
    setPersonalizationConfig(defaultConfig);
    savePersonalizationConfig(defaultConfig);
    toast.success('Personalization settings reset to defaults');
  };

  const exportPersonalization = () => {
    if (!personalizationConfig) return;

    const dataStr = JSON.stringify(personalizationConfig, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `personalization-${userId}-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const importPersonalization = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const config = JSON.parse(e.target?.result as string);
        setPersonalizationConfig(config);
        savePersonalizationConfig(config);
        toast.success('Personalization settings imported successfully');
      } catch (error) {
        console.error('Error importing personalization config:', error);
        toast.error('Failed to import personalization settings');
      }
    };
    reader.readAsText(file);
  };

  const getPersonalizationSummary = () => {
    if (!personalizationConfig) return null;

    return {
      theme: personalizationConfig.preferences.theme,
      language: personalizationConfig.preferences.language,
      timezone: personalizationConfig.preferences.timezone,
      currency: personalizationConfig.preferences.currency,
      notifications: Object.values(personalizationConfig.preferences.notifications).filter(Boolean).length,
      customizations: Object.values(personalizationConfig.customizations).reduce((total, items) => total + items.length, 0),
      lastUpdated: personalizationConfig.lastUpdated
    };
  };

  const getAccessibilitySettings = () => {
    if (!personalizationConfig) return null;

    return {
      fontSize: personalizationConfig.preferences.accessibility.fontSize,
      contrast: personalizationConfig.preferences.accessibility.contrast,
      animations: personalizationConfig.preferences.accessibility.animations,
      keyboardNavigation: personalizationConfig.preferences.accessibility.keyboardNavigation
    };
  };

  const applyAccessibilitySettings = () => {
    if (!personalizationConfig) return;

    const { fontSize, contrast, animations, keyboardNavigation } = personalizationConfig.preferences.accessibility;

    // Apply font size
    document.documentElement.style.fontSize = fontSize === 'small' ? '14px' : fontSize === 'large' ? '18px' : '16px';

    // Apply contrast
    if (contrast === 'high') {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }

    // Apply animations
    if (!animations) {
      document.documentElement.classList.add('no-animations');
    } else {
      document.documentElement.classList.remove('no-animations');
    }

    // Apply keyboard navigation
    if (keyboardNavigation) {
      document.documentElement.classList.add('keyboard-navigation');
    } else {
      document.documentElement.classList.remove('keyboard-navigation');
    }
  };

  useEffect(() => {
    if (personalizationConfig) {
      applyAccessibilitySettings();
    }
  }, [personalizationConfig]);

  return {
    // Personalization State
    personalizationConfig,
    isLoading,
    isSaving,

    // Personalization Actions
    updatePreference,
    updateCustomization,
    removeCustomization,
    resetToDefaults,
    exportPersonalization,
    importPersonalization,

    // Personalization Utilities
    getPersonalizationSummary,
    getAccessibilitySettings,
    applyAccessibilitySettings,

    // Personalization Features
    features: {
      themeCustomization: true,
      languageSupport: true,
      timezoneSupport: true,
      currencySupport: true,
      notificationPreferences: true,
      dashboardCustomization: true,
      viewCustomization: true,
      automationSettings: true,
      accessibilitySettings: true,
      customFields: true,
      customViews: true,
      customReports: true,
      customWorkflows: true,
      customDashboards: true,
      importExport: true
    }
  };
};

export default PersonalizationManager;
