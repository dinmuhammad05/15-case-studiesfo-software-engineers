"""Simulyatsiya va tekshiruv. TAYYOR — o'zgartirish shart emas.

    python bench.py                    # standart: 500 telefon, 1 soat, 5% yo'qotish
    python bench.py --drop 0.15        # yomonroq tarmoq
    python bench.py --phones 2000      # kattaroq (sekinroq)

Hech qanday server, baza yoki tarmoq kerak emas: hamma narsa bitta
jarayonda, virtual vaqt bilan (1 qadam = 1 soniya).
"""
import argparse
import random
import statistics
from collections import Counter

from common import LOST
from phone import Phone
from relay import Relay

# Telefon guruhlari — darsning 6.1-bo'limidagi A/B/C ga o'xshash,
# lekin 1 soatlik simulyatsiyaga siqilgan.
#          ulush   o'rtacha onlayn (s)   o'rtacha oflayn (s)
GROUPS = {
    "A": (0.80, 600, 20),     # deyarli doim onlayn
    "B": (0.19, 300, 600),    # tez-tez oflayn
    "C": (0.01, 120, 2400),   # ko'p vaqt oflayn
}


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class Net:
    """So'rov yoki javob `drop` ehtimoli bilan yo'qoladi."""

    def __init__(self, drop: float, rng: random.Random):
        self.drop, self.rng = drop, rng
        self.calls = 0
        self.lost = 0

    def call(self, fn, *args):
        self.calls += 1
        if self.rng.random() < self.drop:          # so'rov yo'qoldi
            self.lost += 1
            return LOST
        result = fn(*args)
        if self.rng.random() < self.drop:          # javob yo'qoldi (fn BAJARILDI!)
            self.lost += 1
            return LOST
        return result


