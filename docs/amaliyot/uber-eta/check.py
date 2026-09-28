"""eta.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Uch qism: (1) qidiruv — Dijkstra, A* va ikki tomonlama qidiruv mustaqil
"orakul" bilan solishtiriladi, yo'llar haqiqiyligi va ko'rilgan tugunlar
soni tekshiriladi; (2) jonli tezliklar — shovqin, eskirgan va imkonsiz
kuzatuvlar, bitta "spamchi" haydovchi, tarix bilan aralashtirish;
(3) qoldiq modeli — aniqlik, siljish (bias) va kam ma'lumotli zonalar.
"""
import math
import random
import statistics
import sys
import time
from collections import deque

import city
import eta

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


def oracle(g, s, w):
    """Mustaqil tekshiruvchi: navbatli yorliq-tuzatish (Bellman-Ford oilasi).
    Sekinroq, lekin Dijkstra'dan butunlay boshqa g'oya."""
    dist = [math.inf] * g.n
    dist[s] = 0.0
    q, inq = deque([s]), [False] * g.n
    inq[s] = True
    while q:
        u = q.popleft()
        inq[u] = False
        du = dist[u]
        for v, e in g.adj[u]:
            nd = du + w[e]
            if nd < dist[v] - 1e-12:
                dist[v] = nd
                if not inq[v]:
                    inq[v] = True
                    q.append(v)
    return dist


def path_time(g, path, w):
    """Yo'l haqiqiymi (har qo'shni juftlik orasida qirra bor) va uning vaqti."""
    total = 0.0
    for a, b in zip(path, path[1:]):
        best = min((w[e] for v, e in g.adj[a] if v == b), default=None)
        if best is None:
            return None
        total += best
    return total


def close(a, b, eps=1e-6):
    return abs(a - b) <= eps * max(1.0, abs(b))


def unpack(res):
    if not (isinstance(res, tuple) and len(res) == 3):
        return None
    return res


# ------------------------------------------------------------- 1. qidiruv

