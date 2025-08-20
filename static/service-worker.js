// service-worker.js

const CACHE_NAME = 'sentinelvision-cache-v1';
const urlsToCache = [
  '/',
  '/login',
  '/dashboard',
  '/static/css/base.css',
  '/static/css/login.css',
  '/static/css/dashboard.css',
  '/static/css/gallery.css',
  '/static/css/register.css',
  '/static/css/detail_gallery.css',
  '/static/css/manage_users.css',
  '/static/css/my_account.css',
  '/static/css/reset_password.css',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});