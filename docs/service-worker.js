const CACHE_NAME = 'terafab-decision-twin-v1';
const BASE = '/terafab-decision-twin/';
const APP_SHELL = [
  BASE, BASE + 'index.html', BASE + 'model.html', BASE + 'scenarios.html', BASE + 'policy.html', BASE + 'evidence.html', BASE + 'researchers.html', BASE + 'getting-started.html', BASE + 'offline.html', BASE + '404.html', BASE + 'llms.txt', BASE + 'robots.txt', BASE + 'sitemap.xml', BASE + 'manifest.webmanifest', BASE + 'assets/style.css', BASE + 'assets/app.js', BASE + 'assets/icon.svg', BASE + 'assets/icon-192.png', BASE + 'assets/icon-512.png', BASE + 'assets/maskable-icon-512.png', BASE + 'assets/social-card.svg'
];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (!url.pathname.startsWith(BASE)) return;
  event.respondWith(caches.match(request).then(cached => cached || fetch(request).then(response => {
    const copy = response.clone();
    if (response.ok && !url.pathname.includes('/sources/') && !url.pathname.includes('restricted')) { caches.open(CACHE_NAME).then(cache => cache.put(request, copy)); }
    return response;
  }).catch(() => caches.match(BASE + 'offline.html'))));
});
