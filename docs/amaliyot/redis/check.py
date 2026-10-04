"""skiplist.py, hll.py va keyspace.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

To'rt qism:
  1. Skiplist: sodda model bilan solishtirish (fuzz), ichki tuzilma
     (ko'rsatkichlar, span'lar, backward, darajalar taqsimoti), ZSET.
  2. HyperLogLog: registrlar aniq qiymati, aniqlik, birlashtirish.
  3. Kalit maydoni: passiv va faol ekspirasiya, siqib chiqarish siyosatlari,
     namunali LRU sifati.
  4. Bir o'yin kuni: uchala tuzilma birga — reyting, noyob o'yinchilar,
     sessiyalar.
  5. Tezlik.
"""
import bisect
import math
import random
import sys
import time
import traceback
from collections import OrderedDict

from model import MAX_LEVEL, P, Node, Zipf, stable_hash  # noqa: F401

import hll as hll_mod
import keyspace as ks_mod
import skiplist as sl_mod

results = []


class TooSlow(Exception):
    pass


def guard(t0, limit, what):
    if time.time() - t0 > limit:
        raise TooSlow(f"{what}: {limit} soniyadan oshdi — amallar O(log N) / O(1) emas")


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))


def attempt(fn, *a, **kw):
    try:
        return fn(*a, **kw), None
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


# ============================================================ 1. skiplist
class NaiveZ:
    """Sekin, lekin aniq: (score, member) juftlari tartiblangan ro'yxatda."""

    def __init__(self):
        self.items = []

    def insert(self, m, s):
        bisect.insort(self.items, (s, m))

    def delete(self, m, s):
        i = bisect.bisect_left(self.items, (s, m))
        if i < len(self.items) and self.items[i] == (s, m):
            self.items.pop(i)
            return True
        return False

    def rank(self, m, s):
        i = bisect.bisect_left(self.items, (s, m))
        return i if i < len(self.items) and self.items[i] == (s, m) else None

    def by_rank(self, a, b):
        n = len(self.items)
        if a < 0:
            a += n
        if b < 0:
            b += n
        a = max(a, 0)
        if a > b or a >= n:
            return []
        b = min(b, n - 1)
        return [(m, s) for s, m in self.items[a:b + 1]]

    def range_by_score(self, lo, hi, offset=0, count=None):
        out = [(m, s) for s, m in self.items if lo <= s <= hi][offset:]
        return out if count is None else out[:count]


def invariants(sl):
    """Skiplistning ichki tuzilmasini tekshiradi. Xato matnini yoki None qaytaradi."""
    h = sl.header
    if not isinstance(h, Node) or len(h.forward) != MAX_LEVEL:
        return "header — MAX_LEVEL darajali Node bo'lishi kerak"
    lvl0 = []
    x = h.forward[0]
    prev = None
    while x is not None:
        if x.backward is not prev:
            return f"backward noto'g'ri: {x.member}"
        lvl0.append(x)
        prev, x = x, x.forward[0]
    if len(lvl0) != len(sl):
        return f"0-darajada {len(lvl0)} tugun, len() = {len(sl)}"
    if sl.tail is not (lvl0[-1] if lvl0 else None):
        return "tail oxirgi tugunga ko'rsatmayapti"
    keys = [(n.score, n.member) for n in lvl0]
    if keys != sorted(keys):
        return "0-daraja (score, member) bo'yicha tartiblanmagan"
    pos = {id(n): i + 1 for i, n in enumerate(lvl0)}
    pos[id(h)] = 0
    top = max([len(n.forward) for n in lvl0] + [1])
    if sl.level != top:
        return f"sl.level = {sl.level}, eng baland tugun darajasi {top}"
    for i in range(MAX_LEVEL):
        x = h
        while True:
            nxt = x.forward[i]
            want = (pos[id(nxt)] if nxt is not None else len(lvl0) + 1) - pos[id(x)]
            if nxt is None:
                break
            if i >= len(nxt.forward):
                return f"{i}-darajadagi ko'rsatkich past darajali tugunga"
            if x.span[i] != want:
                return f"{i}-darajada span {x.span[i]}, kutilgan {want} ({x.member} -> {nxt.member})"
            if pos[id(nxt)] <= pos[id(x)]:
                return f"{i}-darajada ko'rsatkich orqaga"
            x = nxt
    for i in range(1, MAX_LEVEL):
        cnt_i = sum(1 for n in lvl0 if len(n.forward) > i)
        x, seen = h.forward[i], 0
        while x is not None:
            seen += 1
            x = x.forward[i]
        if seen != cnt_i:
            return f"{i}-darajada {cnt_i} tugun bor, lekin zanjirda {seen} ta"
    return None