def part_search(g, w):
    print("1. Eng tez yo'l: Dijkstra, A*, ikki tomonlama")
    vmax = g.vmax()
    algos = {
        "dijkstra": lambda s, t: eta.dijkstra(g, s, t, w),
        "astar": lambda s, t: eta.astar(g, s, t, w, vmax),
        "bidirectional": lambda s, t: eta.bidirectional(g, s, t, w),
    }

    s0 = g.idx[5, 5]
    same = {name: attempt(f, s0, s0) for name, f in algos.items()}
    check("s == t: vaqt 0, yo'l [s]",
          all(r and unpack(r) and r[0] == 0 and r[1] == [s0] for r, _ in same.values()),
          "; ".join(f"{k}: {e}" for k, (r, e) in same.items() if e))
    unr = {name: attempt(f, s0, g.island) for name, f in algos.items()}
    check("yetib bo'lmaydigan tugun: math.inf va []",
          all(r and unpack(r) and r[0] == math.inf and r[1] == [] for r, _ in unr.values()),
          "; ".join(f"{k}: {e}" for k, (r, e) in unr.items() if e))
    reach = g.n - 1  # orol tugundan boshqa hamma tugun
    cnt = {k: (r[2] if r and unpack(r) else None) for k, (r, _) in unr.items()}
    check("o'rnatilgan tugunlar to'g'ri sanaladi: yetib bo'lmasa — hamma yetiladigan tugun, bir martadan",
          cnt["dijkstra"] == reach and cnt["astar"] == reach, f"Dijkstra {cnt['dijkstra']}, A* {cnt['astar']}, kutilgan {reach}")

    # Ikki tomonlama qidiruvning klassik tuzog'i: birinchi uchrashuv nuqtasi (x)
    # eng qisqa yo'lda emas. s-x-t = 6, s-y-z-t = 5.5.
    tg = city.Graph()
    S, X, Y, Z, T = (tg.add_node(float(i), 0.0) for i in range(5))
    for a, b, sec in ((S, X, 3.0), (X, T, 3.0), (S, Y, 2.0), (Y, Z, 1.5), (Z, T, 2.0)):
        tg.add_edge(a, b, 30.0, "kichik")
    tw = [3.0, 3.0, 2.0, 1.5, 2.0]
    res, err = attempt(eta.bidirectional, tg, S, T, tw)
    check("Ikki tomonlama: birinchi uchrashuvda to'xtash tuzog'i (to'g'ri javob 5.5 s, s-y-z-t)",
          res and unpack(res) and close(res[0], 5.5) and res[1] == [S, Y, Z, T],
          err or (f"{res[0]} s, yo'l {res[1]}" if res else ""))

    rng = random.Random(11)
    nodes = [u for u in range(g.n) if u != g.island]
    sources = rng.sample(nodes, 10)
    pairs = []
    for s in sources:
        d = oracle(g, s, w)
        for t in rng.sample(nodes, 14):
            pairs.append((s, t, d[t]))

    stats = {name: {"bad": [], "settled": 0} for name in algos}
    dij_settled_long = 0
    long_settled = {name: 0 for name in algos}
    for s, t, truth in pairs:
        for name, f in algos.items():
            res, err = attempt(f, s, t)
            r = unpack(res) if res is not None else None
            if r is None:
                stats[name]["bad"].append((s, t, err or "natija (vaqt, yo'l, soni) emas"))
                continue
            tm, path, settled = r
            pt = path_time(g, path, w) if path else None
            ok = close(tm, truth) and path and path[0] == s and path[-1] == t and pt is not None and close(pt, tm)
            if not ok:
                stats[name]["bad"].append((s, t, f"{tm:.1f} s, to'g'risi {truth:.1f} s"))
            if truth > 900:
                long_settled[name] += settled
    n_long = sum(1 for p in pairs if p[2] > 900)

    for name, label in (("dijkstra", "Dijkstra"), ("astar", "A*"), ("bidirectional", "Ikki tomonlama")):
        bad = stats[name]["bad"]
        check(f"{label}: {len(pairs)} juftlikda vaqt va yo'l to'g'ri", not bad,
              f"{len(bad)} xato, birinchisi {bad[0]}" if bad else "")

    d0 = long_settled["dijkstra"] or 1
    ra, rb = long_settled["astar"] / d0, long_settled["bidirectional"] / d0
    check("A* uzun safarlarda kamroq tugun ko'radi (<= 75% Dijkstra)", ra <= 0.75 and not stats["astar"]["bad"],
          f"{n_long} ta uzun safar, nisbat {ra:.2f}")
    check("Ikki tomonlama kamroq tugun ko'radi (<= 75% Dijkstra)", rb <= 0.75 and not stats["bidirectional"]["bad"],
          f"nisbat {rb:.2f}")

    # daryo: yaqin, lekin ko'prik orqali
    a, b = g.idx[20, g.river_row], g.idx[20, g.river_row + 1]
    res, err = attempt(eta.dijkstra, g, a, b, w)
    straight = g.dist(a, b) / (30 * city.KMH)
    check("Daryo: 200 m, lekin ko'prik orqali — to'g'ri chiziqdan ko'p barobar uzoq",
          res and unpack(res) and res[0] > 5 * straight, err or (f"{res[0]:.0f} s vs to'g'ri chiziq {straight:.0f} s" if res else ""))


# ------------------------------------------------------- 2. jonli tezliklar

def part_live(g):
    print("2. Jonli tezliklar: GPS o'tishlaridan og'irliklargacha")
    now = 100_000.0
    obs, truth, cases = city.make_observations(g, now)
    hist = list(g.kmh)
    out, err = attempt(eta.live_speeds, g, obs, now, hist)
    if out is None or len(out) != g.m:
        check("live_speeds har qirra uchun qiymat qaytaradi", False, err or "uzunlik noto'g'ri")
        return None
    seen = set(o[0] for o in obs)
    check("Kuzatuvsiz qirralar — aynan tarixiy tezlik",
          all(out[e] == hist[e] for e in range(g.m) if e not in seen))

    e, v = cases["single"]
    k = 5.0
    check("Bitta kuzatuv: (1 x jonli + k x tarix) / (1 + k)", close(out[e], (v + k * hist[e]) / (1 + k), 1e-6),
          f"{out[e]:.3f} vs {(v + k * hist[e]) / (1 + k):.3f}")
    bad = [name for name in ("stale", "impossible", "future") if not close(out[cases[name][0]], hist[cases[name][0]], 1e-9)]
    check("Eskirgan, kelajakdagi va imkonsiz (>160 km/soat) kuzatuvlar hisobga olinmaydi", not bad,
          f"buzilgan: {bad}" if bad else "")
    e, v = cases["spam"]
    want = (4 * v + k * hist[e]) / (4 + k)
    check("Bitta haydovchining 10 ta sekin kuzatuvi natijani egallamaydi (haydovchi bo'yicha mediana)",
          abs(out[e] - want) / want < 0.03, f"{out[e]:.1f} vs kutilgan ~{want:.1f} km/soat")

    drivers = {}
    for ed, secs, d, ts in obs:
        if now - 600 <= ts <= now:
            drivers.setdefault(ed, set()).add(d)
    busy = [ed for ed, ds in drivers.items() if len(ds) >= 15]
    errs = []
    for ed in busy:
        n = len(drivers[ed])
        want = (n * truth[ed] + k * hist[ed]) / (n + k)
        errs.append(abs(out[ed] - want) / want)
    good = sum(1 for x in errs if x < 0.08) / max(1, len(errs))
    check(f"Gavjum qirralar ({len(busy)} ta, 15+ haydovchi): 90%+ i 8% aniqlikda — 15% 'to'xtagan' kuzatuvlarga qaramay",
          good >= 0.9, f"{good:.0%}")
    return out, truth


