// Service worker Soul of Home — приложение на телефоне и работа без сети.
// Страницы, стили, скрипты и шрифты кешируются при установке; картинки — по мере просмотра.
// При изменении файлов сайта увеличьте VERSION — старый кеш удалится сам.
const VERSION = 'v6';
const CORE = 'soh-core-' + VERSION;
const IMAGES = 'soh-img-' + VERSION;
const OFFLINE = 'offline.html';
const PRECACHE = [
  './', 'index.html', 'raboty.html', 'obuchenie.html', 'uroki.html', 'kompanii.html', 'o-nas.html', 'profile.html', OFFLINE,
  'styles.css', 'site.js', 'analytics-config.js', 'manifest.json',
  'fonts/manrope-cyrillic-wght-normal.woff2', 'fonts/manrope-cyrillic-ext-wght-normal.woff2',
  'fonts/manrope-latin-wght-normal.woff2', 'fonts/manrope-latin-ext-wght-normal.woff2',
  'fonts/fraunces-latin-opsz-normal.woff2', 'fonts/fraunces-latin-opsz-italic.woff2',
  'fonts/fraunces-latin-ext-opsz-normal.woff2', 'fonts/fraunces-latin-ext-opsz-italic.woff2',
  'favicon.ico', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'
];
const MAX_IMAGES = 60;

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CORE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('soh-') && k !== CORE && k !== IMAGES).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// сначала сеть (свежая версия), без сети — из кеша
async function networkFirst(req) {
  const cache = await caches.open(CORE);
  try {
    const res = await fetch(req);
    if (res && res.ok) cache.put(req, res.clone());
    return res;
  } catch (e) {
    const hit = await cache.match(req, {ignoreSearch: true});
    if (hit) return hit;
    if (req.mode === 'navigate') return cache.match(OFFLINE);
    throw e;
  }
}

// сразу из кеша, в фоне — обновление (стили, скрипты)
async function staleWhileRevalidate(req) {
  const cache = await caches.open(CORE);
  const hit = await cache.match(req);
  const update = fetch(req).then(res => { if (res && res.ok) cache.put(req, res.clone()); return res; }).catch(() => null);
  return hit || (await update) || Response.error();
}

// из кеша, иначе из сети с сохранением (шрифты, картинки)
async function cacheFirst(req, name, limit) {
  const cache = await caches.open(name);
  const hit = await cache.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res && res.ok) {
    cache.put(req, res.clone());
    if (limit) cache.keys().then(keys => { if (keys.length > limit) cache.delete(keys[0]); });
  }
  return res;
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;          // счётчики аналитики и Telegram — мимо кеша
  if (req.mode === 'navigate' || url.pathname.endsWith('.html')) { event.respondWith(networkFirst(req)); return; }
  if (/\.(css|js|json)$/.test(url.pathname)) { event.respondWith(staleWhileRevalidate(req)); return; }
  if (/\.woff2$/.test(url.pathname)) { event.respondWith(cacheFirst(req, CORE)); return; }
  if (/\.(jpe?g|png|webp|gif|svg|ico)$/.test(url.pathname)) { event.respondWith(cacheFirst(req, IMAGES, MAX_IMAGES)); return; }
});
