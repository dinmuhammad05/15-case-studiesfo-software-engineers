"""ot.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Uch qism: (1) aniq holatlar — darsdagi misollar; (2) tasodifiy xususiyat
testlari (TP1, compose, kursor); (3) to'liq Jupiter simulyatsiyasi
(sim.py) — yuzlab stsenariyda yaqinlashish va "hech narsa yo'qolmadi".
"""
import random
import sys
import time

import ot
import sim

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def safe(fn, *a):
    try:
        return fn(*a)
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return f"XATO {type(e).__name__}: {e}"


def holds(fn):
    """Tekshiruv ifodasi: istisno ham FAIL hisoblanadi."""
    try:
        return bool(fn())
    except NotImplementedError:
        raise
    except Exception:  # noqa: BLE001
        return False


def random_op(rng, doc):
    """Bir nechta joyda o'zgarish qiladigan tasodifiy operatsiya."""
    op, i, n = [], 0, len(doc)
    while i < n:
        r = rng.random()
        k = rng.randint(1, max(1, min(4, n - i)))
        if r < 0.5:
            op.append(k)
        elif r < 0.75:
            op.append(-k)
        else:
            op.append("".join(rng.choice("xyzXYZ") for _ in range(rng.randint(1, 3))))
            continue
        i += k
    if rng.random() < 0.3:
        op.append(rng.choice("pq") * rng.randint(1, 2))
    return ot.normalize(op)


def unit_tests():
    print("1. Aniq holatlar (darsdagi misollar)")
    check("apply: qo'shish va o'chirish",
          safe(ot.apply, "salom dunyo", [5, ",", 6]) == "salom, dunyo"
          and safe(ot.apply, "abc", [1, -1, 1]) == "ac")
    try:
        ot.apply("abc", [2, "x"])
        raised = False
    except ValueError:
        raised = True
    check("apply: uzunlik mos kelmasa ValueError (6.2 validatsiya)", raised)

    d, a, b = "abc", [1, "X", 2], [2, -1]                     # 2.2 va 5-bo'lim, 3-qadam
    r = safe(ot.transform, a, b)
    ok = holds(lambda: ot.apply(ot.apply(d, a), r[1]) == "aXb"
               and ot.apply(ot.apply(d, b), r[0]) == "aXb")
    check("2.2 misoli: ikkala tomonda 'aXb'", ok, "" if ok else str(r))

    r = safe(ot.transform, [1, "X", 1], [1, "Y", 1])
    ok = holds(lambda: ot.apply("aXb", r[1]) == "aXYb" and ot.apply("aYb", r[0]) == "aXYb")
    check("bir joyga qo'shish: a oldinda ('aXYb')", ok, "" if ok else str(r))

    r = safe(ot.transform, [2, "X", 4], [1, -4, 1])           # qo'shish o'chirish ichida
    ok = holds(lambda: ot.apply(ot.apply("abcdef", [2, "X", 4]), r[1]) == "aXf")
    check("o'chirilayotgan oraliq ichidagi qo'shish saqlanadi ('aXf')", ok, "" if ok else str(r))

    r = safe(ot.transform, [1, -3, 2], [2, -3, 1])            # ustma-ust o'chirishlar
    ok = holds(lambda: ot.apply(ot.apply("abcdef", [1, -3, 2]), r[1]) == "af"
               and ot.apply(ot.apply("abcdef", [2, -3, 1]), r[0]) == "af")
    check("ustma-ust o'chirish: umumiy qism bir marta ('af')", ok, "" if ok else str(r))

    c = safe(ot.compose, [3, "d"], [-1, 3])
    check("compose: 'abc' -> 'abcd' -> 'bcd'", holds(lambda: ot.apply("abc", c) == "bcd"), str(c))

    cur = [safe(ot.transform_cursor, 5, op) for op in
           ([2, "abc", 8], [5, "abc", 5], [7, "abc", 3], [1, -2, 7], [3, -4, 3], [6, -2, 2])]
    check("transform_cursor: oldin/aynan/keyin qo'shish, oldin/ichida/keyin o'chirish",
          cur == [8, 8, 5, 3, 3, 5], str(cur))

    big = 1_000_000
    t0 = time.perf_counter()
    ok = holds(lambda: all(ot.transform([big, "x"], [5, -1, big - 6, "y"]) for _ in range(200)))
    dt = (time.perf_counter() - t0) / 200 * 1e6
    check("1 M belgili hujjatda transform uzunlikdan mustaqil (6.1)", ok and dt < 200,
          f"{dt:.1f} mks bitta transform")


