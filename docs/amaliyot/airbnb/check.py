"""booking.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

To'rt qism: (1) tun modeli va kalendar qoidalari; (2) HOLD, idempotentlik,
to'lov va kitob; (3) qidiruv — sodda hisob bilan solishtirish; (4) bir
nechta jarayon bir vaqtda — ikki marta bron, ikki marta yechish va
kitobdagi takrorlar yo'qligi. Oxirida — rekonsilyatsiya (8.4): kitob va
provayder bir xil gapiryaptimi.
"""
import datetime as dt
import multiprocessing as mp
import os
import random
import shutil
import sys
import tempfile
import time

import booking
import db

T0 = 1_700_000_000.0
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def raises(exc, fn, *a):
    try:
        fn(*a)
    except NotImplementedError:
        raise
    except exc:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def attempt(fn, *a):
    """(natija, None) yoki (None, istisno nomi)."""
    try:
        return fn(*a), None
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return None, type(e).__name__


class Env:
    def __init__(self, tmp, name):
        self.path = os.path.join(tmp, name + ".db")
        self.conn = db.init(self.path)

    def listing(self, lid, nightly=10_000, cleaning=2_500, min_nights=1):
        self.conn.execute(
            "INSERT INTO listings(id, nightly_minor, cleaning_minor, min_nights) VALUES (?, ?, ?, ?)",
            (lid, nightly, cleaning, min_nights),
        )

    def q(self, sql, *a):
        return self.conn.execute(sql, a).fetchall()

    def state(self, bid):
        r = self.q("SELECT state FROM bookings WHERE id = ?", bid)
        return r[0][0] if r else None

    def nights_of(self, bid):
        return [r[0] for r in self.q("SELECT night FROM booked_nights WHERE booking_id = ? ORDER BY night", bid)]


def overlaps(env, now):
    """Mustaqil invariant tekshiruvchi (14.2): tunlar jadvaliga emas,
    bronlarning o'ziga qaraydi — faol bronlar oraliqlari kesishmasin."""
    rows = env.q(
        "SELECT a.id, b.id FROM bookings a JOIN bookings b "
        "ON a.listing_id = b.listing_id AND a.id < b.id "
        "AND a.check_in < b.check_out AND b.check_in < a.check_out "
        "WHERE (a.state = 'CONFIRMED' OR (a.state = 'HOLD' AND a.hold_expires_at > ?)) "
        "AND (b.state = 'CONFIRMED' OR (b.state = 'HOLD' AND b.hold_expires_at > ?))",
        now, now,
    )
    return [tuple(r) for r in rows]


def unbalanced(env):
    return env.q("SELECT txn_id, SUM(amount_minor) FROM ledger GROUP BY txn_id HAVING SUM(amount_minor) != 0")


# ---------------------------------------------------------------- 1. tunlar

def part_nights(tmp):
    print("1. Tun modeli va kalendar qoidalari")
    n = booking.nights
    ok = (n("2024-03-14", "2024-03-17") == ["2024-03-14", "2024-03-15", "2024-03-16"]
          and n("2024-02-27", "2024-03-02") == ["2024-02-27", "2024-02-28", "2024-02-29", "2024-03-01"]
          and n("2023-12-31", "2024-01-01") == ["2023-12-31"])
    check("yarim ochiq oraliq, kabisa yili, yil chegarasi", ok)
    check("noto'g'ri oraliqlar -> Invalid",
          all(raises(db.Invalid, n, a, b) for a, b in [
              ("2024-03-14", "2024-03-14"), ("2024-03-17", "2024-03-14"),
              ("2024-02-30", "2024-03-02"), ("2024-01-01", "2025-06-01")]))

    e = Env(tmp, "nights")
    e.listing(1)
    e.listing(2, min_nights=3)
    a, ea = attempt(booking.create_hold, e.conn, 1, 100, "2024-05-10", "2024-05-13", "k-a", T0)
    b, eb = attempt(booking.create_hold, e.conn, 1, 200, "2024-05-13", "2024-05-15", "k-b", T0)
    check("ketma-ket bronlar: chiqish kuni — keyingisining kirish kuni",
          a and b and e.nights_of(a) == ["2024-05-10", "2024-05-11", "2024-05-12"],
          ea or eb or "")
    before = (e.q("SELECT COUNT(*) FROM bookings")[0][0], e.q("SELECT COUNT(*) FROM booked_nights")[0][0])
    busy = raises(db.Busy, booking.create_hold, e.conn, 1, 300, "2024-05-08", "2024-05-11", "k-c", T0)
    after = (e.q("SELECT COUNT(*) FROM bookings")[0][0], e.q("SELECT COUNT(*) FROM booked_nights")[0][0])
    check("kesishgan bron -> Busy va bazada hech narsa qolmaydi (atomiklik)",
          busy and before == after, f"oldin {before}, keyin {after}")
    check("min_nights -> Invalid",
          raises(db.Invalid, booking.create_hold, e.conn, 2, 100, "2024-05-10", "2024-05-12", "k-d", T0)
          and not raises(Exception, booking.create_hold, e.conn, 2, 100, "2024-05-10", "2024-05-13", "k-e", T0))


