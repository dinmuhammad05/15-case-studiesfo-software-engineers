"""book.py va feed.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Besh qism:
  1. Kitob: birlik testlari — narx-vaqt ustuvorligi, bitim narxi, qisman
     bajarilish, market/IOC/FOK, post-only, o'z-o'zi bilan savdoni oldini olish
     (STP), bekor qilish, o'zgartirish, tekshiruvlar, chuqurlik.
  2. Fuzz: minglab tasodifiy buyruq — sizning kitobingiz sodda (sekin, lekin
     aniq) model bilan har qadamda bir xil hodisa va bir xil holat beradi.
  3. Determinizm: jurnalni qayta o'ynash aynan o'sha hodisalar va holatni beradi.
  4. L2 oqimi mijozi: yo'qolgan, takrorlangan va aralashgan xabarlar bilan
     ham kitob nusxasi birja bilan bir xil bo'lib qoladi.
  5. Tezlik: chuqur kitobda 200 000 buyruq.
"""
import random
import sys
import time

from exchange import Exchange
from model import (BUY, FOK, GTC, IOC, SELL, Accepted, Cancelled, Modified,
                   Order, Rejected, Snapshot, Trade)

try:
    import book as book_mod
except Exception as e:  # noqa: BLE001
    print(f"book.py yuklanmadi: {e}")
    raise
try:
    import feed as feed_mod
except Exception as e:  # noqa: BLE001
    print(f"feed.py yuklanmadi: {e}")
    raise

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


def B(tick=1):
    return book_mod.Book(tick)


def O(oid, side, qty, price=None, owner=None, tif=GTC, post_only=False):
    return Order(oid, owner or f"u{oid}", side, qty, price, tif, post_only)


# ============================================================ sodda model
class Naive:
    """Sekin, lekin aniq: hamma buyurtmalar bitta ro'yxatda, har safar saralanadi."""

    def __init__(self, tick=1):
        self.tick = tick
        self.rest = []          # [t, oid, owner, side, price, qty]
        self.seen = set()
        self.t = 0

    def _ok_int(self, x):
        return isinstance(x, int) and not isinstance(x, bool)

    def _price_ok(self, p):
        return self._ok_int(p) and p > 0 and p % self.tick == 0

    def _cross(self, side, limit):
        opp = [r for r in self.rest if r[3] != side]
        if side == BUY:
            opp = [r for r in opp if limit is None or r[4] <= limit]
            opp.sort(key=lambda r: (r[4], r[0]))
        else:
            opp = [r for r in opp if limit is None or r[4] >= limit]
            opp.sort(key=lambda r: (-r[4], r[0]))
        return opp

    def _place(self, oid, owner, side, price, qty):
        self.t += 1
        self.rest.append([self.t, oid, owner, side, price, qty])

    def _match(self, oid, owner, side, limit, qty, ev):
        for r in self._cross(side, limit):
            if qty == 0:
                break
            if r[2] == owner:
                ev.append(Cancelled(oid, qty, "stp"))
                qty = 0
                break
            q = min(qty, r[5])
            ev.append(Trade(oid, r[1], r[4], q))
            r[5] -= q
            qty -= q
        self.rest = [r for r in self.rest if r[5] > 0]
        return qty

    def submit(self, o):
        if o.oid in self.seen:
            return [Rejected(o.oid, "dup")]
        if not self._ok_int(o.qty) or o.qty <= 0:
            return [Rejected(o.oid, "qty")]
        if o.price is not None and not self._price_ok(o.price):
            return [Rejected(o.oid, "tick")]
        if o.post_only and (o.price is None or self._cross(o.side, o.price)):
            return [Rejected(o.oid, "post_only")]
        self.seen.add(o.oid)
        ev = [Accepted(o.oid)]
        if o.tif == FOK:
            got = 0
            for r in self._cross(o.side, o.price):
                if r[2] == o.owner:
                    break
                got += r[5]
            if got < o.qty:
                return ev + [Cancelled(o.oid, o.qty, "fok")]
        rem = self._match(o.oid, o.owner, o.side, o.price, o.qty, ev)
        if rem:
            if o.price is None:
                ev.append(Cancelled(o.oid, rem, "market"))
            elif o.tif == IOC:
                ev.append(Cancelled(o.oid, rem, "ioc"))
            else:
                self._place(o.oid, o.owner, o.side, o.price, rem)
        return ev

    def _find(self, oid):
        for r in self.rest:
            if r[1] == oid:
                return r
        return None

    def cancel(self, oid):
        r = self._find(oid)
        if r is None:
            return [Rejected(oid, "unknown")]
        self.rest.remove(r)
        return [Cancelled(oid, r[5], "user")]

    def modify(self, oid, qty, price=None):
        r = self._find(oid)
        if r is None:
            return [Rejected(oid, "unknown")]
        if not self._ok_int(qty) or qty <= 0:
            return [Rejected(oid, "qty")]
        price = r[4] if price is None else price
        if not self._price_ok(price):
            return [Rejected(oid, "tick")]
        if price == r[4] and qty <= r[5]:
            r[5] = qty
            return [Modified(oid, price, qty)]
        self.rest.remove(r)
        ev = [Modified(oid, price, qty)]
        rem = self._match(oid, r[2], r[3], price, qty, ev)
        if rem:
            self._place(oid, r[2], r[3], price, rem)
        return ev

    def depth(self, side, n=5):
        agg = {}
        for r in self.rest:
            if r[3] == side:
                agg[r[4]] = agg.get(r[4], 0) + r[5]
        ps = sorted(agg, reverse=(side == BUY))
        return [(p, agg[p]) for p in ps[:n]]

    def best_bid(self):
        d = self.depth(BUY, 1)
        return d[0][0] if d else None

    def best_ask(self):
        d = self.depth(SELL, 1)
        return d[0][0] if d else None

    def order(self, oid):
        r = self._find(oid)
        return r[5] if r else None

    def state(self):
        res = []
        for side in (BUY, SELL):
            rs = sorted((r for r in self.rest if r[3] == side),
                        key=lambda r: ((-r[4]) if side == BUY else r[4], r[0]))
            levels = []
            for r in rs:
                if levels and levels[-1][0] == r[4]:
                    levels[-1][1].append((r[1], r[5]))
                else:
                    levels.append((r[4], [(r[1], r[5])]))
            res.append(tuple((p, tuple(q)) for p, q in levels))
        return tuple(res)