def part_skiplist():
    print("1. Skiplist")
    errs = []
    for seed in range(40):
        rng = random.Random(seed)
        sl, nv = sl_mod.SkipList(seed=seed), NaiveZ()
        live = {}
        for step in range(300):
            op = rng.random()
            if op < 0.5 or not live:
                m = f"m{rng.randrange(80)}"
                if m in live:
                    continue
                s = float(rng.randrange(20))
                sl.insert(m, s)
                nv.insert(m, s)
                live[m] = s
            elif op < 0.7:
                m = rng.choice(list(live))
                s = live.pop(m)
                if sl.delete(m, s) is not True or not nv.delete(m, s):
                    errs.append(f"seed {seed}: delete({m}) True qaytarishi kerak")
                if sl.delete(m, s) is not False:
                    errs.append(f"seed {seed}: ikkinchi delete False qaytarishi kerak")
            elif op < 0.8:
                m = rng.choice(list(live))
                got, e = attempt(sl.rank, m, live[m])
                if got != nv.rank(m, live[m]):
                    errs.append(f"seed {seed}: rank({m}) = {e or got}, kutilgan {nv.rank(m, live[m])}")
                if sl.rank(m, live[m] + 0.5) is not None:
                    errs.append(f"seed {seed}: mavjud bo'lmagan juftlik uchun rank None bo'lishi kerak")
            elif op < 0.9:
                a, b = rng.randint(-15, 15), rng.randint(-15, 25)
                got, e = attempt(sl.by_rank, a, b)
                if got != nv.by_rank(a, b):
                    errs.append(f"seed {seed}: by_rank({a}, {b}) = {e or got}, kutilgan {nv.by_rank(a, b)}")
            else:
                lo = rng.randrange(20)
                hi = lo + rng.randrange(8)
                off, cnt = rng.randrange(3), rng.choice([None, 1, 3])
                got, e = attempt(sl.range_by_score, lo, hi, off, cnt)
                if got != nv.range_by_score(lo, hi, off, cnt):
                    errs.append(f"seed {seed}: range_by_score({lo}, {hi}, {off}, {cnt}) = {e or got}")
            if errs:
                break
            if step % 25 == 0:
                bad = invariants(sl)
                if bad:
                    errs.append(f"seed {seed}, qadam {step}: {bad}")
                    break
        if errs:
            break
    check("fuzz: 40 x 300 amal — sodda model bilan bir xil natija", not errs, errs[0] if errs else "")

    errs = []
    sl = sl_mod.SkipList(seed=7)
    rng = random.Random(7)
    ms = [f"u{i}" for i in range(20000)]
    rng.shuffle(ms)
    t0 = time.time()
    for i, m in enumerate(ms):
        sl.insert(m, float(int(m[1:]) % 997))
        if i % 1000 == 0:
            guard(t0, 10, "20 000 ta insert")
    bad = invariants(sl)
    if bad:
        errs.append(bad)
    lv = [len(n.forward) for n in iter_nodes(sl)]
    frac2 = sum(1 for v in lv if v >= 2) / len(lv)
    frac3 = sum(1 for v in lv if v >= 3) / len(lv)
    if not 0.22 <= frac2 <= 0.28 or not 0.045 <= frac3 <= 0.08:
        errs.append(f"darajalar taqsimoti: >=2 — {frac2:.3f} (kutilgan ~0.25), >=3 — {frac3:.3f} (~0.0625)")
    if max(lv) > 16:
        errs.append(f"20 000 tugunda {max(lv)}-daraja — juda baland")
    check(f"tuzilma: 20 000 tugun, span'lar, backward, darajalar ~P=0.25 (>=2: {frac2:.3f})",
          not errs, "; ".join(errs))

    errs = []
    for i in range(0, 20000, 997):
        m = ms[i]
        s = float(int(m[1:]) % 997)
        hops = count_hops(sl, m, s)
        if hops > 400:
            errs.append(f"rank({m}) {hops} ta qadam — O(log N) emas")
            break
    check("rank: 20 000 elementda har qidiruv ≤ 400 ko'rsatkich o'qishi (O(log N))", not errs, "; ".join(errs))

    errs = []
    z = sl_mod.ZSet(seed=1)
    z.zadd("ali", 10)
    z.zadd("vali", 20)
    z.zadd("guli", 15)
    if z.zrange(0, -1) != [("ali", 10), ("guli", 15), ("vali", 20)]:
        errs.append(f"zrange: {z.zrange(0, -1)}")
    z.zadd("ali", 30)
    if z.zrank("ali") != 2 or z.zscore("ali") != 30:
        errs.append("zadd mavjud a'zoning ballini yangilashi kerak")
    if z.zincrby("vali", 15) != 35 or z.zrevrange(0, 0) != [("vali", 35)]:
        errs.append("zincrby / zrevrange")
    if z.zrangebyscore(15, 30) != [("guli", 15), ("ali", 30)]:
        errs.append(f"zrangebyscore: {z.zrangebyscore(15, 30)}")
    if not z.zrem("guli") or z.zrem("guli") or z.zcard() != 2:
        errs.append("zrem")
    check("ZSET (tayyor qobiq) skiplist ustida ishlaydi", not errs, "; ".join(errs))


