"""store.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Uch qism: (1) Reed-Solomon — generator, tizimli kodlash, istalgan k ta
bo'lakdan tiklash, tezlik; (2) ob'ekt ombori — joylashtirish qoidalari,
disk va butun AZ o'limi, jim buzilish; (3) scrub — buzilgan bo'laklarni
topib, to'liq himoyani tiklash.
"""
import itertools
import math
import random
import sys
import time
import zlib

import cluster
import gf
import store

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def attempt(fn, *a):
    try:
        return fn(*a), None
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def rnd(rng, n):
    return bytes(rng.getrandbits(8) for _ in range(n))


# ---------------------------------------------------------- 1. Reed-Solomon

def part_rs():
    print("1. Reed-Solomon: kodlash va istalgan k ta bo'lakdan tiklash")
    G, err = attempt(store.generator, 4, 2)
    ok = G is not None and len(G) == 6 and all(len(r) == 4 for r in G) and all(
        G[i][j] == (1 if i == j else 0) for i in range(4) for j in range(4))
    check("generator(4, 2): 6 qator, birinchi 4 tasi birlik matritsa", ok, err or "")
    bad = []
    if ok:
        for rows in itertools.combinations(range(6), 4):
            try:
                gf.mat_inv([G[i] for i in rows])
            except ValueError:
                bad.append(rows)
    G8, err8 = attempt(store.generator, 8, 4)
    if G8 is not None and len(G8) == 12:
        for rows in itertools.combinations(range(12), 8):
            try:
                gf.mat_inv([G8[i] for i in rows])
            except ValueError:
                bad.append(rows)
    check("istalgan k ta qatordan tuzilgan matritsa teskarilanadi ((4,2) va (8,4): 15 + 495 kombinatsiya)",
          ok and G8 is not None and not bad, err8 or (f"teskarilanmaydi: {bad[:2]}" if bad else ""))

    rng = random.Random(1)
    data = rnd(rng, 1001)
    sh, err = attempt(store.encode, data, 4, 2)
    L = math.ceil(1001 / 4)
    ok = sh is not None and len(sh) == 6 and all(len(x) == L for x in sh) and b"".join(sh[:4])[:1001] == data
    check("encode: 6 ta teng bo'lak (to'ldirish bilan), birinchi 4 tasi — ma'lumotning o'zi", ok, err or "")

    fails = []
    for k, m, sizes in ((4, 2, (0, 1, 5, 1000, 4097)), (6, 3, (1, 777, 12345))):
        for size in sizes:
            d = rnd(rng, size)
            shards, err = attempt(store.encode, d, k, m)
            if err:
                fails.append((k, m, size, err))
                continue
            for keep in itertools.combinations(range(k + m), k):
                got, err = attempt(store.decode, {i: shards[i] for i in keep}, k, m, size)
                if got != d:
                    fails.append((k, m, size, keep, err))
                    break
    check("decode: har o'lchamda (0 baytdan 12 KB gacha) istalgan k ta bo'lakdan aniq tiklaydi",
          not fails, f"birinchi xato: {fails[0]}" if fails else "")

    shards = store.encode(b"salom dunyo", 4, 2)
    lost = False
    try:
        store.decode({0: shards[0], 1: shards[1], 5: shards[5]}, 4, 2, 11)
    except store.LostError:
        lost = True
    except Exception:  # noqa: BLE001
        lost = False
    check("k tadan kam bo'lak -> LostError", lost)

    big = rnd(random.Random(2), 1 << 20)
    t = time.time()
    sh = store.encode(big, 6, 3)
    back = store.decode({i: sh[i] for i in (1, 3, 5, 6, 7, 8)}, 6, 3, len(big))
    dt = time.time() - t
    check("1 MB: kodlash + 3 bo'laksiz tiklash 3 soniyadan tez (gf.scale va gf.xor bilan)",
          back == big and dt < 3.0, f"{dt:.2f} s")


# ------------------------------------------------------------ 2. ob'ekt ombori

def healthy(st, key):
    """(sog' bo'laklar soni, joylashtirish to'g'rimi) — indeks va disklar bo'yicha."""
    e = st.index[key]
    n_ok, disks = 0, []
    for did, cid, crc in e["shards"]:
        d = st.disks[did]
        disks.append(did)
        try:
            if zlib.crc32(d.read(cid)) == crc:
                n_ok += 1
        except (cluster.DiskDead, KeyError):
            pass
    alive_azs = {d.az for d in st.disks.values() if d.alive}
    cap = math.ceil(len(e["shards"]) / len(alive_azs))
    per_az = {}
    for did in disks:
        per_az[st.disks[did].az] = per_az.get(st.disks[did].az, 0) + 1
    distinct = len(set(disks)) == len(disks)
    return n_ok, distinct and max(per_az.values()) <= cap


def fresh(rng, n=120):
    disks = cluster.make_cluster()
    st = store.Store(disks, k=6, m=3)
    objs = {}
    for i in range(n):
        key = f"rasmlar/{i:04d}.jpg"
        objs[key] = rnd(rng, rng.choice([0, 1, 100, 3000, 20000]))
        st.put(key, objs[key])
    return disks, st, objs


def readable(st, objs):
    bad = []
    for key, data in objs.items():
        got, err = attempt(st.get, key)
        if got != data:
            bad.append((key, err or "noto'g'ri baytlar"))
    return bad


