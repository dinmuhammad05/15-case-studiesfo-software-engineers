"""Sintetik tinglash hodisalari generatori (tayyor, o'zgartirmang).

Mart 2026 uchun bir oylik "haqiqiy" tinglashlar oqimini yaratadi va
ularni hodisalar shinasi ko'rgan tartibda (arrival_time bo'yicha) yozadi.
Oqimda darsdagi barcha muammolar bor:

  - o'tkazib yuborilgan treklar (30 s dan qisqa)        -> 8.3
  - aynan 30 000 ms da to'xtagan tinglashlar             -> chegara
  - qayta yuborilgan dublikatlar (bir xil event_id)      -> 9-qadam
  - oflayn tinglashlar: kunlab kechikib keladi           -> 8.4
  - soati oldinda qurilmalar (event_time > arrival_time) -> 8.4
  - yo'qolgan hodisalar (ketma-ketlik raqamida bo'shliq)  -> 15.2 Deep
  - bot akkauntlar: 31 soniyalik treklarni aylantiradi   -> 12.2

Natija:
  data/tracks.json  — trek -> ijrochi, davomiylik
  data/users.json   — foydalanuvchi -> oylik to'lov
  data/events.jsonl — hodisalar, kelish tartibida
  data/truth.json   — to'g'ri javoblar (check.py ishlatadi; o'qimang!)

Ishga tushirish:  python gen.py        (~10-20 s, ~60 MB)
"""
import json
import math
import os
import random
import uuid
from datetime import datetime, timezone

SEED = 2026
MONTH_START = int(datetime(2026, 3, 1, tzinfo=timezone.utc).timestamp())
MONTH_END = int(datetime(2026, 4, 1, tzinfo=timezone.utc).timestamp())
CLOSE_AT = int(datetime(2026, 4, 5, tzinfo=timezone.utc).timestamp())
DAY = 86_400

N_HUMANS = 1_000
N_HEAVY = 10          # kuniga ~10 soat tinglaydigan, lekin haqiqiy odamlar
N_LOUD_BOTS = 8       # 5 kun, kuniga 20 soat
N_QUIET_BOTS = 4      # butun oy, kuniga ~1.5 soat — hajmi odamnikidek
N_TRACKS = 3_000
N_FRAUD_TRACKS = 30
PRICE = 10.0          # hamma Premium, 10 dollar/oy

P_DUP = 0.02
P_LOST = 0.003
P_SKEW = 0.003
P_OFFLINE_USER = 0.10
P_EXACT_30S = 0.01

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def zipf_weights(n, alpha=1.0):
    return [1.0 / (i + 1) ** alpha for i in range(n)]


def offline_delay(rng):
    r = rng.random()
    if r < 0.60:
        return rng.uniform(60, 3_600)
    if r < 0.95:
        return rng.uniform(3_600, DAY)
    if r < 0.99:
        return rng.uniform(DAY, 7 * DAY)
    return rng.uniform(7 * DAY, 20 * DAY)


def human_ms(rng, dur_ms):
    r = rng.random()
    if r < 0.24:
        return rng.randint(500, 5_000)
    if r < 0.40:
        return rng.randint(5_000, 29_999)
    if rng.random() < P_EXACT_30S:
        return 30_000
    if rng.random() < 0.7:
        return dur_ms
    return rng.randint(30_001, dur_ms)


def heavy_user(h):
    return h["id"] < f"u{N_HEAVY:04d}"