# ============================================================ 1. kitob
def part_units():
    print("1. Kitob: birlik testlari")
    b = B()
    for o in (O(1, SELL, 100, 101), O(2, SELL, 100, 100), O(3, SELL, 100, 100)):
        b.submit(o)
    ev = b.submit(O(4, BUY, 250, 101))
    want = [Accepted(4), Trade(4, 2, 100, 100), Trade(4, 3, 100, 100), Trade(4, 1, 101, 50)]
    unit("narx-vaqt ustuvorligi: avval eng yaxshi narx, bir narxda — kim oldin kelgan", ev == want, f"olindi {ev}")

    b = B()
    b.submit(O(1, SELL, 100, 100))
    ev = b.submit(O(2, BUY, 50, 105))
    b2 = B()
    b2.submit(O(1, BUY, 100, 100))
    ev2 = b2.submit(O(2, SELL, 30, 95))
    unit("bitim narxi — kitobda turgan (maker) buyurtmaning narxi", ev == [Accepted(2), Trade(2, 1, 100, 50)]
          and ev2 == [Accepted(2), Trade(2, 1, 100, 30)], f"{ev} / {ev2}")

    b = B()
    b.submit(O(1, SELL, 100, 100))
    ev = b.submit(O(2, BUY, 150, 100))
    unit("qisman bajarilish: qoldiq kitobda qoladi (best_bid, order, depth)",
          ev == [Accepted(2), Trade(2, 1, 100, 100)] and b.best_bid() == 100 and b.best_ask() is None
          and b.order(2) == 50 and b.order(1) is None and b.depth(BUY) == [(100, 50)], f"{ev}")

    b = B()
    b.submit(O(1, SELL, 40, 100))
    b.submit(O(2, SELL, 40, 102))
    ev = b.submit(O(3, BUY, 100))
    e0 = B().submit(O(9, SELL, 10))
    unit("market: bor narxlarda bajariladi, qoldiq bekor ('market'), kitobda qolmaydi",
          ev == [Accepted(3), Trade(3, 1, 100, 40), Trade(3, 2, 102, 40), Cancelled(3, 20, "market")]
          and b.best_bid() is None and e0 == [Accepted(9), Cancelled(9, 10, "market")], f"{ev} / {e0}")

    b = B()
    b.submit(O(1, SELL, 40, 100))
    ev = b.submit(O(2, BUY, 100, 100, tif=IOC))
    unit("IOC: darhol bajarilgani — bitim, qoldig'i bekor ('ioc')",
          ev == [Accepted(2), Trade(2, 1, 100, 40), Cancelled(2, 60, "ioc")] and b.best_bid() is None, f"{ev}")

    b = B()
    b.submit(O(1, SELL, 40, 100))
    b.submit(O(2, SELL, 40, 101))
    s0 = b.state()
    ev = b.submit(O(3, BUY, 100, 101, tif=FOK))
    s1 = b.state()
    ev2 = b.submit(O(4, BUY, 80, 101, tif=FOK))
    unit("FOK: yetmasa — hech qanday bitim yo'q va kitob o'zgarmaydi; yetsa — to'liq",
          ev == [Accepted(3), Cancelled(3, 100, "fok")] and s0 == s1
          and ev2 == [Accepted(4), Trade(4, 1, 100, 40), Trade(4, 2, 101, 40)], f"{ev} / {ev2}")

    b = B()
    b.submit(O(1, SELL, 10, 100))
    s0 = b.state()
    ev = b.submit(O(2, BUY, 5, 100, post_only=True))
    ev2 = b.submit(O(3, BUY, 5, 99, post_only=True))
    ev3 = b.submit(O(4, BUY, 5, post_only=True))
    unit("post-only: kesishsa — rad (kitob o'zgarmaydi), kesishmasa — kitobga",
          ev == [Rejected(2, "post_only")] and ev2 == [Accepted(3)] and b.best_bid() == 99
          and ev3 == [Rejected(4, "post_only")] and b.state()[1] == s0[1], f"{ev} / {ev2} / {ev3}")

    b = B()
    b.submit(O(1, SELL, 30, 100, owner="bank"))
    b.submit(O(2, SELL, 30, 100, owner="fond"))
    b.submit(O(3, SELL, 30, 100, owner="bank2"))
    ev = b.submit(O(4, BUY, 100, 100, owner="fond"))
    ev_f = b.submit(O(5, BUY, 40, 100, owner="fond", tif=FOK))
    unit("STP: o'z buyurtmasigacha savdo, keyin qoldiq bekor ('stp'); o'z buyurtmasi kitobda qoladi; "
          "FOK uchun mavjud miqdor — faqat o'z buyurtmasigacha",
          ev == [Accepted(4), Trade(4, 1, 100, 30), Cancelled(4, 70, "stp")] and b.order(2) == 30
          and b.order(3) == 30 and ev_f == [Accepted(5), Cancelled(5, 40, "fok")], f"{ev} / {ev_f}")

    b = B()
    b.submit(O(1, BUY, 30, 99))
    b.submit(O(2, BUY, 20, 99))
    ev = b.cancel(1)
    ev2 = b.cancel(1)
    b.cancel(2)
    unit("cancel: qoldiq bilan 'user'; qayta — 'unknown'; bo'sh daraja depth'dan yo'qoladi",
          ev == [Cancelled(1, 30, "user")] and ev2 == [Rejected(1, "unknown")] and b.depth(BUY) == []
          and b.best_bid() is None, f"{ev} / {ev2} / {b.depth(BUY)}")

    b = B()
    b.submit(O(1, BUY, 50, 99))
    b.submit(O(2, BUY, 50, 99))
    e1 = b.modify(1, 30)                     # kamaytirish — navbat saqlanadi
    t1 = b.submit(O(3, SELL, 30, 99))
    b.submit(O(4, BUY, 10, 99))
    e2 = b.modify(2, 80)                     # oshirish — navbat oxiriga
    t2 = b.submit(O(5, SELL, 10, 99))
    e3 = b.modify(2, 5, 98)                  # narx o'zgarishi — yangi daraja oxiri
    b.submit(O(6, SELL, 20, 101))
    e4 = b.modify(2, 90, 101)                # kesishuvchi o'zgartirish — bitim
    unit("modify: kamaytirish navbatni saqlaydi; oshirish yoki narx — navbat oxiriga; kesishsa — bitim",
          e1 == [Modified(1, 99, 30)] and t1 == [Accepted(3), Trade(3, 1, 99, 30)]
          and e2 == [Modified(2, 99, 80)] and t2 == [Accepted(5), Trade(5, 4, 99, 10)]
          and e3 == [Modified(2, 98, 5)] and e4 == [Modified(2, 101, 90), Trade(2, 6, 101, 20)]
          and b.order(2) == 70 and b.best_bid() == 101 and b.modify(99, 5) == [Rejected(99, "unknown")],
          f"{e1} {t1} {e2} {t2} {e3} {e4}")

    b = B(tick=5)
    r = [b.submit(O(1, BUY, 0, 100)), b.submit(O(2, BUY, -5, 100)), b.submit(O(3, BUY, 1.5, 100)),
         b.submit(O(4, BUY, 10, 102)), b.submit(O(5, BUY, 10, 100.0)), b.submit(O(6, BUY, 10, 0)),
         b.submit(O(1, BUY, 10, 100))]
    b.cancel(1)
    dup = b.submit(O(1, SELL, 10, 105))
    m = [b.modify(1, 5)]
    b.submit(O(7, BUY, 10, 95))
    m += [b.modify(7, 0), b.modify(7, 10, 97)]
    want = [[Rejected(1, "qty")], [Rejected(2, "qty")], [Rejected(3, "qty")], [Rejected(4, "tick")],
            [Rejected(5, "tick")], [Rejected(6, "tick")], [Accepted(1)]]
    unit("tekshiruvlar: miqdor musbat butun; narx musbat, butun va tick karrali (float yo'q); "
          "oid qayta ishlatilmaydi (rad etilgani — mumkin)",
          r == want and dup == [Rejected(1, "dup")]
          and m == [[Rejected(1, "unknown")], [Rejected(7, "qty")], [Rejected(7, "tick")]], f"{r} {dup} {m}")

    b = B()
    for i, (s, q, p) in enumerate([(BUY, 10, 99), (BUY, 20, 99), (BUY, 5, 98), (BUY, 7, 97), (SELL, 3, 101),
                                   (SELL, 4, 101), (SELL, 8, 103), (SELL, 1, 102)], 1):
        b.submit(O(i, s, q, p))
    b.submit(O(20, SELL, 12, 99))
    unit("depth: darajalar jamlangan, eng yaxshisi birinchi, n bilan cheklangan, bitimdan keyin yangilanadi",
          b.depth(BUY, 2) == [(99, 18), (98, 5)] and b.depth(SELL) == [(101, 7), (102, 1), (103, 8)]
          and b.depth(BUY, 10) == [(99, 18), (98, 5), (97, 7)], f"{b.depth(BUY, 10)} / {b.depth(SELL)}")


