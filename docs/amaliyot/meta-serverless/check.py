"""scheduler.py, concurrency.py va router.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Olti qism:
  1. Rejalashtiruvchi: birlik testlari — takror chaqiruv, kritiklik va muddat
     tartibi, muddati o'tganlar, kvota (token bucket), downstream chegarasi,
     bo'sh turmaslik.
  2. Rejalashtiruvchi: sodda model bilan solishtirish (fuzz), bajarish mumkin
     bo'lgan yuklamada muddat buzilmasligi, ortiqcha yuklamada kritiklik.
  3. AIMD: yaqinlashish, keskin pasayishga javob, kam talabda o'smaslik.
  4. Router: lokallik guruhlari barqarorligi, sovuq startlar, yuk balansi.
  5. Bir kun: hammasi birga — vaqt bo'yicha surish, kvota, downstream nosozligi.
  6. Tezlik: 300 000 chaqiruv.
"""
import math
import random
import sys
import time
from collections import OrderedDict

from model import HIGH, LOW, NORMAL, Call, Fn, stable_hash  # noqa: F401

import concurrency as cc_mod
import router as router_mod
import scheduler as sched_mod

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def unit(name, ok, detail=""):
    check(name, ok, "" if ok else detail)


def attempt(fn, *a, **kw):
    try:
        return fn(*a, **kw), None
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


# ============================================================ sodda model
class Naive:
    """Sekin, lekin aniq: har tikda hamma kutayotganlarni saralaydi."""

    def __init__(self, fns):
        self.fns = dict(fns)
        self.tokens = {n: float(f.burst) for n, f in self.fns.items()}
        self.q = []
        self.seen = set()

    def submit(self, c):
        if c.cid in self.seen:
            return False
        self.seen.add(c.cid)
        self.q.append(c)
        return True

    def pick(self, now, capacity, limits=None):
        limits = limits or {}
        for n, f in self.fns.items():
            self.tokens[n] = min(float(f.burst), self.tokens[n] + f.rate)
        self.q = [c for c in self.q if c.deadline >= now]
        out, used = [], {}
        for c in sorted(self.q, key=lambda c: (-c.crit, c.deadline, c.submit, c.cid)):
            if len(out) >= capacity:
                break
            f = self.fns[c.fn]
            if self.tokens[c.fn] < 1:
                continue
            d = f.downstream
            if d is not None and used.get(d, 0) >= limits.get(d, float("inf")):
                continue
            self.tokens[c.fn] -= 1
            if d is not None:
                used[d] = used.get(d, 0) + 1
            out.append(c)
        taken = {c.cid for c in out}
        self.q = [c for c in self.q if c.cid not in taken]
        return out


def run_sched(s, calls_by_tick, ticks, capacity, limits_fn=None):
    """Simulyatsiya: har tikda yangi chaqiruvlar, keyin pick. Natija: {cid: bajarilgan tik}."""
    done = {}
    for t in range(ticks):
        for c in calls_by_tick.get(t, ()):
            s.submit(c)
        limits = limits_fn(t) if limits_fn else None
        for c in s.pick(t, capacity, limits):
            if c.cid in done:
                raise AssertionError(f"{c.cid} ikki marta bajarildi")
            done[c.cid] = t
    return done