def property_tests():
    print("\n2. Tasodifiy xususiyat testlari")
    rng = random.Random(7)
    bad_tp1 = bad_norm = 0
    first = None
    for _ in range(20_000):
        d = "".join(rng.choice("abcdef") for _ in range(rng.randint(0, 10)))
        a, b = random_op(rng, d), random_op(rng, d)
        try:
            a2, b2 = ot.transform(a, b)
            same = ot.apply(ot.apply(d, a), b2) == ot.apply(ot.apply(d, b), a2)
        except NotImplementedError:
            raise
        except Exception:  # noqa: BLE001 — xato ham buzilish
            a2, b2, same = [], [], False
        if not same:
            bad_tp1 += 1
            first = first or (d, a, b, a2, b2)
        if ot.normalize(a2) != a2 or ot.normalize(b2) != b2:
            bad_norm += 1
    check("TP1: 20 000 tasodifiy juftlik", bad_tp1 == 0,
          f"{bad_tp1} ta buzilish" + (f"; birinchisi: d={first[0]!r} a={first[1]} b={first[2]}" if first else ""))
    check("transform natijalari normalize qilingan", bad_norm == 0, f"{bad_norm} ta")

    bad = 0
    for _ in range(5_000):
        d = "".join(rng.choice("abcdef") for _ in range(rng.randint(0, 10)))
        a = random_op(rng, d)
        b = random_op(rng, ot.apply(d, a))
        if safe(ot.apply, d, safe(ot.compose, a, b)) != ot.apply(ot.apply(d, a), b):
            bad += 1
    check("compose: 5 000 tasodifiy juftlik", bad == 0, f"{bad} ta buzilish")

    bad = 0
    for _ in range(5_000):
        d = "".join(rng.choice("abcdef") for _ in range(rng.randint(1, 10)))
        pos = rng.randint(0, len(d))
        op = random_op(rng, d)
        new = safe(ot.transform_cursor, pos, op)
        after = ot.apply(d, op)
        if not isinstance(new, int) or not (0 <= new <= len(after)):
            bad += 1
    check("transform_cursor natijasi har doim matn ichida", bad == 0, f"{bad} ta")


def sim_tests():
    print("\n3. Jupiter simulyatsiyasi (sim.py)")
    for clients, seeds, label in ((2, 150, "2 mijoz"), (3, 150, "3 mijoz"), (5, 100, "5 mijoz")):
        bad, rev, tr = 0, 0, 0
        for s in range(seeds):
            try:
                res = sim.run(1000 * clients + s, clients=clients, steps=250)
            except NotImplementedError:
                raise
            except Exception:  # noqa: BLE001
                bad += 1
                continue
            rev += res["revisions"]
            tr += res["transforms"]
            bad += not res["ok"]
        check(f"yaqinlashish, {label}: {seeds} stsenariy", bad == 0,
              f"{bad} ta ajralish/xato; o'rtacha k = {tr / max(1, rev):.2f}")

    bad = 0
    for s in range(80):
        try:
            res = sim.run(50_000 + s, clients=4, steps=250, tokens_mode=True)
        except NotImplementedError:
            raise
        except Exception:  # noqa: BLE001
            bad += 1
            continue
        text = res["server"]
        if not res["ok"] or any(text.count(f"[{i}]") != 1 for i in range(1, res["tokens"] + 1)):
            bad += 1
    check("faqat qo'shish: har token aynan bir marta (hech narsa yo'qolmadi, takrorlanmadi)",
          bad == 0, f"{bad} ta stsenariyda buzilish")


def main():
    t0 = time.time()
    try:
        unit_tests()
        property_tests()
        sim_tests()
    except NotImplementedError:
        sys.exit("\not.py da TODO qolgan — funksiyalarni yozing.")
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} OK   ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
