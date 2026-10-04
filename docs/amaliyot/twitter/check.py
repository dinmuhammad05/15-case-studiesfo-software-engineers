"""snowflake.py va timeline.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Besh qism:
  1. Snowflake: bitlar joylashuvi, takrorsizlik, ketma-ketlik to'lishi,
     soat orqaga ketishi, turli mashinalar.
  2. Tasma: birlik testlari — push va pull, obuna vaqti, o'chirish,
     bloklash, obunani bekor qilish, tasma uzunligi, kursor.
  3. Fuzz: sodda model ("JOIN" bilan tasma) bilan har o'qishni solishtirish.
  4. Narx: darajali graf ustida chegara bo'yicha yozish va o'qish narxi —
     gibrid ikkala sof strategiyadan arzon.
  5. Tezlik.
"""
import random
import sys
import time
import traceback

from model import FakeClock, power_law_graph

import snowflake as sf_mod
import timeline as tl_mod

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))


class TooSlow(Exception):
    pass


def guard(t0, limit, what):
    if time.time() - t0 > limit:
        raise TooSlow(f"{what}: {limit} soniyadan oshdi")


def attempt(fn, *a, **kw):
    try:
        return fn(*a, **kw), None
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


# ============================================================ 1. Snowflake
def part_snowflake():
    print("1. Snowflake")
    S, parse, EP = sf_mod.Snowflake, sf_mod.parse, sf_mod.TWEPOCH
    errs = []
    clk = FakeClock(EP + 1000)
    g = S(5, clk)
    a = g.next_id()
    if a != (1000 << 22) | (5 << 12):
        errs.append(f"birinchi ID {a}, kutilgan {(1000 << 22) | (5 << 12)} (vaqt << 22 | mashina << 12 | 0)")
    b = g.next_id()
    if b != a + 1:
        errs.append("bir xil millisekundda ketma-ketlik 1 ga oshishi kerak")
    clk.ms += 3
    c = g.next_id()
    if parse(c) != (EP + 1003, 5, 0):
        errs.append(f"yangi millisekundda ketma-ketlik 0 dan: parse = {parse(c)}")
    for bad in (-1, 1024):
        _, e = attempt(S, bad, clk)
        if e is None or not e.startswith("ValueError"):
            errs.append(f"mashina ID {bad} — ValueError")
    sid = (123456789 << 22) | (1023 << 12) | 4095
    if parse(sid) != (EP + 123456789, 1023, 4095):
        errs.append(f"parse: {parse(sid)}")
    check("bitlar: vaqt | 10 bit mashina | 12 bit ketma-ketlik; parse; mashina ID 0..1023", not errs, "; ".join(errs[:3]))

    errs = []

    class Spin(FakeClock):
        """Har 5000 chaqiruvda 1 ms o'tadi: ID lar millisekundiga 4096 tadan ko'p so'raladi."""

        def __call__(self):
            self.calls += 1
            if self.calls % 5000 == 0:
                self.ms += 1
            return self.ms

    clk = Spin(EP + 10**9)
    g = S(7, clk)
    ids = []
    t0 = time.time()
    for i in range(20000):
        ids.append(g.next_id())
        if i % 2000 == 0:
            guard(t0, 10, "Snowflake")
    if len(set(ids)) != len(ids):
        errs.append("takror ID")
    if any(x >= y for x, y in zip(ids, ids[1:])):
        errs.append("ID lar qat'iy o'sishi kerak")
    seqs = [parse(x)[2] for x in ids]
    if max(seqs) > 4095:
        errs.append("ketma-ketlik 4095 dan oshdi")
    times = [parse(x)[0] for x in ids]
    if any(t2 < t1 for t1, t2 in zip(times, times[1:])):
        errs.append("vaqt qismi kamaydi")
    stuck_ms = sum(1 for t1, t2 in zip(times, times[1:]) if t2 > t1)
    if stuck_ms < 4:
        errs.append("ketma-ketlik to'lganda keyingi millisekundni kutish kerak edi")
    check("to'lish: millisekundiga 4096 dan ko'p so'rov — keyingi ms kutiladi, takrorsiz, o'suvchi",
          not errs, "; ".join(errs))

    errs = []
    clk = FakeClock(EP + 5000)
    g = S(1, clk)
    g.next_id()
    clk.ms -= 2
    _, e = attempt(g.next_id)
    if e is None or "ClockMovedBackwards" not in e:
        errs.append("soat orqaga ketsa — ClockMovedBackwards (takror ID xavfi)")
    clk.ms += 2
    _, e = attempt(g.next_id)
    if e is not None:
        errs.append(f"soat quvib yetgach yana ishlashi kerak: {e}")
    check("soat orqaga ketsa — xato, takror ID emas", not errs, "; ".join(errs))

    errs = []
    clk = FakeClock(EP + 777)
    gens = [S(m, clk) for m in (0, 3, 1023)]
    all_ids = []
    for step in range(300):
        if step % 10 == 0:
            clk.ms += 1
        for gg in gens:
            all_ids.append((clk.ms, gg.next_id()))
    if len({x for _, x in all_ids}) != len(all_ids):
        errs.append("turli mashinalar bir xil ID berdi")
    by_id = sorted(all_ids, key=lambda p: p[1])
    if any(t2 < t1 for (t1, _), (t2, _) in zip(by_id, by_id[1:])):
        errs.append("ID bo'yicha tartib vaqt bo'yicha tartibni buzdi")
    check("uch mashina: takrorsiz va ID bo'yicha saralash = vaqt bo'yicha", not errs, "; ".join(errs))


