// PWA Manager - Progressive Web App Management
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

interface PWAConfig {
  name: string;
  short_name: string;
  description: string;
  theme_color: string;
  background_color: string;
  display: string;
  orientation: string;
  scope: string;
  start_url: string;
  icons: Array<{
    src: string;
    sizes: string;
    type: string;
    purpose?: string;
  }>;
}

interface OfflineData {
  customers: any[];
  opportunities: any[];
  contacts: any[];
  activities: any[];
  lastSync: string;
}

interface PWAManagerProps {
  onInstallPrompt?: (event: any) => void;
  onOfflineData?: (data: OfflineData) => void;
}

const PWAManager: React.FC<PWAManagerProps> = ({ onInstallPrompt, onOfflineData }) => {
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineData, setOfflineData] = useState<OfflineData | null>(null);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');

  // PWA Configuration
  const pwaConfig: PWAConfig = {
    name: "Advanced CRM System",
    short_name: "CRM Pro",
    description: "Advanced Customer Relationship Management System",
    theme_color: "#2563eb",
    background_color: "#ffffff",
    display: "standalone",
    orientation: "portrait-primary",
    scope: "/",
    start_url: "/",
    icons: [
      {
        src: "/icons/icon-72x72.png",
        sizes: "72x72",
        type: "image/png"
      },
      {
        src: "/icons/icon-96x96.png",
        sizes: "96x96",
        type: "image/png"
      },
      {
        src: "/icons/icon-128x128.png",
        sizes: "128x128",
        type: "image/png"
      },
      {
        src: "/icons/icon-144x144.png",
        sizes: "144x144",
        type: "image/png"
      },
      {
        src: "/icons/icon-152x152.png",
        sizes: "152x152",
        type: "image/png"
      },
      {
        src: "/icons/icon-192x192.png",
        sizes: "192x192",
        type: "image/png"
      },
      {
        src: "/icons/icon-384x384.png",
        sizes: "384x384",
        type: "image/png"
      },
      {
        src: "/icons/icon-512x512.png",
        sizes: "512x512",
        type: "image/png"
      }
    ]
  };

  useEffect(() => {
    // Check if PWA is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    // Listen for install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    });

    // Listen for app installed
    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setIsInstallable(false);
      toast.success('CRM App installed successfully!');
    });

    // Listen for online/offline status
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initialize offline data
    initializeOfflineData();

    // Register service worker
    registerServiceWorker();

    return () => {
      window.removeEventListener('beforeinstallprompt', () => {});
      window.removeEventListener('appinstalled', () => {});
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleOnline = () => {
    setIsOnline(true);
    toast.success('Connection restored');
    syncOfflineData();
  };

  const handleOffline = () => {
    setIsOnline(false);
    toast.warning('You are now offline. Some features may be limited.');
  };

  const initializeOfflineData = async () => {
    try {
      const cachedData = await getOfflineData();
      if (cachedData) {
        setOfflineData(cachedData);
        onOfflineData?.(cachedData);
      }
    } catch (error) {
      console.error('Error initializing offline data:', error);
    }
  };

  const getOfflineData = async (): Promise<OfflineData | null> => {
    try {
      if ('caches' in window) {
        const cache = await caches.open('crm-offline-v1');
        const response = await cache.match('/api/offline-data');
        if (response) {
          return await response.json();
        }
      }
      return null;
    } catch (error) {
      console.error('Error getting offline data:', error);
      return null;
    }
  };

  const setOfflineDataCache = async (data: OfflineData) => {
    try {
      if ('caches' in window) {
        const cache = await caches.open('crm-offline-v1');
        await cache.put('/api/offline-data', new Response(JSON.stringify(data)));
      }
    } catch (error) {
      console.error('Error setting offline data:', error);
    }
  };

  const registerServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', registration);
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  };

  const installPWA = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('PWA installation accepted');
      } else {
        console.log('PWA installation dismissed');
      }
      
      setDeferredPrompt(null);
      setIsInstallable(false);
    }
  };

  const syncOfflineData = async () => {
    if (!isOnline || !offlineData) return;

    setSyncStatus('syncing');
    
    try {
      // Sync customers
      if (offlineData.customers.length > 0) {
        await syncCustomers(offlineData.customers);
      }

      // Sync opportunities
      if (offlineData.opportunities.length > 0) {
        await syncOpportunities(offlineData.opportunities);
      }

      // Sync contacts
      if (offlineData.contacts.length > 0) {
        await syncContacts(offlineData.contacts);
      }

      // Sync activities
      if (offlineData.activities.length > 0) {
        await syncActivities(offlineData.activities);
      }

      setSyncStatus('success');
      toast.success('Data synchronized successfully');
      
      // Clear offline data after successful sync
      setOfflineData(null);
      if ('caches' in window) {
        const cache = await caches.open('crm-offline-v1');
        await cache.delete('/api/offline-data');
      }
    } catch (error) {
      setSyncStatus('error');
      toast.error('Sync failed. Please try again.');
      console.error('Sync error:', error);
    }
  };

  const syncCustomers = async (customers: any[]) => {
    for (const customer of customers) {
      try {
        const response = await fetch('/api/customers', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(customer),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to sync customer ${customer.id}`);
        }
      } catch (error) {
        console.error('Error syncing customer:', error);
        throw error;
      }
    }
  };

  const syncOpportunities = async (opportunities: any[]) => {
    for (const opportunity of opportunities) {
      try {
        const response = await fetch('/api/opportunities', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(opportunity),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to sync opportunity ${opportunity.id}`);
        }
      } catch (error) {
        console.error('Error syncing opportunity:', error);
        throw error;
      }
    }
  };

  const syncContacts = async (contacts: any[]) => {
    for (const contact of contacts) {
      try {
        const response = await fetch('/api/contacts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(contact),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to sync contact ${contact.id}`);
        }
      } catch (error) {
        console.error('Error syncing contact:', error);
        throw error;
      }
    }
  };

  const syncActivities = async (activities: any[]) => {
    for (const activity of activities) {
      try {
        const response = await fetch('/api/activities', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(activity),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to sync activity ${activity.id}`);
        }
      } catch (error) {
        console.error('Error syncing activity:', error);
        throw error;
      }
    }
  };

  const saveOfflineData = async (data: OfflineData) => {
    setOfflineData(data);
    await setOfflineDataCache(data);
    onOfflineData?.(data);
  };

  const getConnectionStatus = () => {
    if (isOnline) {
      return { status: 'online', message: 'Connected' };
    } else {
      return { status: 'offline', message: 'Offline - Limited functionality' };
    }
  };

  const getSyncStatus = () => {
    switch (syncStatus) {
      case 'syncing':
        return { status: 'syncing', message: 'Synchronizing data...' };
      case 'success':
        return { status: 'success', message: 'Data synchronized' };
      case 'error':
        return { status: 'error', message: 'Sync failed' };
      default:
        return { status: 'idle', message: 'Ready' };
    }
  };

  return {
    // PWA State
    isInstallable,
    isInstalled,
    isOnline,
    offlineData,
    syncStatus,
    
    // PWA Actions
    installPWA,
    syncOfflineData,
    saveOfflineData,
    
    // PWA Configuration
    pwaConfig,
    
    // Status Functions
    getConnectionStatus,
    getSyncStatus,
    
    // PWA Features
    features: {
      offlineSupport: true,
      pushNotifications: true,
      backgroundSync: true,
      installPrompt: isInstallable,
      dataSync: true,
      cacheManagement: true
    }
  };
};

export default PWAManager;