# ============================================================ 2. fuzz
def rand_cmd(rng, known, next_oid, tick, bad_prices):
    r = rng.random()
    if r < 0.2 and known:
        return ("cancel", rng.choice(known) if rng.random() < 0.9 else 10**6 + rng.randrange(9))
    if r < 0.35 and known:
        oid = rng.choice(known)
        price = None if rng.random() < 0.5 else tick * rng.randint(95, 105)
        if bad_prices and rng.random() < 0.1:
            price = tick * 100 + 1
        return ("modify", oid, rng.choice([rng.randint(1, 60), rng.randint(1, 5), 0]) if rng.random() < 0.1
                else rng.randint(1, 60), price)
    side = rng.choice([BUY, SELL])
    mid = 100
    price = tick * (mid + rng.randint(-6, 6) + (-2 if side == BUY else 2))
    if rng.random() < 0.08:
        price = None
    if bad_prices and price is not None and rng.random() < 0.05:
        price = price + 1
    tif = rng.choices([GTC, IOC, FOK], [0.75, 0.15, 0.10])[0]
    oid = next_oid if rng.random() > 0.02 else max(1, next_oid - rng.randint(1, 5))
    qty = rng.randint(1, 60) if rng.random() > 0.02 else rng.choice([0, -3])
    return ("new", Order(oid, f"u{rng.randrange(5)}", side, qty, price, tif, rng.random() < 0.1))