# ============================================================ 2-3. tasma
class Naive:
    """Sekin, lekin aniq: har o'qishda barcha postlarni ko'rib chiqadi (v0 dagi JOIN)."""

    def __init__(self):
        self.following, self.blocked, self.posts, self.deleted = {}, {}, [], set()

    def follow(self, u, a, since):
        if u != a:
            self.following.setdefault(u, {})[a] = since

    def unfollow(self, u, a):
        self.following.get(u, {}).pop(a, None)

    def block(self, u, a):
        self.blocked.setdefault(u, set()).add(a)

    def post(self, a, pid):
        self.posts.append((pid, a))

    def delete(self, pid):
        self.deleted.add(pid)

    def read(self, u, limit=50, cursor=None):
        f = self.following.get(u, {})
        out = []
        for pid, a in reversed(self.posts):
            if cursor is not None and pid >= cursor:
                continue
            if pid in self.deleted:
                continue
            if a != u and (a not in f or pid <= f[a] or a in self.blocked.get(u, ())):
                continue
            out.append(pid)
            if len(out) == limit:
                break
        return out, (out[-1] if len(out) == limit else None)


def part_units():
    print("2. Tasma: birlik testlari")
    T = tl_mod.TimelineService
    errs = []
    s = T(threshold=3)
    for u in (1, 2, 3):
        s.follow(u, 9, since=0)          # 9 — 3 obunachi: "mashhur"
    s.follow(1, 8, since=0)              # 8 — 1 obunachi: oddiy
    w1 = s.post(8, 10)
    w2 = s.post(9, 11)
    if (w1, w2) != (2, 1):
        errs.append(f"post() yozuvlar soni: oddiy {w1} (kutilgan 2: o'zi + 1 obunachi), mashhur {w2} (kutilgan 1: faqat o'zi)")
    s.stats["pull_fetches"] = 0
    got, _ = s.read(1)
    if got != [11, 10]:
        errs.append(f"read(1) = {got}, kutilgan [11, 10] (push + pull birlashgan)")
    if s.stats["pull_fetches"] != 1:
        errs.append(f"pull_fetches = {s.stats['pull_fetches']}, kutilgan 1 (bitta mashhur obuna)")
    if s.read(9)[0] != [11]:
        errs.append("muallif o'z postini doim ko'radi")
    check("push va pull: yozuvlar soni, birlashtirish, o'z posti", not errs, "; ".join(errs[:3]))

    errs = []
    s = T(threshold=100)
    s.post(5, 1)
    s.follow(4, 5, since=1)
    s.post(5, 2)
    if s.read(4)[0] != [2]:
        errs.append(f"obunadan oldingi post ko'rinmasligi kerak: {s.read(4)[0]}")
    s.post(5, 3)
    s.delete(2)
    if s.read(4)[0] != [3]:
        errs.append("o'chirilgan post (tombstone) o'qishda filtrlanishi kerak")
    s.block(4, 5)
    if s.read(4)[0] != []:
        errs.append("bloklangan muallif ko'rinmasligi kerak")
    s2 = T(threshold=100)
    s2.follow(4, 5, since=0)
    s2.post(5, 1)
    s2.unfollow(4, 5)
    if s2.read(4)[0] != []:
        errs.append("obuna bekor qilingach, eski push yozuvlar ko'rinmasligi kerak")
    s2.follow(4, 5, since=1)
    s2.post(5, 2)
    if s2.read(4)[0] != [2]:
        errs.append(f"qayta obunadan keyin faqat yangi postlar: {s2.read(4)[0]}")
    check("obuna vaqti, tombstone, bloklash, obunani bekor qilish va qayta obuna", not errs, "; ".join(errs[:3]))

    errs = []
    s = T(threshold=100, cap=5)
    s.follow(1, 2, since=0)
    for pid in range(1, 21):
        s.post(2, pid)
    if len(s.timelines.get(1, ())) != 5:
        errs.append(f"tasma uzunligi {len(s.timelines.get(1, ()))}, cap = 5")
    if s.read(1)[0] != [20, 19, 18, 17, 16]:
        errs.append(f"cap=5 da read: {s.read(1)[0]}")
    s = T(threshold=2)
    for u in range(1, 4):
        s.follow(u, 99, since=0)
    for pid in range(1, 101):
        s.post(99, pid)
    pages, cur = [], None
    while True:
        got, cur = s.read(1, limit=30, cursor=cur)
        pages.append(got)
        if cur is None:
            break
    flat = [x for p in pages for x in p]
    if flat != list(range(100, 0, -1)) or [len(p) for p in pages] != [30, 30, 30, 10]:
        errs.append(f"kursor bilan sahifalash: {[len(p) for p in pages]}")
    check("tasma uzunligi (cap) va kursor bilan sahifalash", not errs, "; ".join(errs[:3]))


