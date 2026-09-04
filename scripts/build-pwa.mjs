#!/usr/bin/env node
/**
 * `next build` dan keyin ishlaydi: out/ ichidagi statik saytga
 * manifest va service worker qo'shadi.
 *
 *  - manifest.webmanifest — ilova sifatida o'rnatish uchun
 *  - sw.js — offline ishlash: app shell precache, sahifalar runtime cache
 *
 * Versiya fayllar mazmunidan hisoblanadi, shuning uchun kontent o'zgarsa
 * brauzer yangi service worker'ni oladi va eski keshni tozalaydi.
 */
import { createHash } from "node:crypto";
import { readdir, readFile, writeFile, stat } from "node:fs/promises";
import { join, relative, sep } from "node:path";

const OUT = "out";
const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

async function walk(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...(await walk(full)));
    else out.push(full);
  }
  return out;
}

const files = (await walk(OUT))
  .map((f) => relative(OUT, f).split(sep).join("/"))
  .filter((f) => !["sw.js", "manifest.webmanifest"].includes(f))
  .sort();

// Versiya: barcha fayllar mazmunining birlashgan xesh'i
const hash = createHash("sha256");
for (const f of files) hash.update(f).update(await readFile(join(OUT, f)));
const VERSION = hash.digest("hex").slice(0, 12);

const url = (f) => `${BASE}/${f}`.replace(/\/index\.html$/, "/");

/** Shell: darhol kerak bo'ladigan hamma narsa. Dars sahifalari runtime'da keshlanadi. */
const precache = [
  ...files.filter((f) => f.startsWith("_next/") || f.endsWith(".png") || f.endsWith(".svg")),
  "index.html",
  "index.txt",
  "404.html",
  "darslar/index.html",
  "darslar/index.txt",
].filter((f, i, a) => files.includes(f) && a.indexOf(f) === i);

const manifest = {
  name: "System Design darsligi",
  short_name: "SD darslik",
  description:
    "Dasturchilar uchun tizim dizayni bo'yicha o'zbek tilidagi darslik — 17 ta case study.",
  lang: "uz",
  dir: "ltr",
  start_url: `${BASE}/`,
  scope: `${BASE}/`,
  display: "standalone",
  orientation: "portrait-primary",
  background_color: "#0b0d10",
  theme_color: "#0b0d10",
  categories: ["education", "productivity"],
  icons: [
    { src: `${BASE}/icon-192.png`, sizes: "192x192", type: "image/png", purpose: "any" },
    { src: `${BASE}/icon-512.png`, sizes: "512x512", type: "image/png", purpose: "any" },
    {
      src: `${BASE}/icon-maskable-512.png`,
      sizes: "512x512",
      type: "image/png",
      purpose: "maskable",
    },
  ],
  shortcuts: [
    { name: "Kurs rejasi", url: `${BASE}/darslar/`, description: "Barcha darslar ro'yxati" },
  ],
};

await writeFile(join(OUT, "manifest.webmanifest"), JSON.stringify(manifest, null, 2));

const sw = `/* Avtomatik generatsiya qilingan — scripts/build-pwa.mjs. Qo'lda tahrirlamang. */
const VERSION = ${JSON.stringify(VERSION)};
const BASE = ${JSON.stringify(BASE)};
const SHELL = ${JSON.stringify(precache.map(url))};
const SHELL_CACHE = "shell-" + VERSION;
const PAGE_CACHE = "pages-" + VERSION;

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(SHELL_CACHE);
      // Bittasi yiqilsa butun o'rnatish buzilmasin
      await Promise.all(
        SHELL.map((u) => cache.add(new Request(u, { cache: "reload" })).catch(() => {})),
      );
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keep = new Set([SHELL_CACHE, PAGE_CACHE]);
      for (const key of await caches.keys()) if (!keep.has(key)) await caches.delete(key);
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("message", (event) => {
  const data = event.data || {};
  if (data.type === "SKIP_WAITING") self.skipWaiting();
  if (data.type === "PRECACHE_URLS") event.waitUntil(precacheUrls(data.urls, event.source));
});

/** "Barcha darslarni yuklab olish" tugmasi uchun: progress bilan keshlash. */
async function precacheUrls(urls, client) {
  const cache = await caches.open(PAGE_CACHE);
  let done = 0;
  for (const u of urls) {
    try {
      const res = await fetch(u, { cache: "reload" });
      if (res.ok) await cache.put(u, res.clone());
    } catch {}
    done++;
    client && client.postMessage({ type: "PRECACHE_PROGRESS", done, total: urls.length });
  }
  client && client.postMessage({ type: "PRECACHE_DONE", total: urls.length });
}

const isHtml = (req) =>
  req.mode === "navigate" || (req.headers.get("accept") || "").includes("text/html");

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Sahifalar: avval tarmoq (yangi kontent), tushsa keshdan
  if (isHtml(req) || url.pathname.endsWith(".txt")) {
    event.respondWith(
      (async () => {
        try {
          const res = await fetch(req);
          if (res.ok) (await caches.open(PAGE_CACHE)).put(req, res.clone());
          return res;
        } catch {
          const cached = (await caches.match(req)) || (await caches.match(BASE + "/"));
          return cached || new Response("Oflayn", { status: 503 });
        }
      })(),
    );
    return;
  }

  // Statik resurslar (xeshlangan nomlar): avval kesh
  event.respondWith(
    (async () => {
      const cached = await caches.match(req);
      if (cached) return cached;
      try {
        const res = await fetch(req);
        if (res.ok && url.pathname.includes("/_next/"))
          (await caches.open(SHELL_CACHE)).put(req, res.clone());
        return res;
      } catch {
        return new Response("", { status: 504 });
      }
    })(),
  );
});
`;

await writeFile(join(OUT, "sw.js"), sw);

// --- SEO: kontent himoyalangan bo'lsa indekslash taqiqlanadi ---
const NOINDEX = /noindex:\s*true/.test(await readFile("lib/site.ts", "utf8"));
const SITE = "https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers";
const pages = files
  .filter((f) => f.endsWith("index.html"))
  .map((f) => `${SITE}/${f.replace(/index\.html$/, "")}`.replace(/([^:])\/\/+/g, "$1/"))
  .filter((u) => !u.includes("/404/"));

if (NOINDEX) {
  await writeFile(join(OUT, "robots.txt"), `User-agent: *\nDisallow: /\n`);
  console.log("robots.txt: indekslash TAQIQLANDI (site.ts -> protection.noindex)");
} else {
await writeFile(
  join(OUT, "sitemap.xml"),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    pages
      .map(
        (u) =>
          `  <url><loc>${u}</loc><changefreq>weekly</changefreq><priority>${u === SITE + "/" ? "1.0" : "0.8"}</priority></url>`,
      )
      .join("\n") +
    `\n</urlset>\n`,
);

await writeFile(
  join(OUT, "robots.txt"),
  `User-agent: *\nAllow: /\n\nSitemap: ${SITE}/sitemap.xml\n`,
);
}

const bytes = (await Promise.all(precache.map((f) => stat(join(OUT, f))))).reduce(
  (a, s) => a + s.size,
  0,
);
console.log(
  `PWA tayyor: versiya ${VERSION}, shell ${precache.length} fayl (${(bytes / 1024).toFixed(0)} KB), basePath "${BASE || "/"}"`,
);