def run_cmd(bk, cmd):
    if cmd[0] == "new":
        return bk.submit(cmd[1])
    if cmd[0] == "cancel":
        return bk.cancel(cmd[1])
    return bk.modify(cmd[1], cmd[2], cmd[3])


def part_fuzz():
    print("2. Fuzz: sodda model bilan solishtirish")
    fails = []
    ops = 0
    t0 = time.time()
    for seed in range(40):
        rng = random.Random(seed)
        tick = 5 if seed % 4 == 3 else 1
        mine, ref = book_mod.Book(tick), Naive(tick)
        known, nxt = [], 1
        for step in range(1200):
            cmd = rand_cmd(rng, known, nxt, tick, seed % 4 == 3)
            if cmd[0] == "new" and cmd[1].oid == nxt:
                nxt += 1
                known.append(cmd[1].oid)
            a, err = attempt(run_cmd, mine, cmd)
            e = run_cmd(ref, cmd)
            ops += 1
            if err or a != e:
                fails.append((seed, step, cmd, err or f"siz: {a}, kerak: {e}"))
                break
            if mine.state() != ref.state() or mine.best_bid() != ref.best_bid() or mine.best_ask() != ref.best_ask():
                fails.append((seed, step, cmd, "holat farq qiladi"))
                break
            if step % 50 == 0 and (mine.depth(BUY, 3) != ref.depth(BUY, 3) or mine.depth(SELL, 3) != ref.depth(SELL, 3)):
                fails.append((seed, step, cmd, "depth farq qiladi"))
                break
            if len(known) > 400:
                known = known[-200:]
    check(f"40 ta tasodifiy ketma-ketlik ({ops} buyruq): har qadamda hodisalar va kitob holati aynan bir xil",
          not fails, f"birinchi farq: seed={fails[0][0]}, qadam={fails[0][1]}, {fails[0][2]} -> {fails[0][3]}"
          if fails else f"{time.time() - t0:.1f} s")

    bad = []
    for seed in range(20):
        rng = random.Random(1000 + seed)
        bk = book_mod.Book(1)
        known, nxt = [], 1
        for step in range(800):
            cmd = rand_cmd(rng, known, nxt, 1, False)
            if cmd[0] == "new" and cmd[1].oid == nxt:
                nxt += 1
                known.append(cmd[1].oid)
            run_cmd(bk, cmd)
            bb, ba = bk.best_bid(), bk.best_ask()
            if bb is not None and ba is not None and bb >= ba:
                bad.append((seed, step, bb, ba))
                break
    check("kitob hech qachon 'kesishgan' holatda qolmaydi: best_bid < best_ask", not bad,
          f"seed={bad[0][0]}, qadam={bad[0][1]}: bid={bad[0][2]}, ask={bad[0][3]}" if bad else "")