def part_fuzz():
    print("3. Fuzz: sodda model bilan solishtirish")
    errs = []
    for seed in range(50):
        rng = random.Random(seed)
        thr = rng.choice([1, 2, 3, 5, 10**9])
        s, nv = tl_mod.TimelineService(threshold=thr, cap=10**9), Naive()
        users = list(range(12))
        clock = 0
        for step in range(500):
            clock += 1
            op = rng.random()
            u, a = rng.choice(users), rng.choice(users)
            if op < 0.25:
                s.follow(u, a, clock)
                nv.follow(u, a, clock)
            elif op < 0.30:
                s.unfollow(u, a)
                nv.unfollow(u, a)
            elif op < 0.32:
                s.block(u, a)
                nv.block(u, a)
            elif op < 0.65:
                s.post(a, clock)
                nv.post(a, clock)
            elif op < 0.70 and nv.posts:
                pid = rng.choice(nv.posts)[0]
                s.delete(pid)
                nv.delete(pid)
            else:
                lim = rng.choice([1, 3, 10, 50])
                cur = rng.choice([None, None, clock - rng.randrange(1, 40)])
                got, e = attempt(s.read, u, lim, cur)
                want = nv.read(u, lim, cur)
                if e or got != want:
                    errs.append(f"seed {seed}, qadam {step}, threshold={thr}: read({u}, {lim}, {cur}) = "
                                f"{e or got}, kutilgan {want}")
                    break
        if errs:
            break
    check("50 x 500 amal (obuna, bekor qilish, bloklash, post, o'chirish, o'qish) — aynan bir xil",
          not errs, errs[0] if errs else "")

    errs = []
    for seed in range(30):
        rng = random.Random(1000 + seed)
        s, nv = tl_mod.TimelineService(threshold=rng.choice([2, 4, 10**9])), Naive()
        clock = 0
        for _ in range(400):
            clock += 1
            u, a = rng.randrange(8), rng.randrange(8)
            r = rng.random()
            if r < 0.3:
                s.follow(u, a, clock)
                nv.follow(u, a, clock)
            elif r < 0.9:
                s.post(a, clock)
                nv.post(a, clock)
            elif nv.posts:
                pid = rng.choice(nv.posts)[0]
                s.delete(pid)
                nv.delete(pid)
        for u in range(8):
            lim = rng.choice([1, 2, 7])
            got_all, cur, pages = [], None, 0
            while pages < 500:
                got, e = attempt(s.read, u, lim, cur)
                if e:
                    errs.append(e)
                    break
                got_all += got[0]
                cur = got[1]
                pages += 1
                if cur is None:
                    break
            want = nv.read(u, 10**9)[0]
            if got_all != want:
                errs.append(f"seed {seed}, foydalanuvchi {u}, limit {lim}: sahifalar birlashmasi aniq ro'yxatdan farq qiladi "
                            f"({len(got_all)} vs {len(want)})")
                break
        if errs:
            break
    check("sahifalash: 30 x 8 foydalanuvchi — barcha sahifalar birlashmasi = to'liq tasma (takrorsiz, bo'shliqsiz)",
          not errs, errs[0] if errs else "")

    s = tl_mod.TimelineService(threshold=1)
    rng = random.Random(4)
    for a in range(300):
        s.follow(10**6, a, 0)
        s.follow(10**6 + 1 + a, a, 0)
    pid = 0
    for _ in range(2000):
        for a in range(300):
            pid += 1
            s.post(a, pid)
    t0 = time.time()
    n = 0
    for i in range(2000):
        got, _ = s.read(10**6, limit=20, cursor=rng.randrange(10**5, pid))
        n += len(got)
        if i % 200 == 0:
            guard(t0, 6, "300 mashhur obunali o'qish")
    dt = time.time() - t0
    check(f"k-way merge: 300 mashhur obuna x 2000 post — 2000 ta o'qish {dt:.2f} s (≤ 3 s)",
          dt <= 3.0 and n == 40000, "hammasini yig'ib saralash emas, uyum (heap) bilan faqat kerakli 20 tasini oling")