def part_route_live(g, live, truth):
    rng = random.Random(21)
    w_hist, w_live, w_true = g.weights(), g.weights(live), g.weights(truth)
    nodes = [u for u in range(g.n) if u != g.island]
    e_hist, e_live = [], []
    for _ in range(40):
        s, t = rng.sample(nodes, 2)
        rh, rl = eta.dijkstra(g, s, t, w_hist), eta.dijkstra(g, s, t, w_live)
        th, tl = path_time(g, rh[1], w_true), path_time(g, rl[1], w_true)
        e_hist.append(abs(rh[0] - th) / th)
        e_live.append(abs(rl[0] - tl) / tl)
    mh, ml = statistics.mean(e_hist), statistics.mean(e_live)
    check("Jonli og'irliklar bilan ETA haqiqatga yaqinroq (xato kamida 30% kam)", ml <= 0.7 * mh,
          f"tarixiy {mh:.1%} -> jonli {ml:.1%}")


# ---------------------------------------------------------- 3. qoldiq modeli

def part_residual():
    print("3. Qoldiq modeli: marshrut ETA xatosini tuzatish")
    train, test = city.make_trips(40_000, seed=3), city.make_trips(8_000, seed=4)
    model, err = attempt(eta.fit_residual, train)
    if err:
        check("fit_residual ishlaydi", False, err)
        return
    preds = []
    for tr in test:
        p, err = attempt(eta.predict, model, tr["route_s"], tr["hour"], tr["zone"])
        if err or p is None or not math.isfinite(p):
            check("predict har safar uchun son qaytaradi", False, err or str(p))
            return
        preds.append(p)
    raw = statistics.mean(abs(t["actual_s"] - t["route_s"]) for t in test)
    mae = statistics.mean(abs(t["actual_s"] - p) for t, p in zip(test, preds))
    check("Xato (MAE) marshrut ETA siga nisbatan kamida 45% kam", mae <= 0.55 * raw,
          f"{raw:.0f} s -> {mae:.0f} s ({1 - mae / raw:.0%})")
    ratio = statistics.median(p / t["actual_s"] for t, p in zip(test, preds))
    check("Siljish yo'q: bashorat/haqiqat medianasi 0.97-1.03 (chiqib ketishlarga qaramay)", 0.97 <= ratio <= 1.03,
          f"{ratio:.3f}")
    a = eta.predict(model, 1000.0, 8, "z9")
    b = eta.predict(model, 1000.0, 3, "z9")
    check("Cho'qqi soat (08:00) tungi (03:00) dan kamida 35% uzun", a >= 1.35 * b, f"{a:.0f} s vs {b:.0f} s")
    y = [eta.predict(model, 1000.0, h, "z_yangi") for h in range(24)]
    u = [eta.predict(model, 1000.0, h, "zona_yoq") for h in range(24)]
    check("Kam ma'lumotli va noma'lum zona — soat darajasiga tushadi (cho'qqi soat baribir uzun)",
          all(close(p, q) for p, q in zip(y, u)) and u[8] >= 1.25 * u[3], f"08:00 {u[8]:.0f} s, 03:00 {u[3]:.0f} s")


def main():
    t0 = time.time()
    g = city.make_city()
    w = g.weights()
    try:
        part_search(g, w)
        live = part_live(g)
        if live is not None and all(results):
            part_route_live(g, *live)
        part_residual()
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
        results.append(False)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
