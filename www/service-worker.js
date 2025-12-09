const CACHE_NAME = 'spitch-cache-v6';
const urlsToCache = [
  '/',
  '/index.html',
  '/landing.html',
  '/manifest.json',
  '/style.css',
  '/assets/img/spitch.ico',
  '/assets/img/spitch-192.png',
  '/assets/img/spitch-512.png'
];
self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(urlsToCache);
    })
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (cacheNames) {
      return Promise.all(
        cacheNames.map(function (cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

self.addEventListener('fetch', function (event) {
  // Network-first strategy for JS files to always get latest code
  if (event.request.url.endsWith('.js')) {
    event.respondWith(
      fetch(event.request).catch(function () {
        return caches.match(event.request);
      })
    );
  } else {
    // Cache-first for other resources
    event.respondWith(
      caches.match(event.request).then(function (response) {
        return response || fetch(event.request);
      })
    );
  }
}); 