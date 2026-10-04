# Amaliyot: Redis’ning uchta ichki mexanizmi

Redis darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+ standart
kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `skiplist.py` | **TODO** | ZSET ichidagi skiplist: span bilan O(log N) rank va diapazonlar |
| `hll.py` | **TODO** | HyperLogLog: 16 384 registr, garmonik o‘rtacha, linear counting, merge |
| `keyspace.py` | **TODO** | TTL (passiv + faol), `maxmemory` siyosatlari, namunali LRU |
| `model.py` | Tayyor | Skiplist tuguni, barqaror xesh, Zipf trafigi |
| `check.py` | Tayyor | 15 ta tekshiruv, ~9 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

1. **Musobaqa jadvali** (`skiplist.py`). Million o‘yinchi, ballar har
   soniyada o‘zgaradi, va har kim “men nechanchi o‘rindaman?” deb so‘raydi.
   Skiplist — metrodagi oddiy va ekspress poyezdlarga o‘xshaydi: yuqori
   qavatlarda bekatlar siyrak, shuning uchun uzoqqa tez yetasiz. **Span**
   esa har “ekspress” nechta bekatni o‘tkazib yuborganini eslaydi —
   o‘rinni shundan hisoblaysiz.
2. **“Bugun nechta odam keldi?”** (`hll.py`). Har odamni eslab qolmasdan,
   12 KB xotirada milliardgacha sanash. Fikr: tanga tashlaganda eng uzun
   “gerb” seriyasi necha marta tashlanganini taxminan aytadi.
3. **Muzlatgich** (`keyspace.py`). Yaroqlilik muddati o‘tganlarni tozalash
   (lekin hammasini har soniya tekshirmasdan) va joy qolmaganda eng kam
   ishlatilganini chiqarib tashlash (lekin hamma narsani tartibda
   ushlamasdan).

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 15/15 OK`:

1. **Skiplist** (4 ta):
   - 40 × 300 tasodifiy amalda sodda model bilan bir xil natija;
   - ichki tuzilma: har qavat tartiblangan, har span 0-qavatdagi haqiqiy
     masofaga teng, backward va tail to‘g‘ri, `level` eng baland tugunga
     teng;
   - darajalar taqsimoti ~`P = 0.25`;
   - `rank` O(log N), chunki ko‘rsatkich o‘qishlar sanaladi;
   - ZSET qobig‘i.
2. **HyperLogLog** (4 ta): `index_rank`, registrlar aynan bir xil,
   aniqlik turli n larda, `merge`.
3. **Kalit maydoni** (3 ta):
   - birlik testlari (TTL, `-1`/`-2`, siyosatlar);
   - faol ekspirasiya: eskirganlar ulushi ~25%, budjet, tinch sikl;
   - namunali LRU haqiqiy LRU bilan solishtiriladi.
4. **Bir o‘yin kuni** (3 ta): reyting aniq javob bilan, kunlik va
   haftalik noyob o‘yinchilar, sessiyalar.
5. **Tezlik**.

## Maslahatlar

- **Skiplist `insert`**: yuqoridan pastga tushib, har qavatda “oxirgi
  oldingi tugun” (`update[i]`) va unga qadar span yig‘indisini (`rank[i]`)
  saqlang. Yangi tugunning `i`-qavatdagi span’i:
  `update[i].span[i] - (rank[0] - rank[i])`, oldingisiniki:
  `rank[0] - rank[i] + 1`. Yangi tugundan yuqori qavatlarda
  `update[i].span[i] += 1`. Bu Redis’ning `zslInsert` funksiyasi.
- **`delete`**: ko‘rsatkichi o‘chirilayotgan tugunga qaragan qavatlarda
  `span += x.span - 1`, qolganlarida `span -= 1`. Keyin bo‘sh qolgan yuqori
  qavatlarni `level` dan olib tashlang.
- **`by_rank`**: boshlanish o‘rniga span bo‘yicha sakrang
  (`traversed + span <= target`), keyin 0-qavatda yuring.
- **HLL rank**: `w & 1` bilan quyi bitlarni tekshiring; `w == 0` — alohida
  holat (51).
- **O(1) o‘chirish**: `i = pos.pop(k)`, oxirgi elementni `i` ga qo‘ying va
  uning `pos` ini yangilang. Oxirgisi `k` ning o‘zi bo‘lsa — shunchaki pop.
- **Faol sikl**: namuna faqat **TTL li** kalitlardan (`vkeys`). Hamma
  kalitlardan namuna olsangiz, TTL siz millionlab kalit orasida eskirganlar
  “ko‘rinmay” qoladi.
