"""Sintetik shahar va ma'lumotlar (tayyor, o'zgartirmang).

Hamma narsa deterministik (seed bilan), faqat Python standart kutubxonasi.

  Graph      — yo'nalishli yo'l grafi: tugunlar (x, y metrlarda), qirralar
               (u, v, uzunlik m, tarixiy tezlik km/soat, yo'l turi)
  make_city  — ko'chalar to'ri: magistrallar, katta ko'chalar, bir tomonlama
               kichik ko'chalar, daryo va bir nechta ko'prik
  make_observations — map matching'dan keyingi bo'lak o'tishlari (jonli tezlik uchun)
  make_trips — marshrut ETA va haqiqiy vaqt juftliklari (qoldiq modeli uchun)
"""
import math
import random

KMH = 1000 / 3600  # 1 km/soat = 0.2777 m/s


class Graph:
    def __init__(self):
        self.x, self.y = [], []
        self.eu, self.ev, self.length, self.kmh, self.kind = [], [], [], [], []
        self.adj = []   # adj[u]  = [(v, edge_id), ...]   — chiquvchi qirralar
        self.radj = []  # radj[v] = [(u, edge_id), ...]   — kiruvchi qirralar (teskari qidiruv uchun)

    def add_node(self, x, y):
        self.x.append(x)
        self.y.append(y)
        self.adj.append([])
        self.radj.append([])
        return len(self.x) - 1

    def add_edge(self, u, v, kmh, kind, curve=1.0):
        e = len(self.eu)
        self.eu.append(u)
        self.ev.append(v)
        # uzunlik to'g'ri chiziqdan kichik emas (egrilik >= 1) — shuning uchun
        # evklid masofa / eng yuqori tezlik — optimistik baho
        self.length.append(self.dist(u, v) * curve)
        self.kmh.append(kmh)
        self.kind.append(kind)
        self.adj[u].append((v, e))
        self.radj[v].append((u, e))
        return e

    def dist(self, a, b):
        return math.hypot(self.x[a] - self.x[b], self.y[a] - self.y[b])

    @property
    def n(self):
        return len(self.x)

    @property
    def m(self):
        return len(self.eu)

    def weights(self, kmh=None):
        """Qirra og'irliklari soniyada: uzunlik / tezlik."""
        kmh = kmh or self.kmh
        return [self.length[e] / (kmh[e] * KMH) for e in range(self.m)]

    def vmax(self, kmh=None):
        return max(kmh or self.kmh)


SPEED = {"magistral": 80.0, "katta": 50.0, "kichik": 30.0}