def iter_nodes(sl):
    x = sl.header.forward[0]
    while x is not None:
        yield x
        x = x.forward[0]


def count_hops(sl, member, score):
    """Instrumentatsiya: forward ko'rsatkichlarni o'qishlar sonini sanaydi."""
    counter = [0]

    class Spy(list):
        def __getitem__(self, i):
            counter[0] += 1
            return list.__getitem__(self, i)

    saved = []
    for n in [sl.header] + list(iter_nodes(sl)):
        saved.append((n, n.forward))
        n.forward = Spy(n.forward)
    try:
        sl.rank(member, score)
    finally:
        for n, f in saved:
            n.forward = f
    return counter[0]


# ============================================================ 2. HLL
def part_hll():
    print("2. HyperLogLog")
    errs = []
    M = hll_mod.M
    if M != 16384:
        errs.append(f"M = {M}, kutilgan 16384")
    cases = [(0b1, (1, 51)), (1 << 14, (0, 1)), (0b11 << 14 | 5, (5, 1)), (0b100 << 14 | 7, (7, 3)),
             ((1 << 63) | 9, (9, 50)), (16383, (16383, 51)), ((0b1000 << 14) | 16383, (16383, 4))]
    for h, want in cases:
        got, e = attempt(hll_mod.index_rank, h)
        if got != want:
            errs.append(f"index_rank({h:#x}) = {e or got}, kutilgan {want}")
    check("index_rank: quyi 14 bit — registr, qolgan 50 bitdagi oxirgi nollar + 1", not errs, "; ".join(errs[:3]))

    errs = []
    h = hll_mod.HLL()
    items = [f"x{i}" for i in range(3000)]
    want = bytearray(M)
    for it in items:
        idx, r = ref_index_rank(stable_hash("hll", it))
        want[idx] = max(want[idx], r)
        h.add(it)
    if bytes(h.reg) != bytes(want):
        diff = sum(1 for a, b in zip(h.reg, want) if a != b)
        errs.append(f"{diff} ta registr noto'g'ri (xesh: stable_hash('hll', element))")
    before = bytes(h.reg)
    for it in items[:500]:
        if h.add(it):
            errs.append("takroriy element registrni o'zgartirmasligi va False qaytarishi kerak")
            break
    if bytes(h.reg) != before:
        errs.append("takroriy element registrlarni o'zgartirdi")
    check("registrlar: 3 000 element — har registr aniq maksimum", not errs, "; ".join(errs[:2]))

    errs, rep = [], []
    worst_mid = 0.0
    for n in [50, 500, 5000, 20000, 41000, 120000, 300000]:
        e_all = []
        for seed in range(2):
            hh = hll_mod.HLL()
            for i in range(n):
                hh.add(f"s{seed}:u{i}")
            c, err = attempt(hh.count)
            if err:
                errs.append(err)
                break
            e_all.append((c - n) / n)
        if errs:
            break
        worst = max(abs(x) for x in e_all)
        rep.append(f"{n}: {worst:.2%}")
        lim = 0.05 if 30000 <= n <= 70000 else 0.025
        if 30000 <= n <= 70000:
            worst_mid = max(worst_mid, worst)
        if worst > lim:
            errs.append(f"n={n}: xato {worst:.2%} > {lim:.1%}")
    print("      eng katta nisbiy xato: " + ", ".join(rep))
    check("aniqlik: kichik va katta n da ≤ 2.5%, o'tish oralig'ida (30-70 ming) ≤ 5%", not errs, "; ".join(errs))

    errs = []
    a, b, u = hll_mod.HLL(), hll_mod.HLL(), hll_mod.HLL()
    for i in range(40000):
        a.add(f"a{i}")
        u.add(f"a{i}")
    for i in range(20000, 70000):
        b.add(f"a{i}")
        u.add(f"a{i}")
    a.merge(b)
    if bytes(a.reg) != bytes(u.reg):
        errs.append("merge — registrlar bo'yicha maksimum bo'lishi kerak")
    if abs(a.count() - 70000) / 70000 > 0.05:
        errs.append(f"birlashma: {a.count()}, haqiqiy 70 000")
    check("merge: ikki kunlik HLL birlashmasi = umumiy HLL (registrlar aynan bir xil)", not errs, "; ".join(errs))


