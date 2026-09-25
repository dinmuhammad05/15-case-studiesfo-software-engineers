"""Yuk testi, xaos va tekshiruv hisoboti. TAYYOR — o'zgartirish shart emas.

    python bench.py --clients 5000 --rate 100 --seconds 120 --jitter on
    python bench.py --clients 5000 --rate 100 --seconds 120 --jitter off
"""
import argparse
import asyncio
import json
import os
import random
import statistics
import time
import uuid

import httpx

import chaos
from client import Client

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
GATEWAYS = os.environ.get("GATEWAYS", "ws://localhost:8001,ws://localhost:8002").split(",")
CHANNELS = ["C1", "C2", "C3"]

sent: dict[str, dict] = {}          # client_msg_id -> {channel, t_sent}


async def sender(rate: int, seconds: int, stop: asyncio.Event):
    """Sekundiga `rate` ta xabar yuboradi."""
    interval = 1.0 / rate
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as http:
        next_at = time.perf_counter()
        while not stop.is_set():
            next_at += interval
            cmid = str(uuid.uuid4())
            ch = random.choice(CHANNELS)
            sent[cmid] = {"channel": ch, "t": time.perf_counter()}
            try:
                await http.post("/send", json={
                    "channel": ch, "user_id": "bench",
                    "text": cmid, "client_msg_id": cmid,
                })
            except httpx.HTTPError:
                pass
            sleep = next_at - time.perf_counter()
            if sleep > 0:
                await asyncio.sleep(sleep)


def report(clients: list[Client], args, outage_at: float, elapsed: float):
    by_channel: dict[str, set] = {c: set() for c in CHANNELS}
    for cmid, meta in sent.items():
        by_channel[meta["channel"]].add(cmid)

    lost = 0
    dup_delivered = 0
    per_client_missing = []
    for c in clients:
        missing = 0
        for ch in c.channels:
            missing += len(by_channel[ch] - c.seen[ch])
        per_client_missing.append(missing)
        lost += missing
        dup_delivered += c.dup_delivered

    reconnects = sum(c.reconnects for c in clients)
    # Qayta ulanish cho'qqisi: eng band 1 soniyalik oyna
    peak = 0
    reconnect_marks = [t for c in clients for t in c.reconnect_times]
    if reconnect_marks:
        marks = sorted(reconnect_marks)
        j = 0
        for i, t in enumerate(marks):
            while marks[i] - marks[j] > 1.0:
                j += 1
            peak = max(peak, i - j + 1)

    result = {
        "jitter": args.jitter,
        "clients": args.clients,
        "messages_sent": len(sent),
        "lost": lost,
        "lost_clients": sum(1 for m in per_client_missing if m > 0),
        "dup_delivered": dup_delivered,
        "reconnects": reconnects,
        "reconnect_peak_per_s": peak,
        "catchup_avg": round(statistics.fmean(
            [len(c.seen[ch]) for c in clients for ch in c.channels]) or 0, 3),
        "outage_at_s": round(outage_at, 1),
        "elapsed_s": round(elapsed, 1),
    }

    path = f"bench_result_{args.jitter}.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n=== jitter={args.jitter} ===")
    for k, v in result.items():
        print(f"  {k:22} {v}")

    print("\n--- tekshiruv ---")
    print(f"  lost == 0                {'OK' if lost == 0 else f'XATO: {lost} ta xabar yo`qoldi'}")
    print(f"  dup_delivered == 0       {'OK' if dup_delivered == 0 else f'XATO: {dup_delivered} dublikat ko`rsatildi'}")

    other = f"bench_result_{'off' if args.jitter == 'on' else 'on'}.json"
    if os.path.exists(other):
        with open(other) as f:
            o = json.load(f)
        on, off = (result, o) if args.jitter == "on" else (o, result)
        a, b = on["reconnect_peak_per_s"], off["reconnect_peak_per_s"]
        ratio = round(b / a, 1) if a else "-"
        print(f"\n  qayta ulanish cho'qqisi:  on={a}/s  off={b}/s  nisbat={ratio}")
        if isinstance(ratio, float):
            print("  " + ("OK (>= 10x)" if ratio >= 10
                          else "YETARLI EMAS — reconnect_delay() to'liq jitter emas"))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clients", type=int, default=5000)
    ap.add_argument("--rate", type=int, default=100)
    ap.add_argument("--seconds", type=int, default=120)
    ap.add_argument("--jitter", choices=["on", "off"], default="on")
    ap.add_argument("--kill-port", type=int, default=8001)
    args = ap.parse_args()

    os.environ["JITTER"] = args.jitter

    clients = [
        Client(f"u{i}", random.sample(CHANNELS, 2), GATEWAYS)
        for i in range(args.clients)
    ]
    stop = asyncio.Event()
    t0 = time.perf_counter()

    tasks = [asyncio.create_task(c.run()) for c in clients]
    tasks.append(asyncio.create_task(sender(args.rate, args.seconds, stop)))

    # Test o'rtasida gateway'ni o'ldiramiz
    await asyncio.sleep(args.seconds / 2)
    outage_at = time.perf_counter() - t0
    print(f"[{outage_at:.1f}s] gateway {args.kill_port} o'ldirilyapti…")
    await asyncio.to_thread(chaos.outage, args.kill_port, 10.0)

    await asyncio.sleep(args.seconds / 2)
    stop.set()
    await asyncio.sleep(5)  # quvib yetish tugasin
    for t in tasks:
        t.cancel()

    report(clients, args, outage_at, time.perf_counter() - t0)


if __name__ == "__main__":
    asyncio.run(main())
