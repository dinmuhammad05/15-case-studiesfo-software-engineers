"""Ovoz navbati ishchisi: guruhlab qo'llash.

Navbat sifatida Redis Stream ishlatiladi (`vote_stream`).
BATCH_WINDOW_MS ni 0 qilsangiz — guruhlash o'chadi (bench uchun).
"""
import os
import time
from collections import defaultdict

import psycopg
import redis

from ranking import hot_score

REDIS = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost"))
DSN = os.environ["DATABASE_URL"]
STREAM = "vote_stream"
GROUP = "appliers"
BATCH_WINDOW_MS = int(os.environ.get("BATCH_WINDOW_MS", "100"))
LISTING_LIMIT = 1000

# Bench shu ikkita hisoblagichni o'qiydi — o'zgartirmang.
STAT_DB_WRITES = "stat:db_writes"
STAT_VOTES_APPLIED = "stat:votes_applied"


def read_batch():
    """Navbatdan bir oyna xabar o'qiydi.

    TODO:
      1. deadline = time.monotonic() + BATCH_WINDOW_MS / 1000
      2. deadline gacha XREADGROUP bilan o'qib, xabarlarni to'plang
         (block=... bilan, busy-wait qilmang)
      3. Xabarlar ro'yxatini qaytaring: [(msg_id, {"user_id":..,
         "thing_id":.., "direction":..}), ...]

    BATCH_WINDOW_MS == 0 bo'lsa bitta xabar o'qib darhol qaytaring.
    """
    raise NotImplementedError("TODO: read_batch")


def collapse(messages):
    """Bir oynadagi ovozlarni siqadi.

    Ikkita siqish bo'lishi kerak:
      1. Bir xil (user_id, thing_id) juftligi — oxirgisi g'olib.
      2. Har bir thing_id uchun ups/downs o'zgarishini yig'ish, shunda
         bitta post uchun bitta UPDATE bo'ladi.

    TODO: qaytaring (votes_to_upsert, delta_by_thing) ko'rinishida, bu yerda
    delta_by_thing = {thing_id: (d_ups, d_downs)}.

    Eslatma: ovoz o'zgarganda (+1 -> -1) delta ikki tomonlama bo'ladi —
    eski yo'nalishni bazadan o'qishingiz kerak. Sodda variant: UPSERT
    RETURNING bilan eski qiymatni olish.
    """
    raise NotImplementedError("TODO: collapse")


def apply_batch(conn, votes_to_upsert, delta_by_thing):
    """Bitta tranzaksiyada qo'llaydi va ZSET larni yangilaydi.

    TODO:
      1. votes ga toplu UPSERT (executemany yoki COPY)
      2. posts.ups/downs ni delta bilan yangilash — har bir thing uchun
         BITTA UPDATE (aylanada bittalab emas!)
      3. Yangilangan postlarni RETURNING bilan olib, hot_score hisoblang
      4. ZADD listing:<sub>:hot, keyin ZREMRANGEBYRANK bilan 1000 ga cheklang

    Har bir haqiqiy DB yozuvidan keyin REDIS.incr(STAT_DB_WRITES) qiling —
    bench shu hisoblagichni o'qiydi.
    """
    raise NotImplementedError("TODO: apply_batch")


def main():
    try:
        REDIS.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
    except redis.ResponseError:
        pass  # guruh allaqachon bor

    with psycopg.connect(DSN, autocommit=False) as conn:
        while True:
            messages = read_batch()
            if not messages:
                continue
            votes, deltas = collapse(messages)
            apply_batch(conn, votes, deltas)
            REDIS.incrby(STAT_VOTES_APPLIED, len(votes))
            REDIS.xack(STREAM, GROUP, *[m[0] for m in messages])


if __name__ == "__main__":
    main()