def ref_index_rank(h):
    idx = h & 16383
    w = h >> 14
    if w == 0:
        return idx, 51
    r = 1
    while not w & 1:
        w >>= 1
        r += 1
    return idx, r


# ============================================================ 3. kalit maydoni
def part_keyspace():
    print("3. Kalit maydoni")
    errs = []
    K = ks_mod.Keyspace
    s = K(100, "allkeys-lru", seed=1)
    s.set("a", 1, 0.0, ttl=10)
    s.set("b", 2, 0.0)
    if s.get("a", 9.99) != 1 or s.ttl("a", 4.0) != 6 or s.ttl("b", 4.0) != -1 or s.ttl("c", 4.0) != -2:
        errs.append("get/ttl: TTL ichida qiymat, ttl() — qolgan vaqt, -1 (TTL yo'q), -2 (kalit yo'q)")
    if s.get("a", 10.0) is not None or len(s) != 1:
        errs.append("passiv ekspirasiya: muddat tugagan kalit get da o'chirilishi kerak (now >= muddat)")
    s.set("b", 3, 11.0, ttl=5)
    s.set("b", 4, 12.0)
    if s.get("b", 100.0) != 4:
        errs.append("TTL siz SET kalitning eski TTL ini olib tashlashi kerak")
    s2 = K(3, "noeviction", seed=1)
    for k in "xyz":
        s2.set(k, 1, 0.0)
    _, e = attempt(s2.set, "w", 1, 1.0)
    if e is None or "OOMError" not in e:
        errs.append("noeviction: to'lganda OOMError")
    s2.set("x", 5, 1.0)
    if s2.get("x", 1.0) != 5:
        errs.append("mavjud kalitni yangilash siqib chiqarishni talab qilmaydi")
    s3 = K(4, "volatile-lru", seed=2)
    s3.set("p1", 1, 0.0)
    s3.set("p2", 1, 0.0)
    s3.set("t1", 1, 0.0, ttl=100)
    s3.set("t2", 1, 0.0, ttl=100)
    s3.set("n1", 1, 1.0, ttl=100)
    s3.set("n2", 1, 1.0, ttl=100)
    if s3.get("p1", 2.0) is None or s3.get("p2", 2.0) is None:
        errs.append("volatile-lru TTL siz kalitlarni hech qachon chiqarmasligi kerak")
    s4 = K(2, "volatile-lru", seed=2)
    s4.set("p1", 1, 0.0)
    s4.set("p2", 1, 0.0)
    _, e = attempt(s4.set, "p3", 1, 0.0)
    if e is None or "OOMError" not in e:
        errs.append("volatile-*: TTL li kalit qolmasa — OOMError")
    check("birlik: get/ttl, passiv ekspirasiya, SET TTL ni almashtiradi, noeviction, volatile-lru",
          not errs, "; ".join(errs[:3]))

    # faol ekspirasiya
    errs = []
    s = K(10**9, "noeviction", seed=5, cycle_budget=400)
    for i in range(60000):
        s.set(f"k{i}", 1, 0.0, ttl=(10 if i % 2 == 0 else 10**6))
    for i in range(100000):
        s.set(f"p{i}", 1, 0.0)
    over = 0
    t = 10.0
    t0 = time.time()
    for c in range(600):
        guard(t0, 20, "faol ekspirasiya")
        checked = s.active_expire_cycle(t)
        if checked > 400 + 20:
            over += 1
        t += 0.1
    stale = sum(1 for e in s.expires.values() if e <= 10.0)
    ttl_total = len(s.expires)
    frac = stale / max(ttl_total, 1)
    if over:
        errs.append(f"{over} siklda budjetdan ko'p kalit tekshirildi")
    if frac > 0.27:
        errs.append(f"60 soniyadan keyin TTL li kalitlarning {frac:.1%} i muddati o'tgan holda turibdi (≤ 27% bo'lishi kerak)")
    calm = s.active_expire_cycle(t)
    if calm > 60:
        errs.append(f"muddati o'tganlar kam bo'lsa ham sikl {calm} kalitni tekshirdi — 25% qoidasi ishlamayapti")
    print(f"      60 s dan keyin: muddati o'tgan, lekin xotirada — {frac:.1%}; tinch siklda tekshirildi {calm}")
    check("faol ekspirasiya: 20 lik namuna, 25% qoidasi, budjet; TTL siz 100 000 kalit xalaqit bermaydi",
          not errs, "; ".join(errs))

    # LRU sifati
    N, CAP, R = 50000, 5000, 200000
    z = Zipf(N, 1.0, seed=1)
    trace = [z.sample() for _ in range(R)]
    c, hit = OrderedDict(), 0
    for k in trace:
        if k in c:
            c.move_to_end(k)
            hit += 1
        else:
            c[k] = 1
            if len(c) > CAP:
                c.popitem(last=False)
    true_lru = hit / R

    def run(policy, samples):
        s = K(CAP, policy, samples, seed=3)
        h, t = 0, 0.0
        t0 = time.time()
        for i, k in enumerate(trace):
            if i % 5000 == 0:
                guard(t0, 15, f"{policy} simulyatsiyasi")
            t += 0.001
            if s.get(k, t) is not None:
                h += 1
            else:
                s.set(k, 1, t)
            if len(s) > CAP:
                return -1.0
        return h / R

    rnd, l5, l10 = run("allkeys-random", 5), run("allkeys-lru", 5), run("allkeys-lru", 10)
    print(f"      urish darajasi: haqiqiy LRU {true_lru:.3f}, random {rnd:.3f}, LRU(5) {l5:.3f}, LRU(10) {l10:.3f}")
    check("namunali LRU: 5 namuna random'dan ≥ 2 punkt yaxshi, 10 namuna haqiqiy LRU'dan ≤ 0.5 punkt farq",
          l5 >= rnd + 0.02 and abs(l10 - true_lru) <= 0.005 and rnd > 0,
          "sig'imdan oshib ketdi" if min(rnd, l5, l10) < 0 else
          f"random {rnd:.3f}, LRU(5) {l5:.3f}, LRU(10) {l10:.3f}, haqiqiy {true_lru:.3f}")