# ============================================================ 3. determinizm
def part_replay():
    print("3. Determinizm: jurnalni qayta o'ynash")
    ok, detail = True, ""
    for seed in range(8):
        rng = random.Random(500 + seed)
        ex = Exchange(book_mod.Book)
        known, nxt = [], 1
        for _ in range(1500):
            cmd = rand_cmd(rng, known, nxt, 1, False)
            if cmd[0] == "new" and cmd[1].oid == nxt:
                nxt += 1
                known.append(cmd[1].oid)
            ex.handle(cmd)
        again = Exchange.replay(book_mod.Book, ex.journal)
        if again.events != ex.events or again.book.state() != ex.book.state() or again.updates != ex.updates:
            ok, detail = False, f"seed={seed}: qayta o'ynash boshqa natija berdi"
            break
    check("zaxira server jurnalni qayta o'ynab, aynan o'sha hodisalar, kitob va L2 oqimini oladi", ok, detail)


# ============================================================ 4. L2 oqimi
def mk_client():
    asked = []
    c = feed_mod.L2Client(lambda: asked.append(1))
    return c, asked


def gen_exchange(seed, n):
    rng = random.Random(seed)
    ex = Exchange(Naive)
    known, nxt = [], 1
    for _ in range(n):
        cmd = rand_cmd(rng, known, nxt, 1, False)
        if cmd[0] == "new" and cmd[1].oid == nxt:
            nxt += 1
            known.append(cmd[1].oid)
        ex.handle(cmd)
    return ex