# ------------------------------------------------- 2. HOLD, to'lov, kitob

def part_hold_payment(tmp):
    print("2. HOLD, idempotentlik, to'lov va kitob")
    e = Env(tmp, "hold")
    for lid in range(1, 10):
        e.listing(lid)
    ok_p = db.FakeProvider(e.path, "ok")

    a1, _ = attempt(booking.create_hold, e.conn, 1, 100, "2024-06-01", "2024-06-04", "idem-1", T0)
    a2, _ = attempt(booking.create_hold, e.conn, 1, 100, "2024-06-01", "2024-06-04", "idem-1", T0 + 5)
    check("bir xil kalit — bir xil bron, ikkinchi qator yo'q",
          a1 is not None and a1 == a2 and e.q("SELECT COUNT(*) FROM bookings")[0][0] == 1)
    check("bir xil kalit, boshqa sanalar -> IdemMismatch",
          raises(db.IdemMismatch, booking.create_hold, e.conn, 1, 100, "2024-06-02", "2024-06-04", "idem-1", T0))
    amount = e.q("SELECT amount_minor FROM bookings WHERE id = ?", a1)[0][0] if a1 else None
    check("HOLD: muddat va summa", a1 and e.state(a1) == "HOLD" and amount == 3 * 10_000 + 2_500
          and abs(e.q("SELECT hold_expires_at FROM bookings WHERE id=?", a1)[0][0] - (T0 + db.HOLD_TTL)) < 1e-6)

    # muddati o'tgan HOLD — expire_holds siz ham tunni band qilmaydi
    late = T0 + db.HOLD_TTL + 1
    b, eb = attempt(booking.create_hold, e.conn, 1, 200, "2024-06-03", "2024-06-05", "idem-2", late)
    check("muddati o'tgan HOLD tunlarni band qilmaydi (expire_holds kutilmaydi)",
          b is not None and e.state(a1) == "EXPIRED" and e.nights_of(a1) == [], eb or "")
    st, _ = attempt(booking.confirm, e.conn, a1, ok_p, late)
    check("muddati o'tgan HOLD ni tasdiqlash -> EXPIRED, pul yechilmaydi",
          st == "EXPIRED" and "charge" not in ok_p.totals())

    # expire_holds
    h1, _ = attempt(booking.create_hold, e.conn, 2, 100, "2024-07-01", "2024-07-03", "idem-3", T0)
    h2, _ = attempt(booking.create_hold, e.conn, 3, 100, "2024-07-01", "2024-07-03", "idem-4", T0 + 600)
    n, _ = attempt(booking.expire_holds, e.conn, T0 + db.HOLD_TTL + 10)
    check("expire_holds: faqat muddati o'tganlar", n is not None and n >= 1
          and e.state(h1) == "EXPIRED" and e.nights_of(h1) == [] and e.state(h2) == "HOLD"
          and e.state(b) == "HOLD" and len(e.nights_of(h2)) == 2, f"qaytardi {n}")

    # muvaffaqiyatli tasdiq va takroriy tasdiq
    c, _ = attempt(booking.create_hold, e.conn, 4, 100, "2024-08-01", "2024-08-05", "idem-5", T0)
    s1, _ = attempt(booking.confirm, e.conn, c, ok_p, T0 + 30)
    s2, _ = attempt(booking.confirm, e.conn, c, ok_p, T0 + 40)
    led = e.q("SELECT account, amount_minor FROM ledger WHERE booking_id = ? ORDER BY account", c)
    total = 4 * 10_000 + 2_500
    host, fee = db.split(total)
    check("confirm: CONFIRMED, bitta yechish, kitobda uchta yozuv",
          s1 == s2 == "CONFIRMED" and ok_p.totals().get("charge", (0, 0))[0] == 1
          and sorted(map(tuple, led)) == sorted([("guest_payments", -total), ("host_payable", host), ("platform_fees", fee)]),
          f"kitob: {[tuple(r) for r in led]}")

    # rad etilgan to'lov
    d, _ = attempt(booking.create_hold, e.conn, 5, 100, "2024-08-01", "2024-08-03", "idem-6", T0)
    sd, _ = attempt(booking.confirm, e.conn, d, db.FakeProvider(e.path, "decline"), T0 + 30)
    check("rad etilgan to'lov -> EXPIRED, tunlar bo'sh, kitob bo'sh",
          sd == "EXPIRED" and e.nights_of(d) == [] and not e.q("SELECT 1 FROM ledger WHERE booking_id=?", d))

    # taymaut: pul yechildi, javob yo'qoldi
    t, _ = attempt(booking.create_hold, e.conn, 6, 100, "2024-08-01", "2024-08-03", "idem-7", T0)
    got_timeout = raises(db.Timeout, booking.confirm, e.conn, t, db.FakeProvider(e.path, "timeout"), T0 + 30)
    mid = e.state(t)
    st2, _ = attempt(booking.confirm, e.conn, t, ok_p, T0 + 60)
    charges = e.q("SELECT calls FROM provider_ops WHERE key = ?", f"charge:{t}")
    check("taymaut: HOLD saqlanadi, qayta urinish tasdiqlaydi, provayderda bitta yechish",
          got_timeout and mid == "HOLD" and st2 == "CONFIRMED" and len(charges) == 1 and charges[0][0] == 2,
          f"oraliq holat {mid}, yakun {st2}")

    # bekor qilish
    s3, _ = attempt(booking.cancel, e.conn, c, ok_p, T0 + 100)
    s4, _ = attempt(booking.cancel, e.conn, c, ok_p, T0 + 101)
    net = e.q("SELECT account, SUM(amount_minor) FROM ledger WHERE booking_id=? GROUP BY account", c)
    check("CONFIRMED ni bekor qilish: tunlar bo'sh, bitta qaytarish, kitob sof nol",
          s3 == "CANCELLED" and s4 == "CANCELLED" and e.nights_of(c) == []
          and ok_p.totals().get("refund", (0, 0))[0] == 1 and all(r[1] == 0 for r in net) and net)
    again, er = attempt(booking.create_hold, e.conn, 4, 300, "2024-08-02", "2024-08-04", "idem-8", T0 + 200)
    check("bekor qilingan bronning tunlari yana bron qilinadi", again is not None, er or "")
    check("kitobda muvozanatsiz tranzaksiya yo'q", not unbalanced(e))


