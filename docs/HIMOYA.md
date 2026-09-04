# Kontentni himoyalash: nima ishlaydi, nima ishlamaydi

Bu hujjat kursni pullik qilish rejasi bo‘lganda qanday qarorlar kerakligini tushuntiradi.
Asosiy xulosa boshida: **statik saytda kontentni himoyalab bo‘lmaydi.**

## Nima uchun

Brauzer sahifani ko‘rsatishi uchun butun matn allaqachon foydalanuvchi qurilmasiga
yuborilgan bo‘ladi. Undan keyin qo‘yilgan har qanday to‘siq — JavaScript, CSS,
o‘ng tugmani bloklash — faqat **interfeys darajasida** ishlaydi.

Bitta buyruq bilan tekshirish mumkin:

```bash
curl -s https://sayt.uz/darslar/redis/ | sed 's/<[^>]*>/ /g'
# -> darsning to'liq matni, 25 000 dan ortiq so'z
```

Butun saytni ko‘chirish ham bitta buyruq:

```bash
wget -r -np -k https://sayt.uz/
```

## Har bir choraning haqiqiy qiymati

| Chora | Kimni to‘xtatadi | Kim chetlab o‘tadi | Chetlab o‘tish vaqti |
| --- | --- | --- | --- |
| `user-select: none` | Sichqoncha bilan belgilamoqchi bo‘lgan | DevTools, reader rejimi, JS o‘chirish | 10 soniya |
| Copy/o‘ng tugmani bloklash | Tasodifiy nusxa oluvchi | Ctrl+U (manba), curl | 10 soniya |
| Chop etishni to‘sish | Ctrl+P bosgan | DevTools’da CSS o‘chirish | 30 soniya |
| Rasm/matnni JS bilan chizish | Oddiy nusxalash | OCR, skrinshot | Bir necha daqiqa |
| Suv belgisi | Hech kimni | — | Foydasi boshqa: tarqalgan nusxada manba ko‘rinadi |
| **Skrinshot bloklash** | **Hech kimni** | **Har kim** | **Web’da umuman imkonsiz** |

### Skrinshot haqida alohida

Veb-sahifada skrinshotni to‘xtatib bo‘lmaydi. Skrinshot operatsion tizim darajasida
olinadi va brauzer unga aralasha olmaydi. Netflix’dagi qora ekran — bu DRM (EME) va u
faqat **video oqimi** uchun ishlaydi, matn uchun emas. Android ilovalarda `FLAG_SECURE`
bor, lekin bu ham faqat mahalliy ilova uchun.

Ya’ni: matnli kursni skrinshotdan himoyalashning yo‘li yo‘q. Faqat **kimga
ko‘rsatayotganingizni nazorat qilish** mumkin.

## Haqiqiy himoya: uch daraja

### 1-daraja: yopiq havola (eng oddiy)

Repozitoriy private, sayt umuman chiqarilmaydi yoki faqat sizda turadi.
Kontent hech kimga ko‘rinmaydi — sotilgunicha.

- Narxi: 0
- Himoya: to‘liq (chunki hech kim ko‘rmaydi)
- Kamchilik: reklama ham qilib bo‘lmaydi

### 2-daraja: kirish nazorati (tavsiya etiladi)

Sayt bor, lekin faqat ro‘yxatdan o‘tgan/to‘lagan odam ko‘radi. Statik sayt uchun eng
arzon yo‘l — hosting darajasidagi gate:

| Yechim | Narxi | Qanday ishlaydi |
| --- | --- | --- |
| Cloudflare Pages + Access | Bepul (50 foydalanuvchigacha) | Email’ga bir martalik kod; ro‘yxatdagilar kiradi |
| Vercel / Netlify parol himoyasi | ~$20/oy | Butun saytga bitta parol |
| Netlify Identity | Bepul tarifda cheklangan | Foydalanuvchi hisoblari |

Bu darajada kontent **baribir yuklab olinadi** — lekin faqat to‘lagan odam tomonidan.
Ular tarqatsa, siz kimdan ketganini bilasiz (suv belgisi shu yerda foyda beradi).

### 3-daraja: to‘liq platforma (haqiqiy kurs sotish)

Sayt statik emas, serverli bo‘ladi:

```
Foydalanuvchi -> Auth (kirish) -> To'lov holati tekshiriladi
              -> Kontent SERVERDAN, faqat huquqi bor darsga
              -> Har sahifada foydalanuvchi ID si bilan suv belgisi
```

Kerak bo‘ladi: Next.js server rejimida (Vercel), autentifikatsiya (NextAuth yoki Clerk),
to‘lov (Payme/Click yoki Stripe), foydalanuvchilar bazasi.

- Narxi: hosting ~$0–20/oy + to‘lov tizimi komissiyasi
- Ish hajmi: 1–2 hafta
- Himoya: kontent hech qachon to‘lamagan odamga yuborilmaydi

## Hozirgi holat

`lib/site.ts` → `protection` bo‘limida quyidagilar yoqilgan:

```ts
noindex: true          // qidiruv tizimlari indekslamaydi
offlineDownload: false // "darslarni yuklab olish" tugmasi o'chirilgan
copyGuard: true        // nusxa olish va o'ng tugma cheklangan
blockPrint: true       // chop etish va PDF ga saqlash to'silgan
watermark: true        // sahifada muallif nomi (skrinshotda ko'rinadi)
```

Bularning hammasi **yuzaki qatlam**. Ular tasodifiy nusxalashni kamaytiradi va
tarqalgan skrinshotda manbani ko‘rsatadi — boshqa hech narsa emas.

## Tavsiya etiladigan tartib

1. **Hozir:** repozitoriyni private qiling va GitHub Pages’ni o‘chiring
   (Settings → Pages → Unpublish site). Kontent ochiqlikdan chiqadi
2. **Reklama uchun:** 2–3 ta darsni **bepul namuna** sifatida ochiq qoldiring,
   qolganini yoping. Odamlar sifatni ko‘rmasa, sotib olmaydi
3. **Sotish uchun:** 2-darajadan boshlang (Cloudflare Access — bepul va bir kunlik ish).
   Sotuv o‘sganda 3-darajaga o‘ting
4. **Har doim:** litsenziya faylini saqlang. Huquqiy himoya texnik himoyadan
   ko‘pincha kuchliroq ishlaydi — ayniqsa katta o‘quv markazlariga qarshi
