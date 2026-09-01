# System Design darsligi — 17 ta case study

Dasturchilar uchun tizim dizayni bo‘yicha o‘zbek tilidagi darslik. Har bir dars bitta
mahsulotni **noldan hozirgi arxitekturasigacha** ochib beradi, va har bir dars sahifasi
o‘sha mahsulot interfeysidan ilhomlangan dizaynda ko‘rsatiladi.

## Ishga tushirish

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # statik sayt -> out/
```

## Stack

| Qatlam | Tanlov |
| --- | --- |
| Framework | Next.js 15 (App Router), `output: "export"` |
| Kontent | MDX (`app/darslar/<slug>/page.mdx`) |
| Styling | Tailwind v4 + CSS o‘zgaruvchilaridagi skin tokenlari |
| Deploy | GitHub Actions → GitHub Pages |

## Loyiha tuzilishi

```
app/
  page.tsx                    bosh sahifa (darslar to'plami)
  darslar/page.tsx            kurs rejasi
  darslar/chatgpt/
    page.mdx                  dars matni
    theme.css                 shu darsning skin tokenlari
    layout.tsx                skin'ni ulaydi
components/
  lesson/                     barcha darslar uchun umumiy bloklar
  skins/                      har bir mahsulotning UI chrome'i
lib/lessons.ts                darslar reyestri (tartib, status, meta)
scripts/yangi-dars.mjs        yangi dars skeletini yaratadi
```

## Skin tizimi

Butun sayt 12 ta CSS o‘zgaruvchisiga tayanadi: `--skin-bg`, `--skin-surface`,
`--skin-surface-2`, `--skin-border`, `--skin-text`, `--skin-muted`, `--skin-accent`,
`--skin-accent-text`, `--skin-ring`, `--skin-radius`, `--skin-font`, `--skin-mono`.

Dars papkasidagi `theme.css` shu qiymatlarni qayta belgilaydi, `skins/<Nom>Shell.tsx` esa
chrome beradi (Slack uchun kanallar sidebar‘i, Spotify uchun player paneli va h.k.).
`components/lesson/*` ichidagi hech bir komponent qat‘iy rang ishlatmaydi — shuning uchun
bir xil kontent 17 xil UI ichida ham tabiiy ko‘rinadi.

> **Huquqiy eslatma.** Rasmiy logotip, shrift va brend materiallari repozitoriyga
> qo‘shilmaydi. Skinlar — o‘xshash palitra, tartib va o‘zimiz chizgan soddalashtirilgan
> belgilar. Har bir dars sahifasi pastida shu haqda izoh chiqadi.

## Dars chuqurligi

Namuna dars — `app/darslar/chatgpt/page.mdx`: 12 000+ so‘z, 21 bo‘lim, 19 ta hisob-kitob
bloki, 25 ta intervyu savoli, 4 daraja amaliyot. Har bir muhandislik qarori raqamdan kelib
chiqadi (roofline, KV cache byudjeti, navbat nazariyasi, sig‘im rejalashtirish, birlik
iqtisodi). Qolgan darslar ham shu me’yorga qarab yoziladi — batafsili
`docs/DARS-SHABLONI.md` da.

## Yangi dars qo‘shish

1. `lib/lessons.ts` ga yozuv qo‘shing (order, slug, title, summary, accent, level, topics).
2. `node scripts/yangi-dars.mjs <slug>` — skelet yaratiladi.
3. `page.mdx` ni 8 bosqichli shablon bo‘yicha to‘ldiring (`docs/DARS-SHABLONI.md`).
4. `theme.css` va `<Nom>Shell.tsx` ni mahsulot UI‘siga moslang.
5. Statusni `tayyor` ga o‘zgartiring, PR oching.

## Offline rejim va ilova sifatida o‘rnatish (PWA)

Sayt **progressive web app**: internetsiz ishlaydi va telefon yoki kompyuterga ilova
sifatida o‘rnatiladi.

- `scripts/build-pwa.mjs` har bir `npm run build` dan keyin `out/` ichiga
  `manifest.webmanifest` va `sw.js` yozadi. Service worker versiyasi fayllar mazmunidan
  hisoblanadi, ya’ni kontent o‘zgarsa foydalanuvchi yangilanishni ko‘radi
- **App shell** (JS, CSS, ikonkalar, bosh sahifa) o‘rnatishda darhol keshlanadi
- **Dars sahifalari** ochilganda keshlanadi, yoki o‘ng pastdagi tugma orqali
  “Barcha darslarni yuklab olish” bilan oldindan saqlanadi
- Sahifalar uchun *network-first* (yangi kontent ustuvor), statik resurslar uchun
  *cache-first* strategiyasi
- Yangi versiya chiqqanda “Yangilanish bor” tugmasi chiqadi; bosilganda eski keshlar
  tozalanadi

Ikonkalar `public/` da commit qilingan. `icon.svg` o‘zgarsa qayta yaratish:

```bash
npx --yes playwright@latest install chromium
node scripts/make-icons.mjs
```

## Deploy

Repo sozlamalarida **Settings → Pages → Source: GitHub Actions** tanlangan bo‘lishi shart.
“Deploy from a branch” tanlansa, GitHub build qilinmagan repo fayllarini (README.md) chiqaradi —
sayt o‘rniga shu ko‘rinadi.

Source to‘g‘ri tanlangach, `main` yoki `claude/**` branchiga har push saytni yangilaydi.
Manzil: `https://<foydalanuvchi>.github.io/<repo-nomi>/`.