# --------------------------------------------------------------- 3. qidiruv

def part_search(tmp):
    print("3. Qidiruv: sodda hisob bilan solishtirish")
    e = Env(tmp, "search")
    rng = random.Random(7)
    L = 120
    for lid in range(1, L + 1):
        e.listing(lid, min_nights=rng.choice([1, 1, 1, 2, 3]))
    base = dt.date(2024, 9, 1)
    now = T0 + 5_000
    made = 0
    provider = db.FakeProvider(e.path, "ok")
    confirm_ok = True  # confirm xato bersa, qolganlarini faqat HOLD bilan davom ettiramiz
    for i in range(700):
        lid = rng.randint(1, L)
        a = base + dt.timedelta(days=rng.randint(0, 60))
        n = rng.randint(3, 6)
        ci, co = a.isoformat(), (a + dt.timedelta(days=n)).isoformat()
        t = now - rng.choice([0, 100, 800, 2000, 4000])  # ba'zilari muddati o'tadi
        bid, err = attempt(booking.create_hold, e.conn, lid, i, ci, co, f"s-{i}", t)
        if bid is not None:
            made += 1
            if confirm_ok and rng.random() < 0.5:
                st, err = attempt(booking.confirm, e.conn, bid, provider, t + 1)
                confirm_ok = err is None
    rows = e.q("SELECT listing_id, check_in, check_out, state, hold_expires_at FROM bookings")
    mins = dict(e.q("SELECT id, min_nights FROM listings"))

    def brute(ci, co):
        n = (dt.date.fromisoformat(co) - dt.date.fromisoformat(ci)).days
        busy = {r[0] for r in rows
                if (r[3] == "CONFIRMED" or (r[3] == "HOLD" and r[4] > now)) and r[1] < co and ci < r[2]}
        return [lid for lid in range(1, L + 1) if lid not in busy and mins[lid] <= n]

    def snapshot():
        return (e.q("SELECT id, state FROM bookings ORDER BY id"),
                e.q("SELECT listing_id, night, booking_id FROM booked_nights ORDER BY 1, 2"))

    snap = [tuple(map(tuple, x)) for x in snapshot()]
    bad = []
    for _ in range(60):
        a = base + dt.timedelta(days=rng.randint(0, 65))
        n = rng.randint(1, 7)
        ci, co = a.isoformat(), (a + dt.timedelta(days=n)).isoformat()
        got, err = attempt(booking.search_available, e.conn, ci, co, now)
        if got != brute(ci, co):
            bad.append((ci, co, err))
    check(f"60 ta tasodifiy so'rov, {made} ta bron (muddati o'tgan HOLD lar bilan)",
          made > 100 and not bad, f"birinchi farq: {bad[0]}" if bad else "")
    check("qidiruv bazaga yozmaydi", [tuple(map(tuple, x)) for x in snapshot()] == snap)


