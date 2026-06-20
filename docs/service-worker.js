const CACHE='terafab-exec-site-v2';
const BASE='/terafab-decision-twin/';
const ASSETS=['','index.html','model.html','scenarios.html','policy.html','evidence.html','researchers.html','getting-started.html','offline.html','404.html','llms.txt','robots.txt','sitemap.xml','manifest.webmanifest','assets/style.css','assets/app.js','assets/icon.svg','assets/icon-192.png','assets/icon-512.png','assets/maskable-icon-512.png','assets/social-card.svg'].map(p=>BASE+p);
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return; const url=new URL(e.request.url); if(!url.pathname.startsWith(BASE)) return; e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{const copy=r.clone(); caches.open(CACHE).then(c=>c.put(e.request,copy)); return r}).catch(()=>caches.match(BASE+'offline.html'))))});
