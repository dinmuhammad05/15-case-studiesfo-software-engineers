# Amaliyot: ikki gateway, pub/sub va quvib yetish

Slack darsining 2-daraja (asosiy) topshirig‘i uchun skelet.
**Yuk testi va o‘lchov qismi tayyor**, mantiq qismi `TODO` bilan belgilangan.

## Maqsad

Ikkita gateway jarayoni Redis pub/sub orqali bog‘lanadi. Mijoz istalgan
gateway’ga ulanadi va kanaldagi barcha xabarlarni oladi. Gateway o‘ldirilganda
mijoz qayta ulanadi va yo‘qotganini **tarixdan quvib yetadi** — hech bir xabar
yo‘qolmaydi.

O‘lchanadigan narsa: xaos testidan keyin har bir mijoz aynan yuborilgan
xabarlar to‘plamini olganmi, va jitter qayta ulanish cho‘qqisini qancha
pasaytiradi.

## Fayllar

| Fayl | Nima qilasiz |
| --- | --- |
| `schema.sql` | Tayyor. `messages`, `channels` sxemasi. |
| `gateway.py` | TODO: WebSocket, obunalar, pub/sub, quvib yetish. |
| `api.py` | TODO: `POST /send` — `ts` tayinlash, saqlash, e’lon qilish. |
| `client.py` | TODO: qayta ulanish, jitter, `last_seen` kursorlari. |
| `chaos.py` | Tayyor. Gateway’ni o‘ldiradi va qaytaradi. |
| `bench.py` | Tayyor. Yuk, o‘lchov va tekshiruv hisoboti. |

## Ishga tushirish

```bash
pip install -r requirements.txt
psql "$DATABASE_URL" -f schema.sql

PORT=8001 python gateway.py &
PORT=8002 python gateway.py &
uvicorn api:app --port 8000 &

# Jitter bilan
python bench.py --clients 5000 --rate 100 --seconds 120 --jitter on
# Jittersiz
python bench.py --clients 5000 --rate 100 --seconds 120 --jitter off
```

`bench.py` o‘zi `chaos.py` ni chaqiradi: test o‘rtasida gateway 8001
o‘ldiriladi va 10 soniyadan keyin qaytariladi.

## Tekshiruv mezoni

```
rejim         lost   dup_detected   catchup_avg   reconnect_peak/s
jitter=on        0            142          0.31              ~420
jitter=off       0            138          0.29             ~4800
```

1. **`lost` aynan 0 bo‘lishi shart** — ikkala rejimda ham. Noldan katta
   bo‘lsa, quvib yetish mantiqingiz `last_seen` kursorini noto‘g‘ri
   yangilayapti (odatda: xabar UI’ga qo‘shilgunicha kursor siljitilgan).
2. **Dublikatlar `client_msg_id` bo‘yicha aniqlangan bo‘lsin** — hisobot
   `dup_delivered` (mijoz ikki marta ko‘rsatgan) ni 0 deb ko‘rsatishi kerak.
3. **Jitter cho‘qqini kamida 10 barobar pasaytirsin.** Farq 3 barobardan
   kam bo‘lsa, `random(0, backoff)` o‘rniga `backoff + random(0, kichik)`
   yozgan bo‘lishingiz mumkin — bu to‘liq jitter emas.

Uchala raqamni bitta grafikda ko‘rsating: vaqt bo‘yicha ulanishlar soni,
qayta ulanish tezligi va yetkazish kechikishi. Gateway o‘lgan lahza
grafikda aniq ko‘rinishi kerak.