def main():
    rng = random.Random(SEED)
    os.makedirs(OUT, exist_ok=True)

    # --- katalog ---
    tracks = {}
    for i in range(N_TRACKS):
        tracks[f"t{i:04d}"] = {"artist": f"a{i // 10:03d}",
                               "dur_ms": rng.randint(120_000, 360_000)}
    fraud_ids = []
    for i in range(N_FRAUD_TRACKS):
        tid = f"f{i:03d}"
        tracks[tid] = {"artist": "a_fraud", "dur_ms": 31_000 + rng.randint(0, 800)}
        fraud_ids.append(tid)
    human_ids = [t for t in tracks if t.startswith("t")]
    catalog_w = zipf_weights(len(human_ids), 0.9)

    # --- foydalanuvchilar ---
    users = {}
    humans = []
    for i in range(N_HUMANS):
        uid = f"u{i:04d}"
        users[uid] = {"price": PRICE}
        heavy = i < N_HEAVY
        humans.append({
            "id": uid,
            "lam": rng.uniform(100, 250) if heavy else max(1.0, rng.lognormvariate(math.log(10), 0.6)),
            "offline": rng.random() < P_OFFLINE_USER,
            "fav": rng.choices(human_ids, weights=catalog_w, k=40),
            "devices": [f"{uid}-d{k}" for k in range(rng.choice([1, 1, 2]))],
        })
    bots = []
    for i in range(N_LOUD_BOTS + N_QUIET_BOTS):
        uid = f"u{N_HUMANS + i:04d}"
        users[uid] = {"price": PRICE}
        loud = i < N_LOUD_BOTS
        start_day = rng.randint(0, 25) if loud else 0
        bots.append({"id": uid, "loud": loud,
                     "days": range(start_day, start_day + 5) if loud else range(31),
                     "hours": 20 if loud else 1.5,
                     "dev": f"{uid}-d0"})

    # --- haqiqiy tinglashlar (qurilma bo'yicha, vaqt tartibida) ---
    plays = []  # (device, user, track, ms, real_time, is_bot, offline)
    for h in humans:
        for day in range(31):
            n = sum(1 for _ in range(int(h["lam"] * 3)) if rng.random() < 1 / 3)
            if n == 0:
                continue
            span_h = 16 if heavy_user(h) else 4
            t = MONTH_START + day * DAY + rng.randint(6, 22 - min(span_h, 16) + 1) * 3_600
            dev = rng.choice(h["devices"])
            for _ in range(n):
                tid = rng.choice(h["fav"]) if rng.random() < 0.5 else \
                    rng.choices(human_ids, weights=catalog_w)[0]
                ms = human_ms(rng, tracks[tid]["dur_ms"])
                plays.append((dev, h["id"], tid, ms, t, False,
                              h["offline"] and rng.random() < 0.5))
                t += ms // 1000 + rng.randint(1, 20)
    for b in bots:
        for day in b["days"]:
            if day > 30:
                continue
            t = MONTH_START + day * DAY + rng.randint(0, 3) * 3_600
            end = t + b["hours"] * 3_600
            while t < end:
                tid = rng.choice(fraud_ids)
                ms = min(tracks[tid]["dur_ms"], rng.randint(30_500, 32_000))
                plays.append((b["dev"], b["id"], tid, ms, t, True, False))
                t += ms // 1000 + rng.randint(0, 1)

    plays.sort(key=lambda p: (p[0], p[4]))

    # --- yetkazish: seq, kechikish, soat xatosi, dublikat, yo'qotish ---
    events = []
    truth_delivered = []
    lost = 0
    seq = {}
    for dev, uid, tid, ms, real_t, is_bot, offline in plays:
        seq[dev] = seq.get(dev, 0) + 1
        real_end = real_t + ms // 1000
        arrive = real_end + (offline_delay(rng) if offline else rng.uniform(0.5, 5))
        et = real_t
        skewed = False
        if not is_bot and rng.random() < P_SKEW:
            et = real_t + rng.randint(DAY, 3 * DAY)   # qurilma soati oldinda
            skewed = True
        ev = {"id": str(uuid.UUID(int=rng.getrandbits(128))), "u": uid, "d": dev,
              "seq": seq[dev], "t": tid, "ms": ms, "et": int(et), "at": int(arrive)}
        if rng.random() < P_LOST:
            lost += 1
            continue
        events.append(ev)
        truth_delivered.append((ev, is_bot, skewed))
        if rng.random() < P_DUP:
            dup = dict(ev)
            dup["at"] = int(arrive + rng.uniform(1, 2 * 3_600))
            events.append(dup)

    events.sort(key=lambda e: (e["at"], e["id"]))

    # --- to'g'ri javoblar ---
    bot_ids = sorted(b["id"] for b in bots)
    on_time, corrections = {}, {}
    quarantined = 0
    for ev, is_bot, skewed in truth_delivered:
        if ev["et"] > ev["at"] + 600:
            quarantined += 1
            continue
        if is_bot or ev["ms"] < 30_000:
            continue
        if not (MONTH_START <= ev["et"] < MONTH_END):
            continue
        bucket = on_time if ev["at"] < CLOSE_AT else corrections
        bucket[ev["t"]] = bucket.get(ev["t"], 0) + 1
    truth = {
        "month_start": MONTH_START, "month_end": MONTH_END, "close_at": CLOSE_AT,
        "unique_events": len(truth_delivered),
        "raw_events": len(events),
        "quarantined": quarantined,
        "bots": bot_ids,
        "on_time": on_time,
        "corrections": corrections,
        "lost": lost,
        "lost_rate": lost / (lost + len(truth_delivered)),
    }

    with open(os.path.join(OUT, "tracks.json"), "w") as f:
        json.dump(tracks, f)
    with open(os.path.join(OUT, "users.json"), "w") as f:
        json.dump(users, f)
    with open(os.path.join(OUT, "events.jsonl"), "w") as f:
        for ev in events:
            f.write(json.dumps(ev, separators=(",", ":")) + "\n")
    with open(os.path.join(OUT, "truth.json"), "w") as f:
        json.dump(truth, f)

    n_bot = sum(1 for _, b, _ in truth_delivered if b)
    print(f"hodisalar: {len(events):,} (noyob {len(truth_delivered):,}, "
          f"dublikat {len(events) - len(truth_delivered):,}, yo'qolgan {lost:,})")
    print(f"bot hodisalari: {n_bot:,}; foydalanuvchilar: {len(users):,}; "
          f"treklar: {len(tracks):,}")
    print(f"yozildi: {OUT}/")


if __name__ == "__main__":
    main()