def levels_at(updates, upto):
    bids, asks = {}, {}
    for u in updates:
        if u.seq > upto:
            break
        lv = bids if u.side == BUY else asks
        if u.qty:
            lv[u.price] = u.qty
        else:
            lv.pop(u.price, None)
    return bids, asks


def part_feed():
    print("4. L2 oqimi mijozi")
    ex = gen_exchange(7, 400)
    c, asked = mk_client()
    for u in ex.updates:
        c.on_update(u)
    snap = ex.snapshot()
    check("tartibli oqim: kitob nusxasi birja bilan bir xil, surat so'ralmaydi",
          (c.bids, c.asks, c.seq) == (snap.bids, snap.asks, snap.seq) and not asked,
          f"seq={c.seq}/{snap.seq}, so'rovlar={len(asked)}")

    # bo'shliq: 1..10 keldi, 11-12 yo'qoldi, 13..20 keldi; surat 16 da olindi
    ups = ex.updates
    c, asked = mk_client()
    for u in ups[:10]:
        c.on_update(u)
    for u in ups[12:20]:
        c.on_update(u)
    b16, a16 = levels_at(ups, 16)
    c.on_snapshot(Snapshot(16, dict(b16), dict(a16)))
    b20, a20 = levels_at(ups, 20)
    got1 = (c.bids, c.asks, c.seq) == (b20, a20, 20) and len(asked) == 1
    for u in ups[20:30]:
        c.on_update(u)
    b30, a30 = levels_at(ups, 30)
    check("bo'shliq: surat so'raladi, kutish paytidagi xabarlar saqlanadi; suratdan eskilari tashlanadi, "
          "yangilari qo'llanadi", got1 and (c.bids, c.asks, c.seq) == (b30, a30, 30),
          f"seq={c.seq}, so'rovlar={len(asked)}")

    c, asked = mk_client()
    for u in ups[:30]:
        c.on_update(u)
    for u in ups[5:25]:
        c.on_update(u)          # eski takrorlar
    check("takror va eski xabarlar e'tiborsiz qoldiriladi (absolyut qiymat eskisi — xavfli)",
          (c.bids, c.asks, c.seq) == (b30, a30, 30) and not asked, f"seq={c.seq}")

    c, asked = mk_client()
    for u in ups[:10]:
        c.on_update(u)
    for u in ups[14:20]:
        c.on_update(u)          # 11-14 yo'q -> surat so'raladi
    b12, a12 = levels_at(ups, 12)
    c.on_snapshot(Snapshot(12, dict(b12), dict(a12)))   # surat 12 da; 13-14 hali yo'q
    n1 = len(asked)
    b25, a25 = levels_at(ups, 25)
    c.on_snapshot(Snapshot(25, dict(b25), dict(a25)))
    check("suratdan keyin ham bo'shliq qolsa — yana surat so'raladi", n1 == 2 and (c.bids, c.asks, c.seq)
          == (b25, a25, 25), f"so'rovlar={n1}, seq={c.seq}")

    fails = []
    for seed in range(30):
        ex = gen_exchange(100 + seed, 700)
        rng = random.Random(seed)
        c, asked = mk_client()
        pending_snap = []
        net = []
        truth = {}
        bids, asks = {}, {}
        for u in ex.updates:
            lv = bids if u.side == BUY else asks
            if u.qty:
                lv[u.price] = u.qty
            else:
                lv.pop(u.price, None)
            truth[u.seq] = (dict(bids), dict(asks))
        truth[0] = ({}, {})
        i = 0
        ups = ex.updates
        wrong = None
        while i < len(ups) or net or pending_snap:
            if i < len(ups):
                u = ups[i]
                i += 1
                x = rng.random()
                if x < 0.02:
                    pass                               # yo'qoldi
                elif x < 0.04:
                    net += [u, u]                      # takror
                else:
                    net.append(u)
                if len(net) > 1 and rng.random() < 0.05:
                    net[-1], net[-2] = net[-2], net[-1]   # tartib buzildi
            if net and (rng.random() < 0.8 or i >= len(ups)):
                c.on_update(net.pop(0))
            while asked:
                asked.pop()
                pending_snap.append(rng.randint(2, 15))
            pending_snap = [d - 1 for d in pending_snap]
            if pending_snap and pending_snap[0] <= 0:
                pending_snap.pop(0)
                s = ups[i - 1].seq if i else 0
                c.on_snapshot(Snapshot(s, dict(truth[s][0]), dict(truth[s][1])))
            if not getattr(c, "waiting", False) and c.seq in truth and (c.bids, c.asks) != truth[c.seq]:
                wrong = f"seq={c.seq} da nusxa noto'g'ri"
                break
        if wrong is None:
            # oxirgi xabarlar yo'qolgan bo'lishi mumkin: birja oxirgisini qayta yuboradi
            # (haqiqatda — "heartbeat" xabaridagi seq), mijoz bo'shliqni ko'radi
            last = ups[-1].seq
            c.on_update(ups[-1])
            while asked:
                asked.pop()
                c.on_snapshot(Snapshot(last, dict(truth[last][0]), dict(truth[last][1])))
            if (c.bids, c.asks, c.seq) != (truth[last][0], truth[last][1], last):
                wrong = f"oxirida seq={c.seq}/{last}, nusxa mos emas"
        if wrong:
            fails.append((seed, wrong))
    check("30 ta 'yomon tarmoq' stsenariysi (2% yo'qolish, 2% takror, tartib buzilishi, kechikkan suratlar): "
          "sinxron paytda nusxa har doim birja bilan bir xil", not fails,
          f"seed={fails[0][0]}: {fails[0][1]}" if fails else "")


