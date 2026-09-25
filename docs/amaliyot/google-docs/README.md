# Amaliyot: operatsion transformatsiya va Jupiter protokoli

Google Docs darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `ot.py` | **TODO** | `apply`, `transform`, `compose`, `transform_cursor` (yordamchilar tayyor) |
| `sim.py` | Tayyor | Server + N mijoz, darsdagi holat mashinasi, tasodifiy tarmoq |
| `check.py` | Tayyor | 17 ta tekshiruv: aniq holatlar, tasodifiy xususiyatlar, simulyatsiya |

```bash
python check.py                       # ~3 s
python sim.py --seeds 1000 --clients 5
python sim.py --seed 17 --verbose     # bitta stsenariy, har qadam jurnali
```

## Operatsiya yozuvi

Operatsiya — komponentlar ro‘yxati (darsning 2.1-bo‘limi):

| Komponent | Ma’nosi |
| --- | --- |
| `5` (musbat son) | 5 ta belgini o‘zgarishsiz o‘tkazish (retain) |
| `"abc"` (satr) | shu joyga “abc” qo‘shish (insert) |
| `-3` (manfiy son) | keyingi 3 ta belgini o‘chirish (delete) |

`"salom dunyo"` → `"salom, dunyo"`: `[5, ",", 6]`.

## Tekshiruv mezoni

`python check.py` oxirida `Jami: 17/17 OK`:

1. **Aniq holatlar** — darsdagi misollar: 2.2 dagi “aXb”, bir joyga
   qo‘shish (bog‘lash qoidasi), o‘chirish ichidagi qo‘shish, ustma-ust
   o‘chirishlar, compose, kursor, va 1 M belgili hujjatda transform
   hujjat uzunligiga bog‘liq emasligi (6.1).
2. **Tasodifiy xususiyatlar** — 20 000 juftlikda TP1, 5 000 da compose,
   natijalar `normalize` qilingan.
3. **Simulyatsiya** — 2, 3 va 5 mijoz bilan 400 stsenariyda yaqinlashish;
   “faqat qo‘shish” rejimida har noyob token yakuniy matnda **aynan
   bir marta** (hech narsa yo‘qolmadi va takrorlanmadi).

## Maslahatlar

- `transform` ni ikki ko‘rsatkich bilan yozing (darsning 6.1-bo‘limi):
  avval qo‘shishlar (a niki birinchi — bog‘lash qoidasi), keyin ikkala
  tomonning retain/delete’larini `min` uzunlik bo‘yicha bo‘lib yuring.
- `compose` ham xuddi shunday yuradi, lekin boshqa savol bilan: `a` ning
  natijasi — `b` ning kirishi. `a` dagi o‘chirishlar va `b` dagi
  qo‘shishlar “bepul” o‘tadi.
- Aniq testlar o‘tib, tasodifiy testlar yiqilsa — `sim.py --seed N --verbose`
  birinchi ajralishni qadam-baqadam ko‘rsatadi. Bu darsning 6.3-bo‘limidagi
  gapning aynan o‘zi: kichik chekka xatolarni faqat tasodifiy testlar topadi.
