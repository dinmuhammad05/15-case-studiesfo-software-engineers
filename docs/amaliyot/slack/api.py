"""Xabar API: ts tayinlaydi, saqlaydi, pub/sub'ga e'lon qiladi."""
import os

import psycopg
import redis
from fastapi import FastAPI
from pydantic import BaseModel

REDIS = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost"))
DSN = os.environ["DATABASE_URL"]

app = FastAPI()


class Send(BaseModel):
    channel: str
    user_id: str
    text: str
    client_msg_id: str  # UUID, mijoz yaratadi


def assign_ts(conn, channel_id: str) -> str:
    """Kanal uchun monoton ts tayinlaydi.

    Darsning 5.5-qadami: ts'ni gateway EMAS, kanal egasi tayinlaydi.
    Bitta yozuvchi bo'lgani uchun soat farqi ahamiyatsiz.

    TODO:
      1. Tranzaksiya ichida: SELECT last_ts FROM channels
         WHERE id = %s FOR UPDATE
      2. ts = max(time.time(), last_ts + 0.000001)
         -- max() ikkita kafolat beradi: vaqt orqaga ketmaydi,
         -- va ikki xabar bir xil ts olmaydi.
      3. UPDATE channels SET last_ts = ts
      4. f"{ts:.6f}" satr sifatida qaytaring — float emas!
         (JS'da float64 16 raqamni aniq saqlay olmaydi)
    """
    raise NotImplementedError("TODO: assign_ts")


@app.post("/send", status_code=201)
def send(m: Send):
    """Xabarni saqlaydi va kanalga e'lon qiladi.

    TODO:
      1. assign_ts bilan ts oling
      2. INSERT ... ON CONFLICT (channel_id, client_msg_id) DO NOTHING
         RETURNING ts
         -- Konflikt bo'lsa: eski ts'ni SELECT qilib qaytaring.
         -- Bu idempotentlik: qayta yuborish yangi xabar yaratmaydi.
      3. Faqat YANGI xabar bo'lsa e'lon qiling:
         REDIS.publish(f"ch:{m.channel}", json.dumps({...}))
      4. {"ts": ts, "duplicate": bool} qaytaring

    MUHIM: avval saqlang, keyin e'lon qiling (darsning 5.3-qadami).
    Teskari tartibda e'lon qilsangiz va yozish muvaffaqiyatsiz bo'lsa,
    mijozlar bazada yo'q xabarni ko'radi va quvib yetishda u g'oyib bo'ladi.
    """
    raise NotImplementedError("TODO: send")


@app.get("/history/{channel}")
def history(channel: str, after: str = "0", limit: int = 200):
    """Quvib yetish so'rovi: ts > after.

    TODO:
      SELECT ts, user_id, text, client_msg_id FROM messages
      WHERE channel_id = %s AND ts > %s ORDER BY ts LIMIT %s

    ts'ni javobda SATR sifatida qaytaring (str(row.ts)), son sifatida emas.
    """
    raise NotImplementedError("TODO: history")
