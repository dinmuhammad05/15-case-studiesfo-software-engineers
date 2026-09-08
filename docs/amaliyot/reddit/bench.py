"""Yuk testi va o'lchov. TAYYOR — o'zgartirish shart emas.

Ishlatish:
    python bench.py --rate 2000 --seconds 60 --batching on
    python bench.py --rate 2000 --seconds 60 --batching off

Chiqish: rejimlar taqqoslash jadvali va bench_result_<rejim>.json
"""
import argparse
import json
import os
import random
import statistics
import threading
import time

import redis
import requests

REDIS = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost"))
BASE = os.environ.get("API_BASE", "http://localhost:8000")
SUB = os.environ.get("BENCH_SUB", "system_design")

STAT_DB_WRITES = "stat:db_writes"
STAT_VOTES_APPLIED = "stat:votes_applied"

_lat_vote, _lat_list = [], []
_lock = threading.Lock()


def _post_votes(rate, seconds, thing_ids, stop):
    interval = 1.0 / rate
    session = requests.Session()
    next_at = time.perf_counter()
    while not stop.is_set():
        next_at += interval
        body = {
            "user_id": random.randint(1, 200_000),
            "thing_id": random.choice(thing_ids),
            "direction": random.choice([1, 1, 1, -1]),
        }
        t0 = time.perf_counter()
        try:
            session.post(f"{BASE}/vote", json=body, timeout=5)
        except requests.RequestException:
            pass
        dt = (time.perf_counter() - t0) * 1000
        with _lock:
            _lat_vote.append(dt)
        sleep = next_at - time.perf_counter()
        if sleep > 0:
            time.sleep(sleep)


def _read_listing(stop):
    session = requests.Session()
    while not stop.is_set():
        t0 = time.perf_counter()
        try:
            session.get(f"{BASE}/r/{SUB}/hot?limit=25", timeout=5)
        except requests.RequestException:
            pass
        with _lock:
            _lat_list.append((time.perf_counter() - t0) * 1000)
        time.sleep(0.02)


def p(values, q):
    if not values:
        return 0.0
    return round(statistics.quantiles(values, n=100)[q - 1], 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=int, default=2000, help="ovoz/s")
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--batching", choices=["on", "off"], default="on")
    ap.add_argument("--writers", type=int, default=16)
    ap.add_argument("--readers", type=int, default=8)
    args = ap.parse_args()

    thing_ids = [int(x) for x in REDIS.zrevrange(f"listing:{SUB}:hot", 0, 499)] or list(
        range(1, 501)
    )

    REDIS.set(STAT_DB_WRITES, 0)
    REDIS.set(STAT_VOTES_APPLIED, 0)

    stop = threading.Event()
    threads = [
        threading.Thread(
            target=_post_votes,
            args=(args.rate / args.writers, args.seconds, thing_ids, stop),
            daemon=True,
        )
        for _ in range(args.writers)
    ] + [threading.Thread(target=_read_listing, args=(stop,), daemon=True)
         for _ in range(args.readers)]

    t0 = time.perf_counter()
    for t in threads:
        t.start()
    time.sleep(args.seconds)
    stop.set()
    time.sleep(2)  # ishchi qarzni so'rib olsin
    elapsed = time.perf_counter() - t0

    db_writes = int(REDIS.get(STAT_DB_WRITES) or 0)
    applied = int(REDIS.get(STAT_VOTES_APPLIED) or 0)
    sent = len(_lat_vote)

    result = {
        "batching": args.batching,
        "target_rate": args.rate,
        "votes_sent": sent,
        "votes_applied": applied,
        "apply_ratio": round(applied / sent, 4) if sent else 0,
        "db_writes_per_s": round(db_writes / elapsed, 1),
        "votes_per_db_write": round(applied / db_writes, 1) if db_writes else 0,
        "vote_p50_ms": p(_lat_vote, 50),
        "vote_p99_ms": p(_lat_vote, 99),
        "listing_p50_ms": p(_lat_list, 50),
        "listing_p99_ms": p(_lat_list, 99),
    }

    path = f"bench_result_{args.batching}.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n=== batching={args.batching} ===")
    for k, v in result.items():
        print(f"  {k:22} {v}")

    other = f"bench_result_{'off' if args.batching == 'on' else 'on'}.json"
    if os.path.exists(other):
        with open(other) as f:
            o = json.load(f)
        on, off = (result, o) if args.batching == "on" else (o, result)
        print("\n=== taqqoslash ===")
        print(f"  {'ko`rsatkich':22} {'on':>10} {'off':>10} {'nisbat':>10}")
        for k in ("db_writes_per_s", "listing_p99_ms", "vote_p99_ms", "apply_ratio"):
            a, b = on.get(k, 0), off.get(k, 0)
            ratio = round(b / a, 1) if a else "-"
            print(f"  {k:22} {a:>10} {b:>10} {str(ratio):>10}")
        gain = off["db_writes_per_s"] / on["db_writes_per_s"] if on["db_writes_per_s"] else 0
        print(f"\n  DB yozuvi tejash: {gain:.1f}x", end="  ")
        print("OK (>= 20x)" if gain >= 20 else "YETARLI EMAS — collapse() ni tekshiring")


if __name__ == "__main__":
    main()
