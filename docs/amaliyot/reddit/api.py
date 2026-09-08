"""API: ovoz qabul qilish va ro'yxat berish."""
import os
import time

import psycopg
import redis
from fastapi import FastAPI
from pydantic import BaseModel

REDIS = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost"))
DSN = os.environ["DATABASE_URL"]
STREAM = "vote_stream"

app = FastAPI()


class Vote(BaseModel):
    user_id: int
    thing_id: int
    direction: int  # -1, 0, 1


@app.post("/vote", status_code=202)
def vote(v: Vote):
    """Ovozni navbatga qo'yadi va darhol qaytadi.

    TODO:
      1. direction ni tekshiring (-1, 0, 1)
      2. REDIS.xadd(STREAM, {...}) — vaqt belgisi bilan
      3. 202 qaytaring

    MUHIM: bu yerda bazaga TEGMANG. Butun mashqning ma'nosi shundaki,
    yozish yo'li navbatdan o'tadi.
    """
    raise NotImplementedError("TODO: vote")


@app.get("/r/{sub}/hot")
def hot(sub: str, limit: int = 25, offset: int = 0):
    """Ro'yxatni ZSET dan o'qiydi va postlarni BATCH bilan oladi.

    TODO:
      1. ids = REDIS.zrevrange(f"listing:{sub}:hot", offset, offset+limit-1)
      2. Postlarni BITTA so'rov bilan oling:
         SELECT ... WHERE id = ANY(%s)
      3. ZSET tartibini saqlab qaytaring (SQL tartibi boshqa!)

    Bu yerdagi eng ko'p uchraydigan xato — har bir id uchun alohida
    so'rov (N+1). U funksional testda ko'rinmaydi, bench da ko'rinadi.
    """
    raise NotImplementedError("TODO: hot")


@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": time.time()}
