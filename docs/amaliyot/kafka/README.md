# Amaliyot: partition replikatsiyasi

Apache Kafka darsining 2-daraja topshirig‘i uchun kod. Faqat Python 3.9+
standart kutubxonasi.

| Fayl | Holati | Nima uchun |
| --- | --- | --- |
| `replication.py` | **TODO** | `append`, `update_hw`, `on_fetch`, `on_response`, `end_offset_for_epoch`, `truncate`, `consumer_read` |
| `model.py` | Tayyor | `Record`, `Replica` (jurnal + HW), `LeaderState` (ISR, izdoshlar LEO lari) |
| `sim.py` | Tayyor | 3 brokerli simulyator: qulash, qaytish, tarmoq uzilishi, toza saylov, elektr o‘chishi |
| `check.py` | Tayyor | 16 ta tekshiruv, ~1 soniya |

```bash
python check.py
```

## Oddiy tilda: nima qurasiz

Bitta partition’ning uch nusxasi uch brokerda. Yetakchi yozuvlarni qabul
qiladi, izdoshlar undan “offset X dan keyingilarni ber” deb so‘rab, nusxa
oladi. Siz yetakchi va izdosh **mantiqini** yozasiz: kim yetib oldi (ISR),
qaysi yozuvlar tasdiqlangan (high watermark), yetakchi almashganda izdosh
dumini qayergacha kesadi (leader epoch). Simulyator esa brokerlarni
tasodifiy o‘ldiradi, qaytaradi, tarmoqni uzadi va sizning kodingiz bilan
yuzlab yetakchi almashinuvini o‘tkazadi.

## Nimalar tekshiriladi

`python check.py` oxirida `Jami: 16/16 OK`:

1. **Birlik testlari**: idempotent `append` (bir xil `(pid, seq)` — bir xil
   offset), HW qoidalari (ISR minimumi, kamaymaydi, izdosh HW si LEO dan
   oshmaydi), `end_offset_for_epoch` ning 7 holati, `truncate`, faqat HW
   gacha o‘qish, `min.insync.replicas`.
2. **Darsdagi stsenariylar** (7-qadam va 6.3 Deep): KIP-101 ning ikki holati —
   qayta ishga tushgan izdosh tasdiqlangan xabarni o‘chirmaydi va elektr
   o‘chishidan keyin nusxalar ajralmaydi; KIP-279 holati — izdoshning oxirgi
   davri yetakchida umuman yo‘q; ISR ning kichrayishi va faqat yetib olgach
   kengayishi.
3. **Xaos**: 40 ta stsenariy (~250 yetakchi almashinuvi) — birorta ham
   tasdiqlangan xabar yo‘qolmaydi, takror yo‘q, nusxalar bir xil, o‘quvchi
   hech qachon keyin yo‘qolgan (“arvoh”) yozuvni ko‘rmaydi. Va 25 ta “elektr
   o‘chishi” stsenariysi — nusxalar hech qachon ajralmaydi.

## Maslahatlar

- **HW = ISR dagi LEO larning minimumi**, yetakchida hech qachon kamaymaydi.
  Yolg‘iz ISR da `append` dan keyin darhol siljiydi.
- **ISR ga faqat yetib olganda qo‘shing** (`fetch_offset >= leader.leo`).
  Orqada qolgan izdoshni ISR ga qo‘shish xaos testida tasdiqlangan xabarlar
  yo‘qolishiga olib keladi.
- **Hech qachon o‘z HW ingiz gacha kesmang** — izdosh HW si eskirgan
  bo‘lishi mumkin. `end_offset_for_epoch` ikki qadamda ishlatiladi (qarang:
  docstring va `sim.py` dagi `truncate_followers`).
- **Idempotentlik kaliti — `(pid, seq)` juftligi**, faqat `seq` emas: turli
  ishlab chiqaruvchilarning raqamlari bir xil bo‘lishi mumkin.
- Biror xaos stsenariysi yiqilsa, `Sim(rep, seed=N)` ni o‘zingiz ishga
  tushirib, `sim.events` ro‘yxatini (qulashlar, saylovlar) ko‘ring.
