# Amaliyot: bron dvigateli

Airbnb darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi (`sqlite3`, `multiprocessing`).

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `booking.py` | **TODO** | `nights`, `create_hold`, `confirm`, `cancel`, `expire_holds`, `search_available` |
| `schema.sql` | Tayyor | E’lonlar, bronlar, `booked_nights` (`PRIMARY KEY (listing_id, night)`), kitob |
| `db.py` | Tayyor | Ulanish, `tx()`, narx, xatolar, soxta to‘lov provayderi |
| `check.py` | Tayyor | 25 ta tekshiruv, jumladan 8 ta parallel jarayon bilan |

```bash
python check.py        # ~7 s
```

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 25/25 OK`:

1. **Tun modeli** (darsning 2-bo‘limi) — yarim ochiq oraliq, kabisa yili,
   ketma-ket bronlar, `min_nights`, va band bo‘lganda bazada hech narsa
   qolmasligi (atomiklik).
2. **HOLD, idempotentlik, to‘lov, kitob** (5-bo‘lim 2–5-qadamlar) —
   bir xil kalit bir xil bron beradi; muddati o‘tgan HOLD tunni band
   qilmaydi; rad etilgan to‘lov tunlarni bo‘shatadi; **taymaut**da
   (pul yechildi, javob yo‘qoldi) bron HOLD’da qoladi va qayta urinish
   pulni ikkinchi marta yechmaydi; bekor qilish kitobni sof nolga qaytaradi.
3. **Qidiruv** (6-bo‘lim) — 700 ta tasodifiy bron (ularning bir qismi
   muddati o‘tgan HOLD) ustida 60 ta so‘rov sodda hisob bilan solishtiriladi.
4. **Parallellik** — 8 ta jarayon bir vaqtda (to‘siq bilan sinxron):
   bir e’longa kesishgan sanalar, bir xil idempotentlik kaliti, bir
   bronni bir vaqtda tasdiqlash va bekor qilish. Ikki marta bron
   **mustaqil tekshiruvchi** (darsning 14.2-bo‘limi) bilan — tunlar
   jadvaliga emas, bronlar oraliqlariga qarab — aniqlanadi. Oxirida
   rekonsilyatsiya (8.4): provayderdagi sof pul kitobdagi mehmon
   to‘lovlariga teng.

4-qism faqat 1–3-qismlar to‘liq o‘tganda ishga tushadi.

## Maslahatlar

- Kafolatni kodga emas, bazaga bering. `booked_nights` ga tunlarni
  oddiy `INSERT` bilan yozing; `sqlite3.IntegrityError` — “band” degani.
  `INSERT OR IGNORE` — xato: to‘qnashuv jim yutiladi va bron qatori
  tunlarsiz qoladi.
- Tekshiruv va yozish **bitta** `db.tx(conn)` ichida bo‘lsin. Tranzaksiyadan
  tashqaridagi “bo‘shmi?” tekshiruvi ketma-ket testlardan o‘tadi, lekin
  parallel testda ikki marta bron beradi — bu darsning 4.1-bo‘limi.
- `db.tx` ichida `Busy` ko‘tarsangiz, u yozilgan hamma narsani qaytaradi.
  Istisnoni ichkarida “yutib”, keyin qaytish — yarim yozilgan bron qoldiradi.
- Provayder chaqiruvi tranzaksiyadan **tashqarida** (4.2). Ichida
  chaqirsangiz, provayder bazaning yozish qulfini 5 soniya kutadi va
  `database is locked` bilan yiqiladi — test buni ko‘rsatadi.
- Holat o‘tishlarini shartli yozing: `UPDATE ... SET state='CONFIRMED'
  WHERE id=? AND state='HOLD'` va `rowcount` ga qarab kitobga yozing.
  Shunda bir vaqtdagi ikki `confirm` dan faqat bittasi kitobga yozadi.
- Idempotentlik kalitlari deterministik bo‘lsin: `charge:{booking_id}`,
  `refund:{booking_id}`. Vaqt yoki jarayon ID si qo‘shilgan kalit —
  kalit emas.
