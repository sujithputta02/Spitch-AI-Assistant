const CACHE_NAME = 'spitch-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/landing.html',
  '/manifest.json',
  '/style.css',
  '/main.js',
  '/assets/img/spitch.ico',
  '/assets/img/spitch-192.png',
  '/assets/img/spitch-512.png'
];
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(urlsToCache);
    })
  );
});
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
}); 