# ============================================================ 4. bir o'yin kuni
def part_day():
    print("4. Bir o'yin kuni: reyting, noyob o'yinchilar, sessiyalar")
    rng = random.Random(42)
    z = sl_mod.ZSet(seed=9)
    exact = {}
    week = hll_mod.HLL()
    days = []
    exact_week = set()
    sess = ks_mod.Keyspace(20000, "volatile-lru", 5, seed=4)
    zipf = Zipf(60000, 0.8, seed=6)
    wrong_rank = stale_served = 0
    set_at = {}
    t = 0.0
    t_start = time.time()
    for day in range(3):
        dh = hll_mod.HLL()
        exact_day = set()
        for i in range(60000):
            if i % 2000 == 0:
                guard(t_start, 40, "o'yin kuni")
            t += 0.5
            p = f"p{zipf.sample() + day * 7000}"
            pts = rng.randrange(1, 50)
            z.zincrby(p, pts)
            exact[p] = exact.get(p, 0) + pts
            dh.add(p)
            exact_day.add(p)
            exact_week.add(p)
            v = sess.get(p, t)
            if v is not None and (v != p or t - set_at[p] >= 1800):
                stale_served += 1
            if v is None:
                sess.set(p, p, t, ttl=1800)
                set_at[p] = t
            if rng.random() < 0.0005:                  # tekshiruv: aniq javob saralash bilan
                rev = sorted(exact.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
                pos = next(i for i, (m, _) in enumerate(rev) if m == p)
                if z.zrevrange(0, 9) != [(m, float(sc)) for m, sc in rev[:10]] or \
                        z.zcard() - 1 - z.zrank(p) != pos:
                    wrong_rank += 1
        days.append((dh, len(exact_day)))
        week.merge(dh)
    day_err = max(abs(h.count() - n) / n for h, n in days)
    week_err = abs(week.count() - len(exact_week)) / len(exact_week)
    print(f"      3 kun: {len(exact)} o'yinchi; HLL kunlik xato ≤ {day_err:.2%}, haftalik {week_err:.2%}; "
          f"sessiyalar: {len(sess)} (chegara 20 000), siqib chiqarildi {sess.evicted}")
    check("reyting: top-10 va 'mening o'rnim' har tekshiruvda aniq javob bilan bir xil", wrong_rank == 0,
          f"{wrong_rank} ta noto'g'ri javob")
    check(f"noyob o'yinchilar: kunlik va birlashtirilgan haftalik HLL ≤ 2% xato ({max(day_err, week_err):.2%})",
          max(day_err, week_err) <= 0.02)
    check("sessiyalar: chegara buzilmaydi, muddati o'tgan sessiya qaytmaydi",
          len(sess) <= 20000 and stale_served == 0 and sess.evicted > 0,
          f"len={len(sess)}, eskirgan={stale_served}, evicted={sess.evicted}")


# ============================================================ 5. tezlik
def part_speed():
    print("5. Tezlik")
    t0 = time.time()
    sl = sl_mod.SkipList(seed=3)
    rng = random.Random(3)
    for i in range(60000):
        sl.insert(f"u{i}", float(rng.randrange(10**6)))
        if i % 2000 == 0:
            guard(t0, 10, "skiplist insert")
    for i in range(0, 60000, 3):
        sl.by_rank(i, i + 5)
        if i % 3000 == 0:
            guard(t0, 10, "skiplist by_rank")
    t1 = time.time()
    s = ks_mod.Keyspace(100000, "allkeys-lru", 5, seed=1)
    z = Zipf(400000, 0.9, seed=2)
    t, n = 0.0, 0
    for _ in range(300000):
        t += 0.001
        k = z.sample()
        if s.get(k, t) is None:
            s.set(k, 1, t, ttl=60 if k % 3 == 0 else None)
        n += 1
        if n % 5000 == 0:
            s.active_expire_cycle(t)
            if time.time() - t1 > 10:
                break
    t2 = time.time()
    check(f"skiplist 60 000 + 20 000 so'rov ({t1 - t0:.2f} s), kalit maydoni 300 000 amal ({t2 - t1:.2f} s) — jami 6 s dan tez",
          n == 300000 and (t2 - t0) < 6.0, f"{n} amal, {t2 - t0:.2f} s")


def run(part):
    try:
        part()
        return True
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
        results.append(False)
        return False
    except TooSlow as e:
        print(f"\n  Juda sekin: {e}.")
        results.append(False)
        return False
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        print("\n  Xato (istisno):\n    " + "\n    ".join(tb[-3:]))
        results.append(False)
        return False


def main():
    t0 = time.time()
    a = run(part_skiplist)
    b = run(part_hll)
    c = run(part_keyspace)
    if a and b and c and all(results):
        run(part_day)
        run(part_speed)
    else:
        print("4-5. O'tkazib yuborildi: avval 1-3 qismlar to'liq o'tsin")
        results.append(False)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
