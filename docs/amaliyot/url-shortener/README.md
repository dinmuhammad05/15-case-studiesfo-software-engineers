# Amaliyot: qisqa havola xizmatining yuragi

URL qisqartiruvchi darsining 2-daraja topshirig‘i uchun kod. Faqat Python
3.9+ standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `keys.py` | **TODO** | Base62, Feistel aralashtirish, blok bo‘yicha kalit ajratish (KGS) |
| `bloom.py` | **TODO** | Bloom filtri: yo‘q kalitlarni bazaga yubormasdan rad etish |
| `cache.py` | **TODO** | Kesh: LRU, TTL, salbiy kesh, single-flight, stale-while-revalidate |
| `model.py` | Tayyor | Alifbo, barqaror xesh, markaziy hisoblagich, “baza”, Zipf trafigi |
| `check.py` | Tayyor | 17 ta tekshiruv, ~4 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

Qisqa havola xizmati ikkita savolga javob beradi: “yangi havolaga qaysi
kalitni beraman?” va “bu kalit qayerga olib boradi?”. Birinchisi kuniga
millionlab marta, ikkinchisi esa sekundiga o‘n minglab marta so‘raladi.

1. **Kalit** (`keys.py`). Kalitlar takrorlanmasligi va taxmin qilinmasligi
   kerak. Markaziy hisoblagich takrorlanmaslikni kafolatlaydi, lekin unga
   har safar murojaat qilish qimmat. Shuning uchun har server undan bir
   yo‘la 1000 ta son oladi. Hisoblagich ketma-ket son beradi (1, 2, 3, ...),
   **Feistel** esa ularni tasodifiyga o‘xshash, lekin baribir takrorsiz
   sonlarga aylantiradi.
2. **Bloom filtri** (`bloom.py`). Skaner mavjud bo‘lmagan kalitlarni
   so‘raydi. Filtr kichik xotirada “bu kalit aniq yo‘q” deb javob beradi,
   shunda bunday so‘rovlar bazaga ham, keshga ham yetib bormaydi.
3. **Kesh** (`cache.py`). Bazaga borish sekin. Kesh mashhur havolalarni
   xotirada ushlaydi va uchta tuzoqdan himoya qiladi:
   - bir lahzada minglab so‘rov bitta havolani so‘rasa — bazaga faqat bittasi
     boradi (**single-flight**);
   - muddat tugaganda hech kim kutmaydi — eski javob beriladi, yangisi fonda
     yuklanadi (**stale-while-revalidate**);
   - yo‘q kalitlar alohida joyda saqlanadi va issiq havolalarni siqib
     chiqarmaydi (**salbiy kesh**).

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 17/17 OK`:

1. **Kalitlar** (5 ta): base62 va xatolar; kichik domenlarda Feistel
   bijeksiyasi to‘liq tekshiriladi; 62^7 domenida teskarisi, sirning roli va
   ketma-ketlikni yashirish; 3 server va 25 000 kalit bilan takrorsizlik va
   markazga murojaatlar soni; qayta ishga tushish.
2. **Bloom filtri** (3 ta): `m` va `k` formulasi; noto‘g‘ri manfiy javob yo‘q;
   noto‘g‘ri ijobiy ulush va’da qilingan `p` ga yaqin.
3. **Kesh** (5 ta): birlik testlari; 60 ta tasodifiy ketma-ketlikda sodda
   model bilan **aynan** bir xil javob va bazaga o‘qishlar soni; stampede;
   SWR; skaner.
4. **Tizim** (3 ta): bir daqiqalik trafik. Unda 60 000 havola, Zipf
   bosishlar, 15% skaner, viral havola, yangi havolalar va 200 ta eng
   mashhur havolaning o‘chirilishi bor. Tekshiriladi: har javob to‘g‘ri,
   bazaga yuk ≤ 16%, skaner bazaga deyarli yetmaydi.
5. **Tezlik**: 50 000 kalit va 300 000 kesh so‘rovi — 4 soniyadan tez.

## Maslahatlar

- **Base62**: `divmod(n, 62)` bilan qoldiqlarni yig‘ing va oxirida teskari
  aylantiring. `encode(0)` — `"0"`, bo‘sh satr emas.
- **Feistel raundi**: `L, R = R, L ^ F(R, i)`. Teskarisi:
  `L, R = R ^ F(L, i), L`, raundlar teskari tartibda. F’ning o‘zi teskari
  bo‘lishi shart emas — Feistel’ning go‘zalligi shunda.
- **Nega cycle walking bijeksiyani saqlaydi**: `_enc` — `[0, 2^bits)` dagi
  bijeksiya, ya’ni har son bitta tsiklda yotadi. `x` dan boshlab tsikl
  bo‘ylab yurib, domen ichiga tushgan **birinchi** songa to‘xtaymiz. Ikki
  xil `x` bir xil natijaga kelolmaydi: aks holda ulardan biri yo‘lda
  ikkinchisining natijasidan o‘tgan bo‘lardi, demak o‘sha yerda to‘xtagan
  bo‘lardi. `bits` domenga yaqin bo‘lgani uchun o‘rtacha 1–4 qadam yetadi.
- **`% domain` bilan qisqartirish xato**: ikki xil son bir xil qoldiq
  beradi — takror kalit.
- **Kesh**: `OrderedDict` — tayyor LRU (`move_to_end`, `popitem(last=False)`).
  Har so‘rovda ro‘yxat bo‘ylab yurish tezlik testidan o‘tmaydi.
- **Single-flight**: yuklanayotgan kalitlar — `self.inflight`. So‘rov kelsa
  va kalit shu yerda bo‘lsa, bazaga bormang, natijani kuting.
- **Bekor qilingan yuklanish**: `invalidate` kalitni `self.inflight` dan
  o‘chiradi, lekin heap’da yozuv qoladi. `_settle` uni tanib, o‘tkazib
  yuborishi kerak.
