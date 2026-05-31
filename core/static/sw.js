/* =========================================================
   YatraPath Service Worker — v3 (Offline PWA + Push)
   ========================================================= */

const CACHE_NAME = 'yathrapath-v4';

// Core pages/assets to pre-cache for offline use
const PRECACHE_URLS = [
  '/',
  '/static/css/output.css',
  '/static/manifest.json',
  '/offline.html',
];

// These pages always fetch fresh from network (never serve from cache)
const NETWORK_FIRST = [
  '/temples/',
  '/blog/',
  '/map/',
  '/temple/',   // detail pages  
];

// ── Install ───────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(PRECACHE_URLS).catch(() => {});
    })
  );
  self.skipWaiting();
});

// ── Activate ──────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ── Fetch ─────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Always skip admin
  if (url.pathname.startsWith('/admin/')) return;

  // Network-first for dynamic pages — always get fresh content
  const isDynamic = NETWORK_FIRST.some(path => url.pathname.startsWith(path))
                 || url.pathname === '/';

  if (isDynamic) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Update cache with fresh response
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          // Only fall back to cache when truly offline
          return caches.match(event.request)
              || caches.match('/offline.html');
        })
    );
    return;
  }

  // Cache-first for static assets (CSS, JS, images, fonts)
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        return cached || fetch(event.request).then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // Everything else — network first, fall back to cache
  event.respondWith(
    fetch(event.request)
      .then(response => response)
      .catch(() => caches.match(event.request)
                || caches.match('/offline.html'))
  );
});

// ── Push Notifications ────────────────────────────────────
self.addEventListener('push', event => {
  let data = { title: 'YatraPath', body: 'Something new awaits!', url: '/' };

  try {
    data = JSON.parse(event.data.text());
  } catch (_) {}

  // keepalive: event.waitUntil keeps the SW alive until notification is shown
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body:             data.body,
      icon:             '/static/images/icons/icon-512.png',   // larger = better on Android
      badge:            '/static/images/icons/icon-192.png',   // small monochrome icon in status bar
      data:             { url: data.url },
      vibrate:          [200, 100, 200, 100, 200],             // stronger pattern = wakes screen
      requireInteraction: true,                                 // ← stays visible until user taps (Android/desktop)
      tag:              data.url || 'yathrapath',              // ← replaces old notification (no spam)
      renotify:         true,                                   // ← re-alerts even if same tag exists
      silent:           false,                                  // ← explicitly NOT silent
      timestamp:        Date.now(),
      actions: [
        { action: 'open',    title: '👁️ View' },
        { action: 'dismiss', title: '✖ Dismiss' },
      ],
    })
  );
});

// ── Notification Click ────────────────────────────────────
self.addEventListener('notificationclick', event => {
  event.notification.close();

  // Handle action buttons
  if (event.action === 'dismiss') return;

  const url = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(wins => {
      // If app already open, focus it and navigate
      for (const win of wins) {
        if ('focus' in win) {
          win.focus();
          win.navigate?.(url);
          return;
        }
      }
      // Otherwise open a new window
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});