def make_city(w=70, h=70, step=200.0, seed=1):
    """w x h chorraha. 0 va oxirgi qator hamda o'rta ustun — magistral,
    har 7-qator/ustun va daryo bo'yi — katta ko'cha, qolganlari — kichik
    (qatorma-qator navbatlashgan bir tomonlama). h//3 va h//3+1 qatorlar
    orasida daryo: faqat 3 ta ko'prik. Oxirida bitta "orol" tugun: undan chiqish bor,
    unga kirish yo'q."""
    rng = random.Random(seed)
    g = Graph()
    idx = {}
    for j in range(h):
        for i in range(w):
            idx[i, j] = g.add_node(i * step + rng.uniform(-40, 40), j * step + rng.uniform(-40, 40))

    river = h // 3
    bridges = {w // 6, w // 2, (5 * w) // 6}

    def kind_row(j):
        if j in (0, h - 1):
            return "magistral"
        if j in (river, river + 1):  # sohil bo'yi ko'chalari, ikki tomonlama
            return "katta"
        return "katta" if j % 7 == 0 else "kichik"

    def kind_col(i):
        if i == w // 2:
            return "magistral"
        return "katta" if i % 7 == 0 else "kichik"

    def link(a, b, kind, oneway_dir=None):
        kmh = SPEED[kind] * rng.uniform(0.85, 1.15)
        c = 1.0 + rng.uniform(0.0, 0.12)
        if oneway_dir in (None, +1):
            g.add_edge(a, b, kmh, kind, c)
        if oneway_dir in (None, -1):
            g.add_edge(b, a, kmh, kind, c)

    for j in range(h):
        k = kind_row(j)
        ow = None if k != "kichik" else (+1 if j % 2 else -1)
        for i in range(w - 1):
            link(idx[i, j], idx[i + 1, j], k, ow)
    for i in range(w):
        k = kind_col(i)
        ow = None if k != "kichik" else (+1 if i % 2 else -1)
        for j in range(h - 1):
            if j == river and i not in bridges:
                continue
            link(idx[i, j], idx[i, j + 1], k, ow)

    island = g.add_node(-500.0, -500.0)
    g.add_edge(island, idx[0, 0], 30.0, "kichik", 1.0)
    g.island = island
    g.idx = idx
    g.river_row = river
    return g


def make_observations(g, now, seed=2):
    """Jonli tezlik uchun kuzatuvlar: (edge_id, o'tish_soniya, haydovchi_id, vaqt).

    Qaytaradi: (obs, truth_kmh, cases) — cases — tekshiruv uchun maxsus qirralar.
    Haqiqiy tezlik tarixiydan farq qiladi (bugungi holat), kuzatuvlar shovqinli,
    ~15% i "to'xtab turgan" haydovchilar (10x sekin), ba'zilari eskirgan yoki
    imkonsiz (GPS sakrashi)."""
    rng = random.Random(seed)
    truth = [v * rng.uniform(0.55, 1.35) for v in g.kmh]
    obs = []
    next_driver = [1000]

    def driver():
        next_driver[0] += 1
        return next_driver[0]

    def add(e, kmh, d, ts):
        obs.append((e, g.length[e] / (kmh * KMH), d, ts))

    counts = [0, 0, 1, 2, 5, 15, 30]
    for e in range(g.m):
        n = rng.choice(counts)
        for _ in range(n):
            d = driver()
            for _ in range(rng.choice([1, 1, 2])):
                v = truth[e] * math.exp(rng.gauss(0, 0.10))
                if rng.random() < 0.15:
                    v *= 0.1  # to'xtab turgan / yo'lovchi kutgan
                add(e, v, d, now - rng.uniform(0, 590))
        if rng.random() < 0.3:  # eskirgan kuzatuvlar: kechagi tirbandlik
            add(e, truth[e] * 0.3, driver(), now - rng.uniform(700, 3000))

    cases = {}
    used = set(o[0] for o in obs)
    pool = [e for e in range(g.m) if e not in used]
    rng.shuffle(pool)

    # 1) bitta haydovchi, bitta kuzatuv — formula aniq tekshiriladi
    e = pool.pop()
    add(e, truth[e], driver(), now - 30)
    cases["single"] = (e, truth[e])
    # 2) faqat eskirgan kuzatuvlar
    e = pool.pop()
    for _ in range(6):
        add(e, truth[e] * 0.2, driver(), now - rng.uniform(900, 2000))
    cases["stale"] = (e, None)
    # 3) faqat imkonsiz tezliklar (GPS sakrashi)
    e = pool.pop()
    for _ in range(4):
        add(e, 250.0, driver(), now - 60)
    cases["impossible"] = (e, None)
    # 4) bitta haydovchi 10 marta sekin, 4 ta halol haydovchi
    e = pool.pop()
    spam = driver()
    for _ in range(10):
        add(e, truth[e] * 0.2, spam, now - rng.uniform(0, 500))
    for _ in range(4):
        add(e, truth[e], driver(), now - rng.uniform(0, 500))
    cases["spam"] = (e, truth[e])
    # 5) kelajakdagi (hali kelmagan) kuzatuv — ts > now, hisobga olinmaydi
    e = pool.pop()
    add(e, truth[e] * 0.25, driver(), now + 120)
    cases["future"] = (e, None)

    rng.shuffle(obs)
    return obs, truth, cases


ZONES = [f"z{i}" for i in range(10)]


def make_trips(n, seed=3):
    """Qoldiq modeli uchun safarlar: {"route_s", "actual_s", "hour", "zone"}.

    Haqiqiy vaqt = marshrut ETA x zona koeffitsienti x soat koeffitsienti x shovqin;
    ~3% safar — chiqib ketish (haydovchi uzoq kutgan, 2-4x uzun).
    "z_yangi" zonasi — yangi hudud: safarlar juda kam."""
    rng = random.Random(seed)
    zf = {z: 0.85 + 0.07 * i for i, z in enumerate(ZONES)}
    zf["z_yangi"] = 1.2

    def hf(h):
        if 7 <= h <= 9 or 17 <= h <= 19:
            return 1.3
        if h <= 5:
            return 0.85
        return 1.0

    trips = []
    for k in range(n):
        zone = "z_yangi" if k % 400 == 0 else rng.choice(ZONES)
        hour = rng.randrange(24)
        route = rng.uniform(180, 2400)
        actual = route * zf[zone] * hf(hour) * math.exp(rng.gauss(0, 0.12))
        if rng.random() < 0.03:
            actual *= rng.uniform(2, 4)
        trips.append({"route_s": route, "actual_s": actual, "hour": hour, "zone": zone})
    return trips
