/* =========================================================
   YatraPath Service Worker — v4 (Offline PWA + Push + Map Cache)
   ========================================================= */

const CACHE_NAME    = 'yathrapath-v5';
const TILE_CACHE    = 'yathrapath-tiles-v2';    // map tiles — separate so we can limit size
const GEOJSON_CACHE = 'yathrapath-geojson-v2';  // state borders GeoJSON

const TILE_MAX     = 500;                  // max cached tiles (each ~10–30 KB)
const TILE_TTL_SEC = 60 * 60 * 24 * 30;   // 30 days

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

// External tile providers to intercept
const TILE_ORIGINS = [
  'basemaps.cartocdn.com',
  'tile.openstreetmap.org',
  'tile.opentopomap.org',
  'server.arcgisonline.com',
];

// GeoJSON state border sources — cache indefinitely (borders never change)
const GEOJSON_ORIGINS = [
  'raw.githubusercontent.com',
];

// ── Helpers ───────────────────────────────────────────────
async function trimCache(cacheName, maxItems) {
  const cache = await caches.open(cacheName);
  const keys  = await cache.keys();
  if (keys.length > maxItems) {
    // Delete oldest entries first (FIFO)
    await Promise.all(
      keys.slice(0, keys.length - maxItems).map(k => cache.delete(k))
    );
  }
}

function isTileRequest(url) {
  return TILE_ORIGINS.some(o => url.hostname.includes(o));
}

function isGeoJSONRequest(url) {
  return GEOJSON_ORIGINS.some(o => url.hostname.includes(o))
      && url.pathname.endsWith('.geojson');
}

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
        keys
          .filter(k => ![CACHE_NAME, TILE_CACHE, GEOJSON_CACHE].includes(k))
          .map(k => caches.delete(k))
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

  // ── 1. Map tiles — cache-first, 30-day TTL, max 500 tiles ──
  if (isTileRequest(url)) {
    event.respondWith(
      caches.open(TILE_CACHE).then(async cache => {
        const cached = await cache.match(event.request);
        if (cached) {
          // Check TTL stored in custom header we inject on save
          const ageHeader = cached.headers.get('sw-cached-at');
          const age = ageHeader ? (Date.now() - Number(ageHeader)) / 1000 : 0;
          if (age < TILE_TTL_SEC) return cached;   // still fresh
        }
        // Fetch fresh tile
        try {
          const response = await fetch(event.request);
          if (response && response.status === 200) {
            // Clone and inject timestamp header so we can check TTL later
            const headers = new Headers(response.headers);
            headers.set('sw-cached-at', String(Date.now()));
            const stamped = new Response(await response.clone().arrayBuffer(), {
              status: response.status,
              statusText: response.statusText,
              headers,
            });
            cache.put(event.request, stamped);
            trimCache(TILE_CACHE, TILE_MAX);   // keep cache bounded
          }
          return response;
        } catch {
          return cached || new Response('Tile unavailable offline', { status: 503 });
        }
      })
    );
    return;
  }

  // ── 2. GeoJSON borders — cache-first, never expire (borders don't change) ──
  if (isGeoJSONRequest(url)) {
    event.respondWith(
      caches.open(GEOJSON_CACHE).then(async cache => {
        const cached = await cache.match(event.request);
        if (cached) return cached;   // instant — no network at all
        try {
          const response = await fetch(event.request);
          if (response && response.status === 200) {
            cache.put(event.request, response.clone());
          }
          return response;
        } catch {
          return new Response('{"error":"offline"}', {
            status: 503,
            headers: { 'Content-Type': 'application/json' },
          });
        }
      })
    );
    return;
  }

  // ── 3. Dynamic Django pages — network-first, cache fallback ──
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
        .catch(() =>
          caches.match(event.request).then(c => c || caches.match('/offline.html'))
        )
    );
    return;
  }

  // ── 4. Static assets (/static/) — cache-first ──
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

  // ── 5. Everything else — network-first, fallback to cache ──
  event.respondWith(
    fetch(event.request)
      .then(response => response)
      .catch(() =>
        caches.match(event.request).then(c => c || caches.match('/offline.html'))
      )
  );
});

// ── Push Notifications ────────────────────────────────────
self.addEventListener('push', event => {
  let data = { title: 'YatraPath', body: 'Something new awaits!', url: '/' };

  try {
    data = JSON.parse(event.data.text());
  } catch (_) {}

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body:               data.body,
      icon:               '/static/images/icons/icon-512.png',
      badge:              '/static/images/icons/icon-192.png',
      data:               { url: data.url },
      vibrate:            [200, 100, 200, 100, 200],
      requireInteraction: true,
      tag:                'yathrapath-' + Date.now(),
      renotify:           true,
      silent:             false,
      timestamp:          Date.now(),
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
