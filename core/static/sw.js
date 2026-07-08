
const CACHE_NAME = 'yathrapath-v12';

const PRECACHE_URLS = [
  '/',
  '/about/',
  '/static/css/output.css',
  '/static/manifest.json',
];

const NETWORK_FIRST = [
  '/destinations/',
  '/blog/',
  '/map/',
  '/about/',
];

// ── Install ───────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async cache => {

      // Cache offline page FIRST — this must succeed
      await cache.add('/offline.html');

      // Then cache the rest (failures are okay)
      await Promise.allSettled(
        PRECACHE_URLS.map(url =>
          cache.add(url).catch(err => console.warn('[SW] Failed to pre-cache:', url, err))
        )
      );

      // Then precache all destination detail pages
      try {
        const res = await fetch('/api/destination-ids/');
        const { ids } = await res.json();
        await Promise.allSettled(
          ids.map(id =>
            cache.add(`/destinations/${id}/`).catch(e => console.warn('[SW] detail fail:', id, e))
          )
        );
      } catch (e) {
        console.warn('[SW] Could not precache destinations:', e);
      }
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

// ── Shared offline fallback ───────────────────────────────
async function offlineFallback(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const offline = await caches.match('/offline.html');
  if (offline) return offline;
  return new Response(
    '<!DOCTYPE html><html><body style="background:#050508;color:#eab308;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center"><h1>You are offline</h1></body></html>',
    { headers: { 'Content-Type': 'text/html' } }
  );
}

// ── Fetch ─────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  if (url.pathname.startsWith('/admin/')) return;

  const isDynamic = NETWORK_FIRST.some(path => url.pathname.startsWith(path))
                 || url.pathname === '/';

  if (isDynamic) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => offlineFallback(event.request))
    );
    return;
  }

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

  // Everything else
  event.respondWith(
    fetch(event.request)
      .then(response => response)
      .catch(() => offlineFallback(event.request))
  );
});

// ── Push Notifications ────────────────────────────────────
self.addEventListener('push', event => {
  let data = { title: 'YatraPath', body: 'Something new awaits!', url: '/' };
  try { data = JSON.parse(event.data.text()); } catch (_) {}

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body:             data.body,
      icon:             '/static/images/icons/icon-512.png',
      badge:            '/static/images/icons/icon-192.png',
      data:             { url: data.url },
      vibrate:          [200, 100, 200, 100, 200],
      requireInteraction: true,
      tag:              'yathrapath-' + Date.now(),
      renotify:         true,
      silent:           false,
      timestamp:        Date.now(),
      actions: [
        { action: 'open',    title: 'View' },
        { action: 'dismiss', title: 'Dismiss' },
      ],
    })
  );
});

// ── Notification Click ────────────────────────────────────
self.addEventListener('notificationclick', event => {
  event.notification.close();
  if (event.action === 'dismiss') return;

  const url = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(wins => {
      for (const win of wins) {
        if ('focus' in win) {
          win.focus();
          win.navigate?.(url);
          return;
        }
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});
