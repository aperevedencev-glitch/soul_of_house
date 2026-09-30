// Service worker Soul of Home: при отсутствии сети показывает страницу «Нет соединения»
const CACHE = 'soh-offline-v1';
const OFFLINE = 'offline.html';
const PRECACHE = [OFFLINE, 'favicon.ico', 'fonts/manrope-cyrillic-wght-normal.woff2', 'fonts/manrope-latin-wght-normal.woff2', 'fonts/fraunces-latin-opsz-normal.woff2'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  // переходы по страницам: сначала сеть, без сети — заглушка
  if (req.mode === 'navigate') {
    event.respondWith(fetch(req).catch(() => caches.match(OFFLINE)));
    return;
  }
  // шрифты и иконка для заглушки — из кэша, если сети нет
  const url = new URL(req.url);
  if (url.origin === location.origin && PRECACHE.some(p => url.pathname.endsWith('/' + p))) {
    event.respondWith(caches.match(req).then(r => r || fetch(req)));
  }
});
