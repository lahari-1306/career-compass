// CareerCompass Production Service Worker for Web Push & Offline Support
const CACHE_NAME = 'careercompass-v2';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

// Push Event: Receive Encrypted Web Push Notification from Server
self.addEventListener('push', (event) => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'CareerCompass Alert', body: event.data.text() };
    }
  }

  const title = data.title || '🧭 CareerCompass Opportunity Alert';
  const options = {
    body: data.body || 'A new verified educational opportunity has been detected for your profile.',
    icon: data.icon || '/favicon.ico',
    badge: data.badge || '/favicon.ico',
    vibrate: [200, 100, 200],
    tag: data.tag || 'careercompass-notif',
    renotify: true,
    data: {
      url: (data.data && data.data.url) ? data.data.url : '/'
    },
    actions: [
      { action: 'open_url', title: 'View Opportunity' },
      { action: 'close', title: 'Dismiss' }
    ]
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// Notification Click Event: Focus or Open Target Application URL
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  const targetUrl = (event.notification.data && event.notification.data.url) 
    ? event.notification.data.url 
    : '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      // If there's an existing CareerCompass window, focus it and navigate
      for (let client of windowClients) {
        if ('focus' in client) {
          if (client.url.includes(self.location.origin)) {
            client.focus();
            if ('navigate' in client && targetUrl !== '/') {
              client.navigate(targetUrl);
            }
            return;
          }
        }
      }
      // If no window is open, open a new browser window
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
