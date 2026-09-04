# Telegram kanal uchun tayyor postlar

Hammasi nusxa olib joylash uchun tayyor. Telegram markdown belgilarini avtomatik
o'girmaydi, shuning uchun matnlar **oddiy matn** ko'rinishida yozilgan — qalin qilish
kerak bo'lgan joylar izohda ko'rsatilgan (matnni belgilab Ctrl+B / Cmd+B).

Havola: `https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/`

Havolani xabar oxiriga qo'ysangiz, Telegram avtomatik ravishda chiroyli kartochka
(rasm + sarlavha) chiqaradi — alohida rasm yuklash shart emas.

---

## 1. ASOSIY E'LON (birinchi post)

> Qalin qilish: birinchi qator va "har bir qaror hisob-kitobdan chiqadi"

```
🇺🇿 System design bo'yicha o'zbekcha darslik — bepul

Tizim dizayni bo'yicha material izlab ko'rgan bo'lsangiz bilasiz: deyarli hammasi
ingliz tilida, ko'pi esa yuzaki — quti-strelka diagrammasi chiziladi, ichkarida
nima bo'layotgani tushuntirilmaydi.

Shuning uchun o'zim yoza boshladim.

Har bir dars bitta mahsulotni noldan hozirgi arxitekturasigacha ochib beradi:

• Mexanizmning o'zidan boshlanadi — diagrammadan oldin sabab
• Eng sodda yechim, keyin u qayerda sindi — aniq raqam bilan
• Har bir evolyutsiya qadami: nima yutdik va nimani yo'qotdik
• 20+ intervyu savoli, javoblari yopiq — avval o'zingiz javob berasiz
• Amaliyot topshiriqlari, tekshiruv mezoni bilan

Asosiy farqi: har bir qaror hisob-kitobdan chiqadi.

"Batching kerak" emas — balki: arifmetik intensivlik 1, ridge point 295, demak
GPU'ning 0.3% i ishlatilyapti. Har bir hisobni kalkulyatorda takrorlash mumkin.

Hozir 4 ta dars tayyor:

01 — ChatGPT qanday ishlaydi (12 200 so'z)
02 — URL qisqartiruvchi qanday ishlaydi (11 600 so'z)
03 — Redis: 12 ta asosiy stsenariy (11 100 so'z)
04 — Twitter tasmasi qanday ishlaydi (10 200 so'z)

Yana 13 tasi rejada: Kafka, Amazon S3, YouTube, Google Docs, Uber ETA, WhatsApp,
fond birjasi va boshqalar.

📱 Internetsiz ishlaydi — telefonga ilova sifatida o'rnatsa bo'ladi
🎨 Har bir dars o'sha mahsulotning interfeysi uslubida

https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/
```

---

## 2. QISQA VARIANT (forward qilish uchun)

```
System design bo'yicha o'zbekcha darslik yozyapman — bepul.

Har bir dars bitta mahsulotni noldan bugungi arxitekturasigacha ochadi va har bir
qaror raqam bilan asoslanadi: roofline, KV cache byudjeti, navbat nazariyasi,
birlik iqtisodi.

4 ta dars tayyor (ChatGPT, URL qisqartiruvchi, Redis, Twitter tasmasi), 13 tasi
rejada. Internetsiz ham o'qish mumkin.

https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/
```

---

## 3. DARS POSTLARI (kuniga bittadan joylash uchun)

Har bir post bitta kuchli raqam bilan boshlanadi — bu eng yaxshi ishlaydigan naqsh.
Dars havolasini qo'ysangiz, Telegram o'sha darsning o'z kartochkasini ko'rsatadi.

### 3.1 — ChatGPT

```
Savol: nega bitta so'rovga xizmat qilish GPU'ning 99% ini isrof qiladi?

Javob roofline modelida. H100 ning ridge point'i ~295 FLOP/bayt. Decode
bosqichida arifmetik intensivlik batch hajmiga teng — ya'ni batch=1 da atigi
1 FLOP/bayt.

295 kerak, 1 bor. GPU hisob quvvatining 0.3% i ishlatiladi, qolgani xotirani
kutadi.

Mana shu bitta son continuous batching, PagedAttention va prefix caching kabi
butun bir texnologiyalar oilasini tug'dirgan.

"ChatGPT qanday ishlaydi" darsi — tokenizatsiyadan inference iqtisodigacha,
12 200 so'z, 19 ta hisob-kitob bloki, 25 ta intervyu savoli:

https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/darslar/chatgpt/
```

### 3.2 — URL qisqartiruvchi

```
"URL qisqartiruvchi yozish oson" — intervyudagi eng aldamchi savol.

Bir nechta savol beraman:

• Kalit uzunligini nima belgilaydi? (base62 da 7 belgi = 3.5 trillion)
• Tasodifiy kalit qachon to'qnashadi? (6 milliard havolada har 587 yozuvdan biri)
• 301 va 302 dan qaysi biri? (301 analitikangizning 80% ini o'ldiradi va
  havolani abadiy qotirib qo'yadi)
• Bitta viral havola tizimni qanday yiqitadi? (cache stampede: TTL tugagan
  lahzada 50 000 so'rov bazaga yuguradi)

Bularning har biriga javob — hisob-kitob bilan.

11 600 so'z, 19 ta hisob bloki:

https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/darslar/url-shortener/
```

