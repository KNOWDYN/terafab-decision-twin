const CACHE_NAME = 'terafab-decision-twin-minimal-v1';
const BASE = '/terafab-decision-twin/';
const APP_SHELL = [
  BASE,
  `${BASE}index.html`,
  `${BASE}offline.html`,
  `${BASE}404.html`,
  `${BASE}assets/style.css`,
  `${BASE}assets/app.js`,
  `${BASE}assets/icon.svg`,
  `${BASE}assets/icon-192.png`,
  `${BASE}assets/icon-512.png`,
  `${BASE}assets/maskable-icon-512.png`,
  `${BASE}assets/social-card.svg`,
  `${BASE}manifest.webmanifest`,
  `${BASE}llms.txt`,
  `${BASE}robots.txt`,
  `${BASE}sitemap.xml`
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).catch(() => null));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(response => {
        const copy = response.clone();
        if (response.ok && new URL(request.url).origin === self.location.origin) {
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy)).catch(() => null);
        }
        return response;
      }).catch(() => {
        if (request.mode === 'navigate') return caches.match(`${BASE}offline.html`);
        return new Response('', { status: 503, statusText: 'Offline' });
      });
    })
  );
});