def part_store():
    print("2. Ob'ekt ombori: joylashtirish, disk va AZ o'limi, jim buzilish")
    rng = random.Random(3)
    res, err = attempt(fresh, rng)
    if err:
        check("put ishlaydi", False, err)
        return
    disks, st, objs = res
    check("put/get: 120 ob'ekt (0 baytdan 20 KB gacha) aniq qaytadi", not readable(st, objs))
    place_bad = [k for k in objs if not healthy(st, k)[1]]
    check("har ob'ekt: 9 bo'lak 9 xil diskda, har AZ da ko'pi bilan 3 ta", not place_bad,
          f"{len(place_bad)} ta buzilgan" if place_bad else "")
    used = [d.used for d in disks]
    check("disklar bir tekis to'ladi (eng ko'p / eng kam <= 1.5)", min(used) > 0 and max(used) / min(used) <= 1.5,
          f"{min(used)}..{max(used)} bayt")

    new = rnd(rng, 5000)
    st.put("rasmlar/0001.jpg", new)
    objs["rasmlar/0001.jpg"] = new
    check("qayta yozish: yangi versiya o'qiladi", st.get("rasmlar/0001.jpg") == new)
    missing = False
    try:
        st.get("yoq/kalit")
    except KeyError:
        missing = True
    check("mavjud bo'lmagan kalit -> KeyError", missing)

    for d in rng.sample(disks, 3):
        d.kill()
    bad = readable(st, objs)
    check("istalgan 3 ta disk o'ldi — hamma ob'ekt o'qiladi", not bad, f"{len(bad)} ta o'qilmadi: {bad[:1]}" if bad else "")

    rng2 = random.Random(4)
    disks, st, objs = fresh(rng2)
    for d in disks:
        if d.az == "az-b":
            d.kill()
    bad = readable(st, objs)
    check("butun AZ (az-b, 6 disk) o'ldi — hamma ob'ekt o'qiladi", not bad, f"{len(bad)} ta o'qilmadi" if bad else "")

    rng3 = random.Random(5)
    disks, st, objs = fresh(rng3)
    victims = [k for k in objs if objs[k]][:40]
    for key in victims:
        e = st.index[key]
        for i in (0, 4):  # ikki bo'lak jim buziladi
            did, cid, _ = e["shards"][i]
            st.disks[did].corrupt(cid)
    rng3.choice(disks).kill()
    bad = readable(st, {k: objs[k] for k in victims})
    check("jim buzilish: 2 bo'lak o'zgargan + 1 disk o'lik — baribir to'g'ri baytlar (crc32 tekshiruvi)",
          not bad, f"{len(bad)} ta xato: {bad[:1]}" if bad else "")

    key = victims[0]
    e = st.index[key]
    for did, cid, _ in e["shards"][:4]:
        if st.disks[did].alive:
            st.disks[did].corrupt(cid, 1)
    for did, _, _ in e["shards"][4:6]:
        st.disks[did].kill()
    got, err = attempt(st.get, key)
    lost = err is not None and "LostError" in err
    check("sog' bo'lak k tadan kam — LostError, hech qachon noto'g'ri baytlar emas", lost and got is None,
          err or "baytlar qaytdi")


# ------------------------------------------------------------------ 3. scrub

def part_scrub():
    print("3. Scrub: buzilganlarni topish va to'liq himoyani tiklash")
    rng = random.Random(6)
    disks, st, objs = fresh(rng)
    for d in rng.sample(disks, 2):
        d.kill()
    keys = list(objs)
    for key in keys[:30]:
        did, cid, _ = st.index[key]["shards"][7]
        if st.disks[did].alive:
            st.disks[did].corrupt(cid)
    n, err = attempt(st.scrub)
    after = [healthy(st, k) for k in keys]
    full = sum(1 for ok, _ in after if ok == 9)
    placed = sum(1 for _, p in after if p)
    check("scrub: har ob'ektda yana 9 ta sog' bo'lak, tirik disklarda", n and full == len(keys),
          err or f"tiklandi {n} bo'lak; to'liq {full}/{len(keys)}")
    check("scrub: tiklangan bo'laklar ham joylashtirish qoidalariga mos", placed == len(keys), f"{placed}/{len(keys)}")
    n2, err = attempt(st.scrub)
    check("ikkinchi scrub hech narsa topmaydi (0)", n2 == 0, err or f"{n2}")
    for d in [d for d in disks if d.alive][:3]:
        d.kill()
    bad = readable(st, objs)
    check("scrub'dan keyin yana 3 disk o'ldi — hammasi o'qiladi (himoya haqiqatan tiklangan)",
          not bad, f"{len(bad)} ta o'qilmadi" if bad else "")

    rng = random.Random(7)
    disks, st, objs = fresh(rng, 60)
    for d in disks:
        if d.az == "az-c":
            d.kill()
    n, err = attempt(st.scrub)
    after = [healthy(st, k) for k in objs]
    check("butun AZ o'lgach scrub: qolgan 2 AZ da 9 ta bo'lak (har AZ da ko'pi bilan 5)",
          all(ok == 9 and p for ok, p in after), err or f"tiklandi {n}")


def main():
    t0 = time.time()
    try:
        part_rs()
        if all(results):
            part_store()
            part_scrub()
        else:
            print("2-3. O'tkazib yuborildi: avval Reed-Solomon qismi to'liq o'tsin")
            results.append(False)
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
        results.append(False)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