# ------------------------------------------------------- 4. parallellik

def _worker(path, task, wid, rounds, barrier, out):
    conn = db.connect(path)
    rng = random.Random(1000 + wid)
    for r in range(rounds):
        barrier.wait()
        res = None
        try:
            if task == "race":
                a = dt.date(2025, 1, 1) + dt.timedelta(days=rng.randint(0, 3))
                ci, co = a.isoformat(), (a + dt.timedelta(days=rng.randint(2, 4))).isoformat()
                res = ("ok", booking.create_hold(conn, r + 1, wid, ci, co, f"race-{r}-{wid}", T0))
            elif task == "idem":
                res = ("ok", booking.create_hold(conn, r + 1, 7, "2025-02-01", "2025-02-04", f"same-{r}", T0))
            elif task == "confirm":
                res = ("ok", booking.confirm(conn, r + 1, db.FakeProvider(path, "ok"), T0 + 10))
            elif task == "cancel":
                res = ("ok", booking.cancel(conn, r + 1, db.FakeProvider(path, "ok"), T0 + 20))
        except db.Busy:
            res = ("busy", None)
        except Exception as e:  # noqa: BLE001
            res = ("err", f"{type(e).__name__}: {e}")
        out.put((task, r, wid, res))
    conn.close()


def run_parallel(path, task, workers, rounds):
    ctx = mp.get_context("fork" if "fork" in mp.get_all_start_methods() else "spawn")
    barrier = ctx.Barrier(workers)
    out = ctx.Queue()
    procs = [ctx.Process(target=_worker, args=(path, task, w, rounds, barrier, out)) for w in range(workers)]
    for p in procs:
        p.start()
    res = [out.get(timeout=120) for _ in range(workers * rounds)]
    for p in procs:
        p.join(timeout=30)
    return res


