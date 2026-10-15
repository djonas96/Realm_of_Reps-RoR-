// Service Worker: speichert die App im Cache, damit sie auch ohne Internet startet.
// Bei Internet wird immer zuerst die neueste Version geladen ("Netzwerk zuerst").
const CACHE = "ror-mobile-v1";
const DATEIEN = ["./", "./index.html", "./icon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(DATEIEN)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(namen =>
    Promise.all(namen.filter(n => n !== CACHE).map(n => caches.delete(n)))));
  self.clients.claim();
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return; // Wetter-API nicht cachen
  e.respondWith(
    fetch(e.request)
      .then(antwort => {
        const kopie = antwort.clone();
        caches.open(CACHE).then(c => c.put(e.request, kopie));
        return antwort;
      })
      .catch(() => caches.match(e.request).then(t => t || caches.match("./index.html")))
  );
});
