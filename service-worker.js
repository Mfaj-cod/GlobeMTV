<<<<<<< HEAD
// Listen for fetch events
self.addEventListener('fetch', event => {
    const req = event.request;
    const url = new URL(req.url);
    const RUNTIME_CACHE = 'runtime-cache';

    // API requests: network-first with cache fallback
    if (url.pathname.startsWith('/api/') || url.pathname.includes('/graphql')) {
        event.respondWith(
            fetch(req)
                .then(resp => {
                    const copy = resp.clone();
                    caches.open(RUNTIME_CACHE).then(cache => cache.put(req, copy));
                    return resp;
                })
                .catch(() => caches.match(req))
        );
        return;
    }

    // Static assets: cache-first, update in background
    event.respondWith(
        caches.match(req).then(cached => {
            if (cached) {
                // Refresh the cache in background
                fetch(req).then(resp => {
                    if (resp && resp.status === 200) {
                        caches.open(RUNTIME_CACHE).then(cache => cache.put(req, resp));
                    }
                }).catch(() => {});
                return cached;
            }
            return fetch(req)
                .then(resp => {
                    // Only cache successful responses
                    if (resp && resp.status === 200) {
                        const copy = resp.clone();
                        caches.open(RUNTIME_CACHE).then(cache => {
                            cache.put(req, copy);
                            // optional: keep runtime cache size reasonable
                            trimCache(RUNTIME_CACHE, 200);
                        });
                    }
                    return resp;
                })
                .catch(() => {
                    // image fallback or generic fallback
                    if (req.destination === 'image') {
                        return caches.match('/icons/icon-192x192.png');
                    }
                    return caches.match('/offline.html');
                });
        })
    );
});



// Optional: receive messages from the page (skipWaiting / update)
self.addEventListener('message', event => {
    if (!event.data) return;
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});



// Helper function to trim cache size
async function trimCache(cacheName, maxItems) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    if (keys.length > maxItems) {
        await cache.delete(keys[0]);
        trimCache(cacheName, maxItems);
    }
=======
// service-worker.js

// Listen for fetch events
self.addEventListener('fetch', event => {
    const req = event.request;
    const url = new URL(req.url);
    const RUNTIME_CACHE = 'runtime-cache';

    // API requests: network-first with cache fallback
    if (url.pathname.startsWith('/api/') || url.pathname.includes('/graphql')) {
        event.respondWith(
            fetch(req)
                .then(resp => {
                    const copy = resp.clone();
                    caches.open(RUNTIME_CACHE).then(cache => cache.put(req, copy));
                    return resp;
                })
                .catch(() => caches.match(req))
        );
        return;
    }

    // Static assets: cache-first, update in background
    event.respondWith(
        caches.match(req).then(cached => {
            if (cached) {
                // Refresh the cache in background
                fetch(req).then(resp => {
                    if (resp && resp.status === 200) {
                        caches.open(RUNTIME_CACHE).then(cache => cache.put(req, resp));
                    }
                }).catch(() => {});
                return cached;
            }
            return fetch(req)
                .then(resp => {
                    // Only cache successful responses
                    if (resp && resp.status === 200) {
                        const copy = resp.clone();
                        caches.open(RUNTIME_CACHE).then(cache => {
                            cache.put(req, copy);
                            // optional: keep runtime cache size reasonable
                            trimCache(RUNTIME_CACHE, 200);
                        });
                    }
                    return resp;
                })
                .catch(() => {
                    // image fallback or generic fallback
                    if (req.destination === 'image') {
                        return caches.match('/icons/icon-192x192.png');
                    }
                    return caches.match('/offline.html');
                });
        })
    );
});



// Optional: receive messages from the page (skipWaiting / update)
self.addEventListener('message', event => {
    if (!event.data) return;
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});



// Helper function to trim cache size
async function trimCache(cacheName, maxItems) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    if (keys.length > maxItems) {
        await cache.delete(keys[0]);
        trimCache(cacheName, maxItems);
    }
>>>>>>> daf33e7acfb1ac2aa13c3c54a165c5ce615c80e9
}