### 3.3 — Redis

```
Redis'da 10 million oddiy kalit qancha xotira yeydi?

Hisoblaymiz: kalit "user:12345678" (13 bayt), qiymat 50 bayt.

dictEntry 24 + kalit SDS 32 + robj 16 + qiymat SDS 72 + TTL yozuvi 24 = ~168 bayt

10 million x 168 = 1.68 GB

Foydali ma'lumot esa atigi 63 bayt — ya'ni xotiraning 63% i ustama xarajat.

Shuning uchun kichik obyektlarni alohida kalitlarda emas, hash ichida saqlash
3-5 barobar tejaydi.

"Redis: 12 ta asosiy stsenariy" darsi — event loop va xotira modelidan klasterga
qadar. Kesh, rate limiter, leaderboard, navbat, taqsimlangan lock va yana 7 tasi,
har birida eng ko'p qilinadigan xato bilan:

https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/darslar/redis/
```

### 3.4 — Twitter tasmasi

```
100 million obunachisi bor akkaunt bitta post yozsa nima bo'ladi?

Agar har bir obunachining tasmasiga nusxa qo'yadigan bo'lsak — bu 100 million
yozuv. Klaster sig'imi sekundiga 2 million bo'lsa, bitta post butun tizimni
50 soniyaga band qiladi.

Va bu bitta post emas: 1000 ta yirik akkaunt qolgan 500 million foydalanuvchidan
KO'PROQ yuk yaratadi.

Shuning uchun Twitter'da ikkita butunlay boshqa mexanizm bir vaqtda ishlaydi —
oddiy akkauntlar uchun bittasi, mashhurlar uchun ikkinchisi.

"Twitter tasmasi qanday ishlaydi" darsi — fan-out on write va on read, gibrid
yechim, Snowflake ID, tombstone, reyting narxi:

https://dinmuhammad05.github.io/15-case-studiesfo-software-engineers/darslar/twitter/
```

---

## 4. SO'ROVNOMA (poll) — engagement uchun

Telegram'da "So'rovnoma" yaratib, quyidagi variantlarni qo'ying:

**Savol:** Keyingi darsni qaysi mavzuda yozay?

- Apache Kafka (commit log, partition, exactly-once)
- Amazon S3 (erasure coding, 11 ta to'qqizlik)
- YouTube (transkodlash, CDN, adaptiv bitreyt)
- Google Docs (OT va CRDT)
- Uber ETA (graf, geoindeks, real-time ML)

---

## 5. TIZERLAR (qisqa qiziqtiruvchi postlar)

Bularni darslar orasida, alohida joylash mumkin:

```
Bilasizmi: o'zbekcha matn ChatGPT'ga inglizchadan 2.5-3 barobar qimmatga tushadi.

Sabab — tokenizatsiya. Inglizchada ~4 belgi bir token, o'zbekchada bir so'z
3-5 tokenga bo'linadi: kitob|lar|imiz|ga

Ya'ni 100 000 tokenlik kontekst oynasiga inglizcha 77 000 so'z sig'sa,
o'zbekcha atigi 28 000 so'z sig'adi.

Mahalliy AI mahsulot qurayotganlar buni byudjetga kiritishi kerak.
```

```
Web-sahifada skrinshotni to'xtatib bo'lmaydimi?

Yo'q. Skrinshot operatsion tizim darajasida olinadi, brauzer unga aralasha
olmaydi. Netflix'dagi qora ekran — DRM va u faqat video oqimi uchun ishlaydi.

Bu — kontentni himoyalash haqidagi eng keng tarqalgan noto'g'ri tasavvur.
```

---

## 6. JOYLASH BO'YICHA MASLAHATLAR

| Nima | Tavsiya |
| --- | --- |
| Birinchi post | Asosiy e'lon (1-bo'lim), kanalga pin qilib qo'ying |
| Keyingi postlar | Kuniga yoki ikki kunda bitta dars posti (3-bo'lim) |
| Vaqt | Ish kunlari 09:00-10:00 yoki 20:00-22:00 |
| So'rovnoma | Dars postlaridan keyin, 2-3 kun o'tib |
| Havola | Har doim xabar oxirida — Telegram kartochkani o'sha yerdan oladi |
| Rasm | Alohida yuklash shart emas, kartochka avtomatik chiqadi |

**Kartochka eskirib qolsa:** Telegram havola preview'ini keshlaydi. Sayt yangilangandan
keyin eski rasm chiqsa, havolaga `?v=2` qo'shib bir marta yuboring — kesh yangilanadi.

**Eslatma:** hozir saytda `noindex` yoqilgan, ya'ni u Google'da topilmaydi. Kanal orqali
tarqalish uchun bu muammo emas, lekin qidiruvdan odam kelishini xohlasangiz, uni
`lib/site.ts` da o'chirish kerak.
