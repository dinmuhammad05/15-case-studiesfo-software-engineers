# Amaliyot: ovoz quvuri va `hot` ro‘yxati

Bu — Reddit darsining 2-daraja (asosiy) topshirig‘i uchun skelet.
**O‘lchov qismi tayyor**, mantiq qismi `TODO` bilan belgilangan.

## Maqsad

Ovozni to‘g‘ridan-to‘g‘ri bazaga yozish o‘rniga navbat orqali guruhlab
qo‘llash, va bu qaror DB yozuv tezligi hamda ro‘yxat kechikishiga qanday
ta’sir qilishini **o‘lchash**.

## Fayllar

| Fayl | Nima qilasiz |
| --- | --- |
| `schema.sql` | Tayyor. Postgres sxemasi: `posts`, `votes`. |
| `ranking.py` | TODO: `hot_score` va `wilson_lower_bound`. |
| `worker.py` | TODO: guruhlash oynasi, ovozlarni qo‘llash, ZADD. |
| `api.py` | TODO: `POST /vote`, `GET /r/<sub>/hot`. |
| `bench.py` | Tayyor. Yuk testi, metrikalar va taqqoslash jadvali. |

## Ishga tushirish

```bash
pip install -r requirements.txt
psql "$DATABASE_URL" -f schema.sql

python worker.py &                 # ishchi
uvicorn api:app --port 8000 &      # API

python bench.py --rate 2000 --seconds 60 --batching on
python bench.py --rate 2000 --seconds 60 --batching off
```

## Tekshiruv mezoni

`bench.py` ikkita rejim uchun quyidagi jadvalni chiqaradi:

```
rejim        db_writes/s   listing_p99_ms   vote_lag_p99_ms
batching=on        ~40           ~12               ~110
batching=off      ~2000          ~45                 ~2
```

- **DB yozuvi kamida 20 barobar kamayishi kerak.** Farq 5 barobardan kam
  bo‘lsa — guruhlash kaliti noto‘g‘ri (ehtimol har bir ovoz alohida
  tranzaksiyada qo‘llanyapti).
- **Ro‘yxat p99 oshmasligi kerak** — guruhlash o‘qishni sekinlashtirmaydi.
- **Ovoz lagi oshadi** va bu kutilgan narx: 100 ms oyna = ~100 ms lag.

Uchala raqamni bitta grafikda ko‘rsating. Darsdagi 6-bo‘limdagi
hisob 50 barobar tejashni bashorat qiladi — o‘lchoviningiz undan qancha
farq qilganini va nima uchun ekanini yozing.