def run(args):
    rng = random.Random(args.seed)
    clock = Clock()
    net = Net(args.drop, rng)
    phones: dict[str, Phone] = {}
    relay = Relay(net, phones, clock)

    group_of: dict[str, str] = {}
    names = list(GROUPS)
    weights = [GROUPS[g][0] for g in names]
    for i in range(args.phones):
        dev = f"d{i}"
        phones[dev] = Phone(dev, net, relay, clock)
        group_of[dev] = rng.choices(names, weights)[0]

    online = {d: rng.random() < 0.7 for d in phones}
    next_flip = {}
    for d in phones:
        _, on_mean, off_mean = GROUPS[group_of[d]]
        next_flip[d] = rng.expovariate(1 / (on_mean if online[d] else off_mean))
        if online[d]:
            relay.connect(d)

    devices = list(phones)
    L_samples, L_by_group = [], Counter()
    prev_status: dict[str, dict] = {d: {} for d in phones}
    tick_regressions = 0
    total_steps = args.seconds + args.drain

    for step in range(total_steps):
        clock.t = float(step)
        draining = step >= args.seconds

        # 1) Onlayn/oflayn almashishi (drenaj paytida hamma onlayn)
        for d in devices:
            if draining:
                if not online[d]:
                    online[d] = True
                    relay.connect(d)
                continue
            if clock.t >= next_flip[d]:
                online[d] = not online[d]
                _, on_mean, off_mean = GROUPS[group_of[d]]
                next_flip[d] = clock.t + rng.expovariate(1 / (on_mean if online[d] else off_mean))
                (relay.connect if online[d] else relay.disconnect)(d)

        # 2) Onlayn telefonlar xabar yozadi
        if not draining:
            for d in devices:
                if online[d] and rng.random() < args.rate:
                    to = rng.choice(devices)
                    if to != d:
                        phones[d].send(to, f"salom {step}")

        # 3) Qayta urinishlar
        relay.tick()
        for d in devices:
            if online[d]:
                phones[d].tick()

        # 4) O'lchov: navbat hajmi va belgilar monotonligi
        L_samples.append(relay.queue_size())
        for dev, q in relay.queue.items():
            L_by_group[group_of[dev]] += len(q)
        for d in devices:
            cur = phones[d].status
            prev = prev_status[d]
            for mid, v in cur.items():
                if v < prev.get(mid, 0):
                    tick_regressions += 1
            prev_status[d] = dict(cur)

    # ---- Tekshiruv ----------------------------------------------------------
    sent = [(p.id, mid, env.to) for p in phones.values() for mid, env in p.outbox.items()]
    shown = Counter((e.frm, e.msg_id) for p in phones.values() for e in p.inbox)
    received = {(frm, mid) for (frm, mid) in shown}
    lost = sum(1 for (frm, mid, _) in sent if (frm, mid) not in received)
    dup_shown = sum(c - 1 for c in shown.values() if c > 1)
    not_delivered_tick = sum(1 for p in phones.values() for v in p.status.values() if v < 2)

    acc, rem = relay.stats_accepted, relay.stats_removed
    T = float(total_steps)
    L = statistics.fmean(L_samples) if L_samples else 0.0
    lam = len(acc) / T if T else 0.0
    waits = [rem[k] - acc[k] for k in acc if k in rem]
    W = statistics.fmean(waits) if waits else 0.0
    little = lam * W
    little_err = abs(L - little) / little if little else float("inf")
    total_L = sum(L_by_group.values()) or 1

    print(f"\n=== {args.phones} telefon, {args.seconds} s + {args.drain} s drenaj, "
          f"yo'qotish {args.drop:.0%} ===")
    print(f"  yuborilgan xabarlar       {len(sent)}")
    print(f"  tarmoq chaqiruvlari       {net.calls}  (yo'qolgan: {net.lost})")
    print(f"  navbatga qabul qilingan   {len(acc)}")
    print()
    print(f"  lost                      {lost}")
    print(f"  dup_shown                 {dup_shown}")
    print(f"  tick_regressions          {tick_regressions}")
    print(f"  ✓✓ olmaganlar (oxirida)    {not_delivered_tick}")
    print()
    print(f"  Little: o'lchangan L      {L:.2f}")
    print(f"          lambda            {lam:.3f} xabar/s")
    print(f"          W                 {W:.1f} s  (o'rtacha navbatda turish)")
    print(f"          lambda x W        {little:.2f}   (farq {little_err:.1%})")
    if waits:
        ws = sorted(waits)
        p50, p99 = ws[len(ws) // 2], ws[int(len(ws) * 0.99)]
        print(f"          W p50 / p99       {p50:.1f} s / {p99:.1f} s")
    print()
    print("  Navbat hajmi guruhlar bo'yicha (vaqt bo'yicha o'rtacha ulush):")
    counts = Counter(group_of.values())
    for g in names:
        print(f"    {g}: telefonlarning {counts[g] / args.phones:5.1%}  ->  "
              f"navbatning {L_by_group[g] / total_L:5.1%}")

    print("\n--- tekshiruv ---")
    checks = [
        ("lost == 0", lost == 0, "xabar yo'qoldi: relay ✓✓ dan oldin o'chiryaptimi?"),
        ("dup_shown == 0", dup_shown == 0, "on_deliver dublikatni tanimayapti"),
        ("tick_regressions == 0", tick_regressions == 0, "belgilar orqaga ketdi: max() ishlating"),
        ("hamma ✓✓ oldi", not_delivered_tick == 0,
         "✓✓ yo'qolyapti, qayta urinilmayapti, YOKI kechikkan ✓ uni 1 ga tushiryapti "
         "(submit javobi ✓✓ dan keyin kelishi mumkin — max() ishlating)"),
        ("Little farqi <= 20%", little_err <= 0.20,
         "_accepted()/_removed() chaqirilmayapti yoki noto'g'ri joyda"),
    ]
    ok = True
    for name, passed, hint in checks:
        print(f"  {'OK ' if passed else 'XATO'}  {name}" + ("" if passed else f"  — {hint}"))
        ok &= passed
    print("\n" + ("Hammasi o'tdi." if ok else "Tuzatish kerak."))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phones", type=int, default=500)
    ap.add_argument("--seconds", type=int, default=3600)
    ap.add_argument("--drain", type=int, default=300)
    ap.add_argument("--drop", type=float, default=0.05)
    ap.add_argument("--rate", type=float, default=0.01, help="onlayn telefon boshiga xabar/s")
    ap.add_argument("--seed", type=int, default=7)
    raise SystemExit(0 if run(ap.parse_args()) else 1)
