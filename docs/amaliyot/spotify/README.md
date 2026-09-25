# Amaliyot: tinglashlar kitobi va royalti

Spotify darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi — hech narsa o‘rnatish shart emas.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `gen.py` | Tayyor | Bir oylik sintetik hodisalar oqimi (~540 000 hodisa, ~75 MB) |
| `check.py` | Tayyor | 15 ta tekshiruv va firibgar ulushi jadvali |
| `pipeline.py` | **TODO** | 9 ta funksiya: dedublikatsiyadan royaltigacha |

```bash
python gen.py       # bir marta, ~15 s; data/ papkasini yaratadi
python check.py     # har o'zgarishdan keyin, ~3 s
```

`data/truth.json` — to‘g‘ri javoblar. Uni o‘qish topshiriqning
ma’nosini yo‘qotadi: haqiqiy tizimda “to‘g‘ri javob” yo‘q.

## Oqimda nima bor

| Hodisa | Darsdagi bo‘lim | Qaysi funksiya ushlaydi |
| --- | --- | --- |
| Qayta yuborilgan dublikatlar (~2%) | 9-qadam, 8.4 Deep | `dedup` |
| Soati 1–3 kun oldinda qurilmalar | 8.4 | `quarantine` |
| Oflayn tinglashlar, 20 kungacha kechikish | 7.3, 8.4 | `split_month` |
| Mart oxirida boshlanib, aprelga o‘tgan tinglashlar | 8.4 | `split_month` |
| O‘tkazishlar va aynan 30 000 ms | 6.3 Deep, 8.3 | `qualify` |
| 8 ta “baland” bot (5 kun, kuniga 20 soat) | 12.2 | `detect_bots` |
| 4 ta “sokin” bot (butun oy, kuniga ~1.5 soat) | 12.2 Deep | `detect_bots` |
| 10 ta haqiqiy odam, kuniga ~10 soat | 15.2 Callout | `detect_bots` (ularni belgilamang!) |
| Yo‘qolgan hodisalar (~0.3%) | 15.2 Deep | `loss_rate` |

## Tekshiruv mezoni

`python check.py` oxirida `Jami: 15/15 OK`. Tekshiruvlar:

1. Noyob hodisalar soni aniq; har id uchun **eng erta** kelgan nusxa.
2. Karantin soni aniq; hech bir hodisa yo‘qolmagan.
3. O‘z vaqtidagi tinglashlar va tuzatishlar — **har trek bo‘yicha aniq**.
4. Botlar: aniqlik ≥ 0.9, to‘liqlik ≥ 0.9, ko‘p tinglaydigan odamlar belgilanmagan.
5. Yo‘qotish bahosi haqiqiydan 25% dan ko‘p farq qilmaydi.
6. Royalti: pro-rata yig‘indisi = fond; foydalanuvchi-markazlida botlar
   o‘z obunasidan ko‘p ololmaydi; bot filtri bilan firibgar ulushi ~0.

Oxirida jadval chiqadi — firibgar ijrochining ulushi ikki model va
filtr bilan/filtrsiz. Uni darsdagi 12.2-bo‘limdagi Check bilan
solishtiring.

## Maslahatlar

- Uchinchi tekshiruv “aniq” — bitta chegaradagi xato (`>` va `>=`,
  `at` va `et`) uni buzadi. Bu ataylab: buxgalteriyada “deyarli to‘g‘ri”
  yo‘q (darsning 4.4-bo‘limi).
- `detect_bots` uchun hajm chegarasi yetmaydi: sokin botlar ko‘p
  tinglaydigan odamlardan **kam** tinglaydi. 12.2-jadvaldagi boshqa
  belgilarga qarang.
- `loss_rate` da har qurilmaning oxirgi hodisalari yo‘qolgan bo‘lsa,
  ularni ko‘rib bo‘lmaydi — baho biroz past chiqishi normal.
