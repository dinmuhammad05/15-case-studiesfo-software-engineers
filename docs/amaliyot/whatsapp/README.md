# Amaliyot: saqla va uzat — belgilar bilan

WhatsApp darsining 1- va 2-daraja topshiriqlari uchun kod.
**Hech qanday server, baza yoki tarmoq kerak emas** — hammasi bitta
Python jarayonida, virtual vaqt bilan.

## Fayllar

| Fayl | Holati | Nima qilasiz |
| --- | --- | --- |
| `dh_demo.py` | Tayyor | 1-daraja: kichik sonlar bilan DH va X25519 o‘lchovi |
| `common.py` | Tayyor | `Envelope` va `LOST` |
| `relay.py` | **TODO** | Server: navbat, idempotent qabul, qayta yetkazish, ✓✓ uzatish |
| `phone.py` | **TODO** | Telefon: yuborish, qayta urinish, dublikatni tanish, monoton belgilar |
| `bench.py` | Tayyor | Simulyatsiya, tekshiruvlar, Little qonuni |

## 1-daraja

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python dh_demo.py              # p=23, g=5, a=6, b=15
python dh_demo.py 23 5 4 9     # o'z sonlaringiz
```

## 2-daraja

`relay.py` va `phone.py` dagi `TODO` larni to‘ldiring, keyin:

```bash
python bench.py                 # 500 telefon, 1 soat, 5% paket yo'qotish
python bench.py --drop 0.15     # yomonroq tarmoq — baribir o'tishi kerak
```

Simulyatsiyada nima bo‘ladi:

- telefonlar uch guruhda onlayn/oflayn bo‘ladi (darsning 6.1-bo‘limi kabi):
  A deyarli doim onlayn, B tez-tez oflayn, C ko‘p vaqt oflayn;
- har bir tarmoq chaqiruvida **so‘rov yoki javob** yo‘qolishi mumkin —
  ikkinchisida funksiya bajarilgan, lekin chaqiruvchi buni bilmaydi;
- oxirida 300 soniyalik “drenaj”: hamma onlayn, yangi xabar yo‘q,
  navbat bo‘shashi kerak.

## Tekshiruv mezoni

```
--- tekshiruv ---
  OK   lost == 0
  OK   dup_shown == 0
  OK   tick_regressions == 0
  OK   hamma ✓✓ oldi
  OK   Little farqi <= 20%
```

Beshtasi ham `OK` bo‘lishi shart, `--drop 0.15` da ham. Xato bo‘lsa,
bench qayerga qarashni aytadi. Eng ko‘p uchraydiganlari:

| Belgi | Odatdagi sabab |
| --- | --- |
| `lost > 0` | Relay xabarni telefon ack’ini kutmasdan o‘chiryapti |
| `dup_shown > 0` | `on_deliver` bir xil `(frm, msg_id)` ni ikkinchi marta ko‘rsatyapti |
| ✓✓ olmaganlar > 0 | `status = 1` yozilyapti, `max()` o‘rniga — kechikkan ✓ ✓✓ ni o‘chiradi |
| Little farqi katta | `_accepted()` / `_removed()` chaqirilmayapti |

Hisobotdagi “navbat hajmi guruhlar bo‘yicha” qismiga alohida qarang:
telefonlarning ~20% i bo‘lgan B va C guruhlari navbatning deyarli
hammasini egallaydi. Bu — darsdagi “dum hamma narsani belgilaydi”
xulosasining kichik miqyosdagi takrori.
