# Amaliyot: ETA dvigateli

Uber ETA darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `eta.py` | **TODO** | `dijkstra`, `astar`, `bidirectional`, `live_speeds`, `fit_residual`, `predict` |
| `city.py` | Tayyor | Sintetik shahar (70×70 chorraha, magistrallar, bir tomonlama ko‘chalar, daryo va 3 ko‘prik), GPS o‘tishlari va safarlar |
| `check.py` | Tayyor | 20 ta tekshiruv, ~3 soniya |

```bash
python check.py
```

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 20/20 OK`:

1. **Qidiruv** (darsning 5-bo‘limi, 1–3-qadamlar). Uchala algoritm 140 ta
   tasodifiy juftlikda mustaqil “orakul” (navbatli yorliq-tuzatish, Dijkstra
   emas) bilan solishtiriladi: vaqt ham, yo‘lning haqiqiyligi ham. Uzun
   safarlarda A* va ikki tomonlama qidiruv Dijkstra’ning 75% idan kam tugun
   ko‘rishi kerak. Alohida testlar: `s == t`, yetib bo‘lmaydigan tugun,
   o‘rnatilgan tugunlarni to‘g‘ri sanash, daryo va ko‘prik, va ikki tomonlama
   qidiruvning klassik tuzog‘i — birinchi uchrashuv nuqtasi eng qisqa yo‘lda
   bo‘lmagan kichik graf.
2. **Jonli tezliklar** (7–8-qadamlar). Kuzatuvlarning 15% i “to‘xtab turgan”
   haydovchilar (10 barobar sekin), ba’zilari eskirgan, kelajakdagi yoki
   imkonsiz (GPS sakrashi). Bitta haydovchi 10 ta sekin kuzatuv bilan natijani
   egallab olmasligi kerak. Tarix bilan aralashtirish formulasi aniq
   tekshiriladi. Oxirida — jonli og‘irliklar bilan topilgan marshrutlarning
   ETA’si haqiqatga kamida 30% yaqinroq.
3. **Qoldiq modeli** (10-qadam). Safarlarning 3% i chiqib ketish (2–4 barobar
   uzun). MAE marshrut ETA’sidan kamida 45% kam, siljish (bias) ±3% ichida,
   cho‘qqi soat tunnikidan uzun, kam ma’lumotli va noma’lum zonalar soat
   darajasiga tushadi.

## Maslahatlar

- Dijkstra’da javob `t` navbatdan **chiqarilganda** aniq. Unga birinchi marta
  yetilganda qaytish — ba’zi juftliklarda noto‘g‘ri (test buni ko‘rsatadi).
- `heapq` kalitni kamaytira olmaydi: bir tugun navbatda bir necha marta
  bo‘ladi. Allaqachon o‘rnatilganini ikkinchi marta sanamang.
- A* evristikasi uchun `g.dist(u, t) / (vmax_kmh * 1000 / 3600)`. Tezlikni
  “o‘rtacha”ga almashtirsangiz, javoblar ba’zan 1–3% uzun bo‘ladi — faqat
  tasodifiy taqqoslash buni ushlaydi.
- Ikki tomonlama qidiruvda `mu` ni qirra ikkinchi tomon **ko‘rgan** (hali
  o‘rnatilmagan bo‘lsa ham) tugunga olib borganda yangilang; to‘xtash —
  `oldinga_navbat_boshi + orqaga_navbat_boshi >= mu`.
- `live_speeds`: avval har haydovchi bo‘yicha mediana, keyin haydovchilar
  bo‘yicha mediana. O‘rtacha qiymat 15% “to‘xtagan” kuzatuvga chidamaydi.
- `fit_residual`: nisbatlarning **medianasi**. O‘rtacha 3% chiqib ketish
  bilan ~6% siljish beradi.
