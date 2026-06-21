const CACHE_NAME = 'terafab-decision-twin-website-v1';
const BASE = '/terafab-decision-twin/website/';
const APP_SHELL = [
  BASE,
  `${BASE}index.html`,
  `${BASE}offline.html`,
  `${BASE}assets/fonts.css`,
  `${BASE}assets/style.css`,
  `${BASE}assets/app.js`,
  `${BASE}assets/icon.svg`,
  `${BASE}assets/social-card.svg`,
  `${BASE}manifest.webmanifest`
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).catch(() => null));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  event.respondWith(caches.match(request).then(cached => {
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
  }));
});
