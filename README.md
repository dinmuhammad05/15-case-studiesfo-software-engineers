<div align="center">

<img src="public/icon-192.png" width="88" alt="" />

# System Design darsligi

**Dasturchilar uchun tizim dizayni bo‘yicha o‘zbek tilidagi darslik.**
Har bir dars bitta mahsulotni noldan hozirgi arxitekturasigacha ochib beradi —
va har bir qaror hisob-kitob bilan asoslanadi.

[**→ Saytni ochish**](https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/)

![Next.js](https://img.shields.io/badge/Next.js-15-000?logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white)
![PWA](https://img.shields.io/badge/PWA-offline%20ishlaydi-5A0FC8)
![Kod: MIT](https://img.shields.io/badge/kod-MIT-green)
![Matn: CC BY--NC 4.0](https://img.shields.io/badge/matn-CC%20BY--NC%204.0-lightgrey)

</div>

<p align="center">
  <img src="docs/screenshots/home.png" width="880" alt="Bosh sahifa" />
</p>

---

## Nima bu?

Tizim dizayni haqidagi ko‘p material ikkita xatodan birini qiladi: yo faqat quti-strelka
diagrammasini chizadi va ichkarida nima bo‘layotganini tushuntirmaydi, yo aksincha —
nazariyaga botib, uni real mahsulotga bog‘lamaydi.

Bu darslikda har bir mavzu **bir xil yo‘ldan** boradi:

| Bosqich | Nima beradi |
| --- | --- |
| **Nol nuqta** | Mexanizmning o‘zi: token, HTTP redirect, event loop. Diagrammadan oldin — sabab |
| **v0** | Eng sodda ishlaydigan yechim — “yomon” emas, shunchaki kichik |
| **Nima sindi** | Aniq raqam bilan: `500 token × 42 ms = 21 soniya` |
| **Evolyutsiya** | 12–14 qadam, har birida **nima yutdik va nimani yo‘qotdik** |
| **Bugungi arxitektura** | To‘liq diagramma va so‘rovning kechikish byudjeti |
| **Ishonchlilik** | Nosozliklar taksonomiyasi va degradatsiya tartibi |
| **Iqtisod** | Bitta operatsiya necha tsentga tushadi |
| **Intervyu** | 20+ savol, javoblari yopiq — avval o‘zingiz javob berasiz |
| **Amaliyot** | 3–4 daraja topshiriq va **tekshiruv mezoni** |

Har bir darsda ~19 ta **hisob-kitob bloki** bor: farazlar → arifmetika → xulosa. Ularni
kalkulyatorda takrorlash mumkin.

## Darslar

| № | Dars | Holat | Hajm | Nimani o‘rgatadi |
| --- | --- | --- | --- | --- |
| 01 | [ChatGPT qanday ishlaydi](https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/darslar/chatgpt/) | ✅ Tayyor | 12 200 so‘z | Tokenizatsiya, attention, KV cache, continuous batching, roofline, inference iqtisodi |
| 02 | [URL qisqartiruvchi](https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/darslar/url-shortener/) | ✅ Tayyor | 11 600 so‘z | Base62, tug‘ilgan kun paradoksi, cache stampede, hot key, Bloom filtri, ochiq redirect |
| 03 | [Redis: 12 ta stsenariy](https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/darslar/redis/) | ✅ Tayyor | 11 100 so‘z | Event loop, xotira modeli, TTL va eviction, fork/COW, ZSET, Streams, klaster |
| 04 | Twitter tasmasi | ⏳ Rejada | | Fan-out on write vs read, mashhur akkauntlar muammosi |
| 05 | Reddit | ⏳ Rejada | | Ovoz berish, kommentariya daraxti, “hot” reytingi |
| 06 | Slack | ⏳ Rejada | | WebSocket, presence, kanal tarixi |
| 07 | WhatsApp | ⏳ Rejada | | E2E shifrlash, yetkazish kafolati, oflayn navbat |
| 08 | YouTube | ⏳ Rejada | | Transkodlash, CDN, adaptiv bitreyt |
| 09 | Spotify | ⏳ Rejada | | Audio yetkazish, tavsiya tizimi |
| 10 | Google Docs | ⏳ Rejada | | OT va CRDT tanlovi |
| 11 | Airbnb | ⏳ Rejada | | Geo qidiruv, bron, ikki marta band bo‘lmaslik |
| 12 | Uber ETA | ⏳ Rejada | | Yo‘l grafi, H3 geoindeks, real-time ML |
| 13 | Amazon S3 | ⏳ Rejada | | Erasure coding, 11 ta to‘qqizlik ishonchlilik |
| 14 | Apache Kafka | ⏳ Rejada | | Commit log, partition, ISR, exactly-once |
| 15 | Fond birjasi | ⏳ Rejada | | Order book, matching engine, past kechikish |
| 16 | Bluesky | ⏳ Rejada | | AT Protocol, federatsiya, firehose |
| 17 | Meta Serverless | ⏳ Rejada | | XFaaS, sovuq start, rejalashtirish |

## Har bir dars o‘z UI‘sida

Dars sahifasining dizayni o‘sha mahsulot interfeysidan ilhomlangan — bu shunchaki bezak
emas, mavzuga kirishishga yordam beradi.

<p align="center">
  <img src="docs/screenshots/lesson-chatgpt.png" width="440" alt="ChatGPT darsi" />
  <img src="docs/screenshots/lesson-url.png" width="440" alt="URL qisqartiruvchi darsi" />
</p>
<p align="center">
  <img src="docs/screenshots/lesson-redis.png" width="880" alt="Redis darsi" />
</p>

> **Huquqiy eslatma.** Rasmiy logotip, shrift va brend materiallari ishlatilmagan —
> faqat o‘xshash palitra, tartib va o‘zimiz chizgan soddalashtirilgan belgilar. Har bir
> dars sahifasi pastida shu haqda izoh bor. Barcha tovar belgilari o‘z egalariga tegishli.

## Imkoniyatlar

- 📱 **Offline ishlaydi** — service worker barcha darslarni keshlaydi, internetsiz o‘qish mumkin
- 📲 **Ilova sifatida o‘rnatiladi** (PWA) — telefon yoki kompyuterga
- 🎨 **Har dars o‘z skinida** — 12 ta CSS tokeni ustiga qurilgan tizim
- 🧮 **Hisob-kitob bloklari** — har bir arxitektura qarori raqamdan chiqadi
- 🧭 **Avtomatik mundarija** — skroll bo‘yicha joriy bo‘lim ajratiladi
- ⚡️ **To‘liq statik** — server yo‘q, GitHub Pages‘da bepul turadi

## Ishga tushirish

```bash
git clone https://github.com/dinmuhammad05/15-case-studiesfo-software-engineers.git
cd 15-case-studiesfo-software-engineers
npm install
npm run dev          # http://localhost:3000
```

```bash
npm run build        # statik sayt -> out/ (+ manifest, service worker, sitemap)
npm run typecheck
```

## Loyiha tuzilishi

```
app/
  page.tsx                    bosh sahifa
  darslar/page.tsx            kurs rejasi
  darslar/<slug>/
    page.mdx                  dars matni
    theme.css                 shu darsning skin tokenlari
    layout.tsx                skinni ulaydi + OG metadata
components/
  lesson/                     barcha darslar uchun umumiy bloklar
  skins/                      har bir mahsulotning UI chrome'i
  pwa/                        offline rejim boshqaruvi
lib/
  lessons.ts                  darslar reyestri
  site.ts                     muallif, havolalar, litsenziya
scripts/
  yangi-dars.mjs              yangi dars skeletini yaratadi
  build-pwa.mjs               manifest, service worker, sitemap
  make-og.mjs / make-icons.mjs  ulashish rasmlari va ikonkalar
docs/DARS-SHABLONI.md         dars yozish qoidalari va hajm mezoni
```

## Yangi dars qo‘shish

1. `lib/lessons.ts` ga yozuv qo‘shing
2. `node scripts/yangi-dars.mjs <slug>` — skelet yaratiladi
3. `page.mdx` ni [`docs/DARS-SHABLONI.md`](docs/DARS-SHABLONI.md) bo‘yicha to‘ldiring
4. `theme.css` va `<Nom>Shell.tsx` ni mahsulot UI‘siga moslang
5. Statusni `tayyor` ga o‘zgartiring va PR oching

Chuqurlik mezoni: ~10 000+ so‘z, 15+ hisob bloki, 20+ intervyu savoli. Eng muhim qoida —
**har bir muhandislik qarori raqamdan kelib chiqsin**: “batching kerak” emas, balki
“arifmetik intensivlik 1, ridge point 295, demak GPU‘ning 0.3% i ishlatilyapti”.

## Hissa qo‘shish

Xato topsangiz, aniqlik kiritmoqchi bo‘lsangiz yoki yangi dars yozmoqchi bo‘lsangiz —
[issue oching](https://github.com/dinmuhammad05/15-case-studiesfo-software-engineers/issues)
yoki PR yuboring. Ayniqsa qadrlanadi:

- Texnik aniqlik xatolari va eskirgan raqamlar
- Til va uslub tuzatishlari
- Yangi darslar (avval issue orqali kelishib olamiz)

## Litsenziya

| Nima | Litsenziya |
| --- | --- |
| Manba kodi | [MIT](LICENSE) |
| Dars matnlari va rasmlar | [CC BY-NC 4.0](LICENSE-CONTENT) — nom ko‘rsatilsa, notijorat maqsadda erkin |

## Muallif

**[@dinmuhammad05](https://github.com/dinmuhammad05)** · Telegram:
[@dinMuhammad05](https://t.me/dinMuhammad05)

Loyiha foydali bo‘lsa — ⭐️ qo‘yib ketsangiz, boshqalar ham topadi.