# ============================================================ 5. tezlik
def part_speed():
    print("5. Tezlik")
    rng = random.Random(42)
    bk = book_mod.Book(1)
    for i in range(1, 20001):
        side = BUY if i % 2 else SELL
        p = rng.randint(500, 1000) if side == BUY else rng.randint(1001, 1500)
        bk.submit(Order(i, f"m{i % 50}", side, rng.randint(1, 100), p))
    cmds = []
    oid = 20001
    live = list(range(1, 20001))
    for _ in range(200000):
        r = rng.random()
        if r < 0.3:
            cmds.append(("cancel", live[rng.randrange(len(live))]))
        elif r < 0.4:
            cmds.append(("modify", live[rng.randrange(len(live))], rng.randint(1, 50), None))
        else:
            side = rng.choice([BUY, SELL])
            p = rng.randint(990, 1010)
            cmds.append(("new", Order(oid, f"t{oid % 97}", side, rng.randint(1, 100), p,
                                      IOC if rng.random() < 0.2 else GTC)))
            live.append(oid)
            oid += 1
    t0 = time.time()
    done = 0
    for cmd in cmds:
        run_cmd(bk, cmd)
        done += 1
        if done % 1000 == 0 and time.time() - t0 > 6.0:
            break
    dt = time.time() - t0
    check(f"20 000 buyurtmali kitobda 200 000 buyruq 6 soniyadan tez ({done / max(dt, 1e-9):,.0f} buyruq/s)",
          done == len(cmds) and dt < 6.0,
          f"{dt:.2f} s" if done == len(cmds) else f"6 s da faqat {done} ta buyruq bajarildi")


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
    units_ok = run(part_units) and all(results)
    if units_ok:
        run(part_fuzz)
        run(part_replay)
    else:
        print("2-3. O'tkazib yuborildi: avval kitobning birlik testlari to'liq o'tsin")
        results.append(False)
    run(part_feed)
    if units_ok:
        run(part_speed)
    else:
        print("5. O'tkazib yuborildi")
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