def part_parallel(tmp):
    W, R = 8, 60
    print(f"4. Parallellik: {W} jarayon, {R} raund, har raundda bir vaqtda")
    e = Env(tmp, "par")
    for lid in range(1, R + 1):
        e.listing(lid)

    res = run_parallel(e.path, "race", W, R)
    errs = [x for x in res if x[3][0] == "err"]
    wins = {}
    for task, r, wid, (kind, _) in res:
        wins.setdefault(r, 0)
        wins[r] += kind == "ok"
    ov = overlaps(e, T0 + 1)
    check("poyga: ikki marta bron yo'q (bronlar oraliqlari bo'yicha mustaqil tekshiruv)",
          not ov and not errs, f"kesishmalar: {len(ov)}; xatolar: {errs[:1]}")
    check("poyga: har raundda kamida bitta mehmon yutadi", all(v >= 1 for v in wins.values()))

    res = run_parallel(e.path, "idem", W, R)
    ids = {}
    for task, r, wid, (kind, val) in res:
        ids.setdefault(r, set()).add(val if kind == "ok" else kind)
    dup = e.q("SELECT idem_key, COUNT(*) FROM bookings WHERE idem_key LIKE 'same-%' GROUP BY idem_key HAVING COUNT(*) > 1")
    check("bir xil kalit bilan 8 ta parallel so'rov — bitta bron, hamma bir xil ID oladi",
          all(len(v) == 1 and None not in v and "err" not in v and "busy" not in v for v in ids.values()) and not dup)

    # confirm: har raundning bronlaridan birini (bor bo'lsa) bir vaqtda tasdiqlash
    e2 = Env(tmp, "par2")
    for lid in range(1, R + 1):
        e2.listing(lid)
        booking.create_hold(e2.conn, lid, 1, "2025-03-01", "2025-03-04", f"c-{lid}", T0)
    res = run_parallel(e2.path, "confirm", W, R)
    errs = [x for x in res if x[3][0] == "err"]
    txns = e2.q("SELECT booking_id, COUNT(DISTINCT id) FROM ledger GROUP BY booking_id")
    charges = e2.q("SELECT COUNT(*) FROM provider_ops WHERE kind='charge'")[0][0]
    check("8 ta parallel confirm: har bronga bitta yechish va aynan 3 kitob yozuvi",
          not errs and charges == R and len(txns) == R and all(t[1] == 3 for t in txns),
          f"yechishlar {charges}, xatolar {errs[:1]}")

    def reconcile(env):
        p = db.FakeProvider(env.path).totals()
        net_provider = p.get("charge", (0, 0))[1] - p.get("refund", (0, 0))[1]
        guest = env.q("SELECT COALESCE(SUM(amount_minor), 0) FROM ledger WHERE account='guest_payments'")[0][0]
        return net_provider, -guest

    rec1 = reconcile(e2)
    res = run_parallel(e2.path, "cancel", W, R)
    errs = [x for x in res if x[3][0] == "err"]
    refunds = e2.q("SELECT COUNT(*) FROM provider_ops WHERE kind='refund'")[0][0]
    check("8 ta parallel cancel: har bronga bitta qaytarish",
          not errs and refunds == R and not unbalanced(e2), f"qaytarishlar {refunds}, xatolar {errs[:1]}")

    # rekonsilyatsiya (8.4): provayder va kitob bir xil gapiradi
    rec2 = reconcile(e2)
    check("rekonsilyatsiya: provayderdagi sof pul == kitobdagi mehmon to'lovlari (tasdiqdan va bekordan keyin)",
          rec1[0] == rec1[1] and rec1[0] > 0 and rec2[0] == rec2[1], f"tasdiqdan keyin {rec1}, bekordan keyin {rec2}")


def main():
    tmp = tempfile.mkdtemp(prefix="airbnb-check-")
    t = time.time()
    try:
        part_nights(tmp)
        part_hold_payment(tmp)
        part_search(tmp)
        if all(results):
            part_parallel(tmp)
        else:
            print("4. Parallellik — o'tkazib yuborildi: avval 1-3 qismlar to'liq o'tsin")
            results.append(False)
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
        results.append(False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