# ============================================================ 4. narx
def simulate(graph, threshold, posts_per_user, reads_per_user, seed=1):
    s = tl_mod.TimelineService(threshold=threshold)
    for u, fs in graph.items():
        for a in fs:
            s.follow(u, a, 0)
    rng = random.Random(seed)
    users = list(graph)
    events = [("p", u) for u in users for _ in range(posts_per_user)] + \
             [("r", u) for u in users for _ in range(reads_per_user)]
    rng.shuffle(events)
    pid = 0
    max_fanout = 0
    t0 = time.time()
    for i, (kind, u) in enumerate(events):
        if i % 5000 == 0:
            guard(t0, 30, f"simulyatsiya (threshold={threshold})")
        if kind == "p":
            pid += 1
            max_fanout = max(max_fanout, s.post(u, pid))
        else:
            s.read(u, limit=20)
    return s.stats["push_writes"], s.stats["pull_fetches"], max_fanout


def part_cost():
    print("4. Narx: chegara qayerda bo'lishi kerak")
    graph = power_law_graph(8000, avg_following=40, alpha=1.0, seed=3)
    fol = {}
    for u, fs in graph.items():
        for a in fs:
            fol[a] = fol.get(a, 0) + 1
    top = sorted(fol.values(), reverse=True)
    print(f"      8 000 foydalanuvchi, {sum(top)} obuna; eng ko'p obunachi: {top[:3]}, median: {top[len(top) // 2]}")
    rows = {}
    for thr in (0, 200, 1000, 3000, 10**9):
        w, r, mx = simulate(graph, thr, posts_per_user=2, reads_per_user=20)
        rows[thr] = (w, r, mx, w + r)
        name = {0: "sof pull", 10**9: "sof push"}.get(thr, f"chegara {thr}")
        print(f"      {name:>14}: push yozuv {w:>8}, pull so'rov {r:>8}, eng katta fan-out {mx:>5}, jami {w + r:>8}")
    push, pull, hyb = rows[10**9], rows[0], rows[3000]
    check(f"sof pull eng qimmat: sof push'dan ≥ 4 barobar ko'p amal ({pull[3] / push[3]:.1f}x)",
          pull[3] >= 4 * push[3], "o'qish yozishdan 10 barobar ko'p — pull har o'qishda ishlaydi")
    check(f"gibrid (chegara 3000): eng katta fan-out {hyb[2]} (sof push'da {push[2]}), jami amal sof pull'dan "
          f"{pull[3] / max(hyb[3], 1):.1f}x kam",
          hyb[2] <= 3000 < push[2] and pull[3] >= 3 * hyb[3] and rows[200][2] <= 200,
          f"chegara 200 da eng katta fan-out {rows[200][2]}")


# ============================================================ 5. tezlik
def part_speed():
    print("5. Tezlik")
    t0 = time.time()
    clk = FakeClock()
    clk.auto = 0
    g = sf_mod.Snowflake(1, clk)
    for i in range(200000):
        if i % 1000 == 0:
            clk.ms += 1
        g.next_id()
    t1 = time.time()
    graph = power_law_graph(20000, avg_following=60, alpha=1.0, seed=8)
    s = tl_mod.TimelineService(threshold=500)
    for u, fs in graph.items():
        for a in fs:
            s.follow(u, a, 0)
    rng = random.Random(2)
    t2 = time.time()
    pid = 0
    for i in range(150000):
        u = rng.randrange(20000)
        if rng.random() < 0.3:
            pid += 1
            s.post(u, pid)
        else:
            s.read(u, limit=20)
        if i % 5000 == 0:
            guard(t2, 20, "tasma yuklamasi")
    t3 = time.time()
    check(f"200 000 Snowflake ID ({t1 - t0:.2f} s), 150 000 post/o'qish 20 000 foydalanuvchida ({t3 - t2:.2f} s) — jami 8 s dan tez",
          (t1 - t0) + (t3 - t2) < 8.0)


def run(part):
    try:
        part()
        return True
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
    except TooSlow as e:
        print(f"\n  Juda sekin: {e}.")
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        print("\n  Xato (istisno):\n    " + "\n    ".join(tb[-3:]))
    results.append(False)
    return False


def main():
    t0 = time.time()
    a = run(part_snowflake)
    b = run(part_units)
    if b and all(results):
        run(part_fuzz)
    if a and b and all(results):
        run(part_cost)
        run(part_speed)
    elif not all(results):
        print("3-5. O'tkazib yuborildi: avval 1-2 qismlar to'liq o'tsin")
        results.append(False)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
