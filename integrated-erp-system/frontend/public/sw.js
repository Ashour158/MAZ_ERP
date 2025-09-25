// Service Worker for PWA CRM System
const CACHE_NAME = 'crm-pwa-v1';
const OFFLINE_CACHE = 'crm-offline-v1';
const API_CACHE = 'crm-api-v1';

// Files to cache for offline functionality
const STATIC_CACHE_URLS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/offline.html'
];

// API endpoints to cache
const API_CACHE_URLS = [
  '/api/customers',
  '/api/opportunities',
  '/api/contacts',
  '/api/activities',
  '/api/leads',
  '/api/campaigns'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
  console.log('Service Worker: Install event');
  
  event.waitUntil(
    Promise.all([
      caches.open(CACHE_NAME).then((cache) => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_CACHE_URLS);
      }),
      caches.open(OFFLINE_CACHE).then((cache) => {
        console.log('Service Worker: Setting up offline cache');
        return cache.add('/offline.html');
      })
    ])
  );
  
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activate event');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== OFFLINE_CACHE && cacheName !== API_CACHE) {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  self.clients.claim();
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // Handle static resources
  if (request.method === 'GET') {
    event.respondWith(handleStaticRequest(request));
    return;
  }
  
  // Handle other requests
  event.respondWith(fetch(request));
});

// Handle API requests with offline support
async function handleApiRequest(request) {
  const url = new URL(request.url);
  const cacheKey = `${request.method}:${url.pathname}${url.search}`;
  
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      const cache = await caches.open(API_CACHE);
      cache.put(cacheKey, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache for:', url.pathname);
    
    // Try cache
    const cache = await caches.open(API_CACHE);
    const cachedResponse = await cache.match(cacheKey);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline data if available
    if (url.pathname === '/api/offline-data') {
      return new Response(JSON.stringify({
        customers: [],
        opportunities: [],
        contacts: [],
        activities: [],
        lastSync: new Date().toISOString()
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Return offline page for other requests
    return caches.match('/offline.html');
  }
}

// Handle static resource requests
async function handleStaticRequest(request) {
  try {
    // Try cache first
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Try network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache the response
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('Service Worker: Serving offline page');
    return caches.match('/offline.html');
  }
}

// Background sync for offline data
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync event');
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Background sync implementation
async function doBackgroundSync() {
  try {
    console.log('Service Worker: Performing background sync');
    
    // Get offline data from cache
    const cache = await caches.open(OFFLINE_CACHE);
    const offlineDataResponse = await cache.match('/api/offline-data');
    
    if (offlineDataResponse) {
      const offlineData = await offlineDataResponse.json();
      
      // Sync data to server
      await syncOfflineData(offlineData);
      
      // Clear offline data after successful sync
      await cache.delete('/api/offline-data');
      
      console.log('Service Worker: Background sync completed');
    }
  } catch (error) {
    console.error('Service Worker: Background sync failed:', error);
  }
}

// Sync offline data to server
async function syncOfflineData(offlineData) {
  const syncPromises = [];
  
  // Sync customers
  if (offlineData.customers && offlineData.customers.length > 0) {
    syncPromises.push(syncCustomers(offlineData.customers));
  }
  
  // Sync opportunities
  if (offlineData.opportunities && offlineData.opportunities.length > 0) {
    syncPromises.push(syncOpportunities(offlineData.opportunities));
  }
  
  // Sync contacts
  if (offlineData.contacts && offlineData.contacts.length > 0) {
    syncPromises.push(syncContacts(offlineData.contacts));
  }
  
  // Sync activities
  if (offlineData.activities && offlineData.activities.length > 0) {
    syncPromises.push(syncActivities(offlineData.activities));
  }
  
  await Promise.all(syncPromises);
}

// Sync customers
async function syncCustomers(customers) {
  for (const customer of customers) {
    try {
      await fetch('/api/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customer)
      });
    } catch (error) {
      console.error('Error syncing customer:', error);
    }
  }
}

// Sync opportunities
async function syncOpportunities(opportunities) {
  for (const opportunity of opportunities) {
    try {
      await fetch('/api/opportunities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(opportunity)
      });
    } catch (error) {
      console.error('Error syncing opportunity:', error);
    }
  }
}

// Sync contacts
async function syncContacts(contacts) {
  for (const contact of contacts) {
    try {
      await fetch('/api/contacts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contact)
      });
    } catch (error) {
      console.error('Error syncing contact:', error);
    }
  }
}

// Sync activities
async function syncActivities(activities) {
  for (const activity of activities) {
    try {
      await fetch('/api/activities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(activity)
      });
    } catch (error) {
      console.error('Error syncing activity:', error);
    }
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push event received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification from CRM',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/icons/icon-72x72.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/icon-72x72.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('CRM Notification', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification click received');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    return;
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  console.log('Service Worker: Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_OFFLINE_DATA') {
    event.waitUntil(cacheOfflineData(event.data.data));
  }
});

// Cache offline data
async function cacheOfflineData(data) {
  try {
    const cache = await caches.open(OFFLINE_CACHE);
    await cache.put('/api/offline-data', new Response(JSON.stringify(data)));
    console.log('Service Worker: Offline data cached');
  } catch (error) {
    console.error('Service Worker: Error caching offline data:', error);
  }
}