# ============================================================ 1. birlik
def part_units():
    print("1. Rejalashtiruvchi: birlik testlari")
    fns = {"a": Fn("a"), "b": Fn("b")}
    s = sched_mod.Scheduler(fns)
    r = [s.submit(Call("x1", "a", 0, 10)), s.submit(Call("x1", "a", 0, 10)), s.submit(Call("x2", "b", 0, 10))]
    unit("takror cid qabul qilinmaydi (at-least-once yetkazishda bir marta bajarish)",
         r == [True, False, True] and s.pending() == 2, f"submit={r}, pending={s.pending()}")

    s = sched_mod.Scheduler(fns)
    for c in [Call("p", "a", 0, 50, LOW), Call("q", "a", 0, 9, NORMAL), Call("r", "b", 0, 5, NORMAL),
              Call("s", "b", 0, 30, HIGH), Call("t", "a", 0, 5, NORMAL)]:
        s.submit(c)
    order = [c.cid for c in s.pick(0, 10)]
    unit("tartib: avval kritiklik, keyin eng yaqin muddat, keyin submit, keyin cid",
         order == ["s", "r", "t", "q", "p"], f"olindi {order}")

    s = sched_mod.Scheduler(fns)
    s.submit(Call("old", "a", 0, 2))
    s.submit(Call("new", "a", 0, 9))
    got = [c.cid for c in s.pick(5, 10)]
    unit("muddati o'tgan chaqiruv bajarilmaydi (navbatdan tashlanadi)", got == ["new"] and s.pending() == 0,
         f"olindi {got}, pending={s.pending()}")

    fq = {"q": Fn("q", rate=0.5, burst=3)}
    s = sched_mod.Scheduler(fq)
    for i in range(200):
        s.submit(Call(f"c{i:03d}", "q", 0, 1000))
    per = [len(s.pick(t, 100)) for t in range(20)]
    want = [3, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    unit("kvota (token bucket): boshida burst, har tikda +rate, ko'pi bilan burst", per == want,
         f"tiklar bo'yicha {per}, kerak {want}")

    fd = {"u": Fn("u", downstream="tao"), "v": Fn("v", downstream="tao"), "w": Fn("w")}
    s = sched_mod.Scheduler(fd)
    for i in range(30):
        for f in "uvw":
            s.submit(Call(f"{f}{i:02d}", f, 0, 100, HIGH if f != "w" else LOW))
    got = s.pick(0, 20, {"tao": 5})
    tao = sum(1 for c in got if c.fn in "uv")
    unit("downstream chegarasi: 'tao' ga 5 tadan ko'p emas, qolgan joy boshqa funksiyalarga (bo'sh turmaydi)",
         tao == 5 and len(got) == 20, f"tao={tao}, jami={len(got)}")

    fx = {"slow": Fn("slow", rate=0.0, burst=1), "fast": Fn("fast")}
    s = sched_mod.Scheduler(fx)
    for i in range(10):
        s.submit(Call(f"s{i}", "slow", 0, 100, HIGH))
        s.submit(Call(f"f{i}", "fast", 0, 100, LOW))
    a = [c.cid for c in s.pick(0, 5)]
    b = [c.cid for c in s.pick(1, 5)]
    unit("kvotasi tugagan funksiya boshqalarni to'smaydi", a == ["s0", "f0", "f1", "f2", "f3"]
         and b == ["f4", "f5", "f6", "f7", "f8"], f"{a} / {b}")


# ============================================================ 2. fuzz va muddatlar
def random_workload(rng, ticks, nf, rate_mode):
    fns = {}
    for i in range(nf):
        name = f"f{i}"
        if rate_mode and rng.random() < 0.4:
            fns[name] = Fn(name, rate=rng.choice([0.3, 0.5, 1, 2, 5]), burst=rng.randint(1, 8),
                           downstream=rng.choice([None, "tao", "kesh"]))
        else:
            fns[name] = Fn(name, downstream=rng.choice([None, None, "tao", "kesh"]))
    calls = {}
    n = 0
    for t in range(ticks):
        for _ in range(rng.randint(0, 12)):
            n += 1
            fn = f"f{rng.randrange(nf)}"
            cid = f"c{n:05d}" if rng.random() > 0.03 else f"c{max(1, n - rng.randint(1, 5)):05d}"
            calls.setdefault(t, []).append(Call(cid, fn, t, t + rng.randint(0, 30), rng.choice([LOW, NORMAL, HIGH])))
    return fns, calls


def part_fuzz():
    print("2. Rejalashtiruvchi: fuzz, muddatlar va kritiklik")
    bad = None
    for seed in range(40):
        rng = random.Random(seed)
        fns, calls = random_workload(rng, 120, rng.randint(2, 12), rate_mode=True)
        mine, ref = sched_mod.Scheduler(fns), Naive(fns)
        for t in range(150):
            lim = {"tao": rng.randint(0, 6), "kesh": rng.randint(1, 10)} if rng.random() < 0.7 else None
            cap = rng.randint(0, 10)
            for c in calls.get(t, ()):
                a, b = mine.submit(c), ref.submit(c)
                if a != b:
                    bad = f"seed={seed}, t={t}: submit({c.cid}) = {a}, kerak {b}"
                    break
            if bad:
                break
            x, err = attempt(mine.pick, t, cap, lim)
            y = ref.pick(t, cap, lim)
            if err or x != y:
                bad = err or f"seed={seed}, t={t}: {[c.cid for c in x]} != {[c.cid for c in y]}"
                break
        if bad:
            break
    check("40 ta tasodifiy yuklama (kvotalar, downstream chegaralari, takrorlar): har tikda sodda model bilan "
          "aynan bir xil tanlov", bad is None, bad or "")

    bad = None
    for seed in range(30):
        rng = random.Random(100 + seed)
        cap = rng.randint(2, 8)
        calls, k = {}, 0
        for slot in range(200):                     # ma'lum jadvaldan teskari yasalgan, bajarish mumkin bo'lgan yuklama
            for _ in range(cap):
                if rng.random() < 0.85:
                    k += 1
                    r = max(0, slot - rng.randint(0, 20))
                    d = slot + rng.randint(0, 15)
                    calls.setdefault(r, []).append(Call(f"j{k:05d}", "f", r, d, NORMAL))
        done = run_sched(sched_mod.Scheduler({"f": Fn("f")}), calls, 260, cap)
        late = [c.cid for cs in calls.values() for c in cs if c.cid not in done or done[c.cid] > c.deadline]
        if late:
            bad = f"seed={seed}: {len(late)} ta chaqiruv muddatidan kechikdi (masalan {late[0]})"
            break
    check("bajarish mumkin bo'lgan 30 ta yuklama: birorta ham muddat buzilmaydi (EDF optimal)", bad is None,
          bad or "")

    rng = random.Random(7)
    calls, k = {}, 0
    for t in range(200):
        for _ in range(6):                          # HIGH: tikiga 6 ta, sig'im 10 — o'zi bajariladi
            k += 1
            calls.setdefault(t, []).append(Call(f"h{k:05d}", "f", t, t + rng.randint(0, 3), HIGH))
        for _ in range(8):                          # LOW: tikiga 8 ta — jami sig'imdan ko'p
            k += 1
            calls.setdefault(t, []).append(Call(f"l{k:05d}", "f", t, t + rng.randint(0, 40), LOW))
    done = run_sched(sched_mod.Scheduler({"f": Fn("f")}), calls, 260, 10)
    hi_miss = sum(1 for cs in calls.values() for c in cs if c.crit == HIGH and c.cid not in done)
    lo_done = sum(1 for cs in calls.values() for c in cs if c.crit == LOW and c.cid in done)
    check("ortiqcha yuklama: yuqori kritiklikdagilar hech qachon kechikmaydi, past kritiklik qolgan sig'imni "
          "to'liq ishlatadi", hi_miss == 0 and lo_done >= 200 * 4 - 5,
          f"HIGH kechikdi={hi_miss}, LOW bajarildi={lo_done}")


# ============================================================ 3. AIMD
def aimd_sim(ctl, ticks, cap_fn, demand_fn):
    hist, over = [], 0
    for t in range(ticks):
        sent = min(ctl.limit, demand_fn(t))
        o = max(0, sent - cap_fn(t))
        over += o > 0
        ctl.on_tick(sent, o)
        hist.append(ctl.limit)
    return hist, over


def part_aimd():
    print("3. AIMD: downstream'ni himoya qilish")
    ctl = cc_mod.AIMD(start=1)
    hist, over = aimd_sim(ctl, 600, lambda t: 40, lambda t: 10**6)
    tail = hist[200:]
    avg = sum(tail) / len(tail)
    check(f"yashirin sig'im 40: o'rtacha chegara {avg:.1f} (20..42 oralig'ida), ortiqcha yuklangan tiklar "
          f"{over}/600 (<= 10%)", 20 <= avg <= 42 and over <= 60 and max(tail) <= 41,
          f"o'rtacha={avg:.1f}, max={max(tail)}, ortiqcha={over}")

    ctl = cc_mod.AIMD(start=1)
    hist, _ = aimd_sim(ctl, 400, lambda t: 40 if t < 300 else 10, lambda t: 10**6)
    after = hist[300:310]
    check("sig'im keskin tushdi (40 -> 10): 5 tik ichida chegara 15 dan past",
          min(after[:5]) <= 15, f"tushgandan keyingi chegaralar: {after}")

    ctl = cc_mod.AIMD(start=1)
    hist, _ = aimd_sim(ctl, 200, lambda t: 100, lambda t: 3)
    ctl2 = cc_mod.AIMD(start=8)
    ctl2.on_tick(8, 3)
    check("kam talab (3/tik) bilan chegara o'smaydi (ishlatilmagan chegara — keyingi portlashning sababi); "
          "ortiqcha yuklamada — ikki barobar kamayadi", max(hist) <= 4 and ctl2.limit == 4,
          f"max chegara={max(hist)}, 8 -> {ctl2.limit}")


# ============================================================ 4. router
def zipf_fns(rng, n_fns, n_calls, s=1.1):
    weights = [1 / (i + 1) ** s for i in range(n_fns)]
    return rng.choices([f"fn{i:04d}" for i in range(n_fns)], weights, k=n_calls)


def lru_sim(route, calls, n_workers, cache, per_tick):
    """Har ishchida LRU kesh (cache ta funksiya). Natija: (sovuq start ulushi, eng katta yuk / o'rtacha)."""
    caches = [OrderedDict() for _ in range(n_workers)]
    cold = 0
    worst = 0
    for i in range(0, len(calls), per_tick):
        load = {}
        for fn in calls[i:i + per_tick]:
            w = route(fn, load)
            load[w] = load.get(w, 0) + 1
            c = caches[int(w[1:])]
            if fn in c:
                c.move_to_end(fn)
            else:
                cold += 1
                c[fn] = True
                if len(c) > cache:
                    c.popitem(last=False)
        avg = per_tick / n_workers
        worst = max(worst, max(load.values()) / avg)
    return cold / len(calls), worst


def part_router():
    print("4. Router: lokallik guruhlari va sovuq start")
    workers = [f"w{i:02d}" for i in range(64)]
    r = router_mod.Router(workers, group_size=3)
    fns = [f"fn{i:04d}" for i in range(3000)]
    g1, err = attempt(lambda: {f: tuple(r.group(f)) for f in fns})
    ok = err is None and all(len(set(g)) == 3 for g in g1.values())
    r.add_worker("w64")
    g2 = {f: tuple(r.group(f)) for f in fns}
    moved = sum(1 for f in fns if set(g1[f]) != set(g2[f])) / len(fns)
    r2 = router_mod.Router(list(reversed(workers)), group_size=3)
    same = all(set(r2.group(f)) == set(g1[f]) for f in fns[:200])
    check(f"guruh: 3 ta har xil ishchi, ro'yxat tartibiga bog'liq emas; ishchi qo'shilganda {moved:.1%} "
          f"funksiyaning guruhi o'zgaradi (<= 8%)", ok and same and moved <= 0.08,
          err or f"tartibga bog'liq emas={same}, o'zgardi={moved:.1%}")

    rng = random.Random(3)
    calls = zipf_fns(rng, 3000, 60000)
    r = router_mod.Router(workers, group_size=3)
    cold, worst = lru_sim(lambda fn, load: r.route(fn, load, 12), calls, 64, 60, 640)
    rnd = random.Random(4)
    cold_rand, _ = lru_sim(lambda fn, load: rnd.choice(workers), calls, 64, 60, 640)
    check(f"sovuq startlar: lokallik guruhlari bilan {cold:.1%}, tasodifiy taqsimotda {cold_rand:.1%} "
          f"(kamida 2 barobar kam); hech bir ishchi tikiga 12 tadan ko'p olmaydi (eng yuklangani "
          f"o'rtachadan {worst:.2f}x)", cold * 2 <= cold_rand and worst <= 1.2 + 1e-9,
          f"lokal={cold:.1%}, tasodifiy={cold_rand:.1%}, yuk={worst:.2f}")

    load = {"w00": 5, "w01": 2}
    g = r.group("issiq")
    full = {w: 12 for w in g}
    spill = r.route("issiq", full, 12)
    unit("guruh to'la bo'lsa — chaqiruv guruhdan tashqariga, eng kam yuklangan ishchiga; bo'sh guruhda — "
         "guruh ichida", spill not in g and spill == min(workers, key=lambda w: (full.get(w, 0), w))
         and r.route("issiq", load, 12) in g, f"guruh={g}, to'lganda={spill}")


# ============================================================ 5. bir kun va tezlik
def part_day():
    print("5. Bir kun: kvota, muddat, downstream va vaqt bo'yicha surish birga")
    rng = random.Random(11)
    day, cap = 1440, 300                            # 1 tik = 1 daqiqa; ikkinchi kun — faqat "qarzlarni" bajarish
    fns = {f"f{i}": Fn(f"f{i}", downstream="tao" if i % 8 == 0 else None) for i in range(40)}
    calls, k = {}, 0
    for t in range(day):
        wave = 0.15 + 0.85 * math.sin(math.pi * t / day) ** 2      # kunduzi cho'qqi
        for _ in range(int(450 * wave)):
            k += 1
            urgent = rng.random() < 0.3
            calls.setdefault(t, []).append(Call(f"d{k:06d}", f"f{rng.randrange(40)}", t,
                                                t + (rng.randint(0, 2) if urgent else day), HIGH if urgent else LOW))
    ctl = cc_mod.AIMD(start=5)
    s = sched_mod.Scheduler(fns)
    done, over, util = {}, 0, []

    def tao_cap(t):
        return 15 if 700 <= t < 760 else 60       # kunduzi bir soatlik nosozlik

    t0 = time.time()
    for t in range(2 * day):
        if t % 100 == 0 and time.time() - t0 > 30:
            check("kun: simulyatsiya 30 soniyada tugamadi — pick juda sekin (har tikda hammasini saralamang)", False)
            return
        for c in calls.get(t, ()):
            s.submit(c)
        picked = s.pick(t, cap, {"tao": ctl.limit})
        sent = sum(1 for c in picked if fns[c.fn].downstream == "tao")
        o = max(0, sent - tao_cap(t))
        over += o > 0
        ctl.on_tick(sent, o)
        for c in picked:
            done[c.cid] = t
        if t < day:
            util.append(len(picked) / cap)
    hi = [c for cs in calls.values() for c in cs if c.crit == HIGH]
    lo = [c for cs in calls.values() for c in cs if c.crit == LOW]
    hi_late = sum(1 for c in hi if c.cid not in done or done[c.cid] > c.deadline)
    lo_ok = sum(1 for c in lo if c.cid in done and done[c.cid] <= c.deadline) / len(lo)
    peak_in = max(len(calls.get(t, ())) for t in range(day)) / cap
    avg_util = sum(util) / len(util)
    check(f"kun: kiruvchi cho'qqi sig'imning {peak_in:.2f}x i, o'rtacha bandlik {avg_util:.0%}; "
          f"shoshilinchlardan kechikkani {hi_late}/{len(hi)} (<= 1%); kechiktiriladiganlarning {lo_ok:.1%} i "
          f"24 soat ichida; downstream ortiqcha yuklangan daqiqalar {over} (<= 5%)",
          hi_late <= len(hi) * 0.01 and lo_ok >= 0.999 and avg_util >= 0.8 and over <= 0.05 * 2 * day,
          f"HIGH={hi_late}, LOW={lo_ok:.2%}, bandlik={avg_util:.0%}, ortiqcha={over}")


def part_speed():
    print("6. Tezlik")
    rng = random.Random(42)
    fns = {f"g{i}": Fn(f"g{i}", rate=rng.choice([2, 5, 50, 1e9]), burst=rng.choice([5, 50, 10**9]),
                        downstream=rng.choice([None, "a", "b"])) for i in range(200)}
    s = sched_mod.Scheduler(fns)
    batches, k = [], 0
    for t in range(1500):
        b = []
        for _ in range(200):
            k += 1
            b.append(Call(f"z{k:07d}", f"g{rng.randrange(200)}", t, t + rng.randint(0, 600), rng.randint(0, 2)))
        batches.append(b)
    t0 = time.time()
    n = 0
    for t, b in enumerate(batches):
        for c in b:
            s.submit(c)
        n += len(s.pick(t, 150, {"a": 40, "b": 60}))
        if t % 100 == 0 and time.time() - t0 > 6:
            break
    dt = time.time() - t0
    check(f"tezlik: 300 000 chaqiruv, 200 funksiya, 1 500 tik — 6 soniyadan tez ({dt:.2f} s)",
          t == 1499 and dt < 6.0, f"{dt:.2f} s, {t + 1} tik" if t != 1499 or dt >= 6 else "")


def run(part):
    try:
        part()
        return True
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
        results.append(False)
        return False


def main():
    t0 = time.time()
    run(part_units)
    ok_units = all(results)
    if ok_units:
        run(part_fuzz)
    else:
        print("2. O'tkazib yuborildi: avval birlik testlari to'liq o'tsin")
        results.append(False)
    run(part_aimd)
    run(part_router)
    if ok_units:
        run(part_day)
        run(part_speed)
    else:
        print("5-6. O'tkazib yuborildi")
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
