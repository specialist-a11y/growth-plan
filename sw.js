/* 1GAMMA MB service worker.
   The app shell is cached so the tracker opens instantly and keeps working
   with no signal — a child ticking off a morning routine on the bus should
   not need a connection. Data still lives in localStorage and syncs when
   there is a network again. */
const VERSION = 'v1';
const SHELL = 'gt-shell-' + VERSION;
const MEDIA = 'gt-media-' + VERSION;

const SHELL_FILES = [
  './Growth_Tracker_Pro.html',
  './manifest.webmanifest',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './assets/icons/apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== SHELL && k !== MEDIA).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // never cache Supabase or anything else off-site: stale account data is worse than none
  if (url.origin !== self.location.origin) return;

  // artwork barely changes and there is a lot of it: serve from the cache first
  if (/\/assets\/.*\.(webp|png|jpg|jpeg|svg|ico)$/i.test(url.pathname)) {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        const copy = res.clone();
        caches.open(MEDIA).then(c => c.put(req, copy));
        return res;
      }).catch(() => hit))
    );
    return;
  }

  // the page itself: fresh when there is a network, cached when there is not
  e.respondWith(
    fetch(req)
      .then(res => {
        const copy = res.clone();
        caches.open(SHELL).then(c => c.put(req, copy));
        return res;
      })
      .catch(() => caches.match(req).then(hit => hit || caches.match('./Growth_Tracker_Pro.html')))
  );
});
