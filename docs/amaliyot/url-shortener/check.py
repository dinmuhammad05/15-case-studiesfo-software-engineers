"""keys.py, bloom.py va cache.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Besh qism:
  1. Kalitlar: base62, Feistel aralashtirish (bijeksiya, teskarisi,
     ketma-ketlikni yashirish), blok bo'yicha ajratish.
  2. Bloom filtri: o'lcham formulasi, noto'g'ri manfiy yo'q, noto'g'ri
     ijobiy ulushi va'da qilinganiga yaqin.
  3. Kesh: birlik testlari, sodda model bilan solishtirish (fuzz), cache
     stampede (single-flight), stale-while-revalidate, skanerdan himoya.
  4. Tizim: bir daqiqalik trafik — Zipf bosishlar, viral havola, skaner,
     yangi havolalar va o'chirishlar birga.
  5. Tezlik.
"""
import math
import random
import sys
import time
import traceback

from model import ALPHABET, BASE, Counter, Store, Zipf, stable_hash  # noqa: F401

import bloom as bloom_mod
import cache as cache_mod
import keys as keys_mod

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))


def same(got, want):
    return (isinstance(got, tuple) and len(got) == 2 and got[0] == want[0]
            and isinstance(got[1], (int, float)) and abs(got[1] - want[1]) < 1e-9)


def attempt(fn, *a, **kw):
    try:
        return fn(*a, **kw), None
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


# ============================================================ sodda model
class NaiveCache:
    """Sekin, lekin aniq: ro'yxatlar va chiziqli qidiruv. cache.py dagi
    qoidalarning so'zma-so'z ifodasi."""

    def __init__(self, store, capacity, neg_capacity, ttl, neg_ttl, stale, db_latency):
        self.store, self.capacity, self.neg_capacity = store, capacity, neg_capacity
        self.ttl, self.neg_ttl, self.stale, self.lat = ttl, neg_ttl, stale, db_latency
        self.pos = []        # [kalit, url, fresh, stale], 0-indeks — eng eski
        self.neg = []        # [kalit, expires]
        self.fl = []         # [kalit, ready, value]

    def _find(self, lst, key):
        for i, e in enumerate(lst):
            if e[0] == key:
                return i
        return -1

    def _start(self, key, now):
        v = self.store.get(key)
        self.fl.append([key, now + self.lat, v])
        return now + self.lat, v

    def _settle(self, now):
        due = sorted((e for e in self.fl if e[1] <= now), key=lambda e: (e[1], e[0]))
        self.fl = [e for e in self.fl if e[1] > now]
        for key, ready, v in due:
            if v is not None:
                i = self._find(self.neg, key)
                if i >= 0:
                    self.neg.pop(i)
                i = self._find(self.pos, key)
                if i >= 0:
                    self.pos.pop(i)
                self.pos.append([key, v, ready + self.ttl, ready + self.ttl + self.stale])
                if len(self.pos) > self.capacity:
                    self.pos.pop(0)
            else:
                i = self._find(self.pos, key)
                if i >= 0:
                    self.pos.pop(i)
                i = self._find(self.neg, key)
                if i >= 0:
                    self.neg.pop(i)
                self.neg.append([key, ready + self.neg_ttl])
                if len(self.neg) > self.neg_capacity:
                    self.neg.pop(0)

    def get(self, key, now):
        self._settle(now)
        i = self._find(self.pos, key)
        if i >= 0:
            e = self.pos[i]
            if now < e[2]:
                self.pos.append(self.pos.pop(i))
                return e[1], 0.0
            if now < e[3]:
                self.pos.append(self.pos.pop(i))
                if self._find(self.fl, key) < 0:
                    self._start(key, now)
                return e[1], 0.0
            self.pos.pop(i)
        i = self._find(self.neg, key)
        if i >= 0:
            if now < self.neg[i][1]:
                return None, 0.0
            self.neg.pop(i)
        i = self._find(self.fl, key)
        if i >= 0:
            return self.fl[i][2], self.fl[i][1] - now
        r, v = self._start(key, now)
        return v, r - now

    def invalidate(self, key):
        for lst in (self.pos, self.neg, self.fl):
            i = self._find(lst, key)
            if i >= 0:
                lst.pop(i)


# ============================================================ 1. kalitlar
def part_keys():
    print("1. Kalitlar")
    enc, dec = keys_mod.encode, keys_mod.decode
    errs = []
    cases = [(0, 0, "0"), (61, 0, "Z"), (62, 0, "10"), (3843, 0, "ZZ"), (5, 7, "0000005"),
             (BASE ** 7 - 1, 7, "ZZZZZZZ"), (125, 3, "021")]
    for n, w, want in cases:
        got, e = attempt(enc, n, w)
        if got != want:
            errs.append(f"encode({n}, {w}) = {got!r}, kutilgan {want!r}" + (f" ({e})" if e else ""))
    rng = random.Random(1)
    for _ in range(3000):
        n = rng.randrange(BASE ** rng.randint(1, 12))
        s, e = attempt(enc, n)
        back, e2 = attempt(dec, s) if s is not None else (None, e)
        if back != n:
            errs.append(f"decode(encode({n})) = {back}" + (f" ({e2})" if e2 else ""))
            break
    if dec("00012") != dec("12"):
        errs.append("decode boshidagi nollarni e'tiborsiz qoldirishi kerak")
    for bad in ["", "ab-c", "a b", "ё"]:
        _, e = attempt(dec, bad)
        if e is None or not e.startswith("ValueError"):
            errs.append(f"decode({bad!r}) ValueError berishi kerak")
    _, e = attempt(enc, -1)
    if e is None or not e.startswith("ValueError"):
        errs.append("encode(-1) ValueError berishi kerak")
    check("base62: encode/decode, kenglik, xatolar", not errs, "; ".join(errs[:3]))

    errs = []
    for domain in (1000, 3844, 10007):
        f = keys_mod.Feistel(domain, secret=7)
        out = [f.permute(x) for x in range(domain)]
        if sorted(out) != list(range(domain)):
            bad = sum(1 for y in out if not 0 <= y < domain)
            errs.append(f"domen {domain}: bijeksiya emas ({len(set(out))} xil qiymat, {bad} tasi diapazondan tashqarida)")
            continue
        if any(f.invert(y) != x for x, y in enumerate(out)):
            errs.append(f"domen {domain}: invert(permute(x)) != x")
        fixed = sum(1 for x, y in enumerate(out) if x == y)
        if fixed > domain // 50:
            errs.append(f"domen {domain}: {fixed} ta son joyida qoldi — aralashmayapti")
    check("Feistel: kichik domenlarda to'liq bijeksiya va teskarisi", not errs, "; ".join(errs[:2]))

    errs = []
    D = BASE ** 7
    f1, f2, f1b = keys_mod.Feistel(D, 2024), keys_mod.Feistel(D, 2025), keys_mod.Feistel(D, 2024)
    xs = [rng.randrange(D) for _ in range(3000)]
    for x in xs:
        y = f1.permute(x)
        if not 0 <= y < D:
            errs.append(f"permute({x}) = {y} diapazondan tashqarida")
            break
        if f1.invert(y) != x:
            errs.append(f"invert(permute({x})) != {x}")
            break
        if f1b.permute(x) != y:
            errs.append("bir xil sir — bir xil natija bo'lishi kerak")
            break
    same = sum(1 for x in xs[:1000] if f1.permute(x) == f2.permute(x))
    if same > 5:
        errs.append(f"boshqa sir bilan {same}/1000 natija bir xil — sir ishlatilmayapti")
    ys = [f1.permute(x) for x in range(20000)]
    close = sum(1 for a, b in zip(ys, ys[1:]) if abs(a - b) < D // 1000)
    if close > 200:
        errs.append(f"ketma-ket sonlarning {close}/19999 tasi yaqin natija berdi — ketma-ketlik ko'rinib qoladi")
    if len(set(ys)) != len(ys):
        errs.append("62^7 domenida takror natija")
    check("Feistel: 62^7 domeni — diapazon, teskarisi, sir, ketma-ketlikni yashirish", not errs, "; ".join(errs[:2]))

    errs = []
    counter = Counter()
    fe = keys_mod.Feistel(D, 99)
    allocs = [keys_mod.KeyAllocator(counter, fe, block=1000, width=7) for _ in range(3)]
    seen, per = set(), [0, 0, 0]
    for i in range(25000):
        j = rng.choice([0, 0, 1, 2])
        k = allocs[j].next_key()
        per[j] += 1
        if len(k) != 7 or any(ch not in ALPHABET for ch in k):
            errs.append(f"kalit {k!r}: 7 ta base62 belgi bo'lishi kerak")
            break
        if k in seen:
            errs.append(f"takror kalit {k!r} ({i}-chi)")
            break
        seen.add(k)
    want_calls = sum(math.ceil(p / 1000) for p in per)
    if not errs and counter.calls != want_calls:
        errs.append(f"markazga {counter.calls} marta murojaat, kutilgan {want_calls} (blok bo'yicha)")
    nums = [keys_mod.decode(k) for k in list(seen)[:2000]] if not errs else []
    if nums and max(nums) < D // 100:
        errs.append("kalitlar maydonning boshida to'planib qoldi — aralashtirilmagan")
    check("KeyAllocator: 3 server, 25 000 kalit — takrorsiz, blok bo'yicha", not errs, "; ".join(errs[:2]))

    errs = []
    counter = Counter()
    a = keys_mod.KeyAllocator(counter, fe, block=500, width=7)
    got = [a.next_key() for _ in range(700)]
    a = keys_mod.KeyAllocator(counter, fe, block=500, width=7)       # qayta ishga tushdi
    got += [a.next_key() for _ in range(700)]
    if len(set(got)) != len(got):
        errs.append("qayta ishga tushgandan keyin takror kalit")
    if counter.calls != 4:
        errs.append(f"markazga {counter.calls} murojaat, kutilgan 4")
    if counter.value != 2000:
        errs.append(f"hisoblagich {counter.value}, kutilgan 2000 (ishlatilmagan 300 ta kalit yo'qoladi — bu normal)")
    check("Qayta ishga tushish: ishlatilmagan blok yo'qoladi, takror yo'q", not errs, "; ".join(errs))


# ============================================================ 2. Bloom
def part_bloom():
    print("2. Bloom filtri")
    errs = []
    for n, p, m, k in [(1_000_000, 0.01, 9585059, 7), (6_000, 0.1, 28756, 3), (100, 0.001, 1438, 10)]:
        b = bloom_mod.Bloom(n, p)
        if (b.m, b.k) != (m, k):
            errs.append(f"Bloom({n}, {p}): m={b.m}, k={b.k}; kutilgan m={m}, k={k}")
    check("o'lcham: m = ceil(-n ln p / ln²2), k = round(m/n · ln2)", not errs, "; ".join(errs[:2]))

    b = bloom_mod.Bloom(40_000, 0.01)
    members = [f"k{i}" for i in range(40_000)]
    for x in members:
        b.add(x)
    fn = sum(1 for x in members if x not in b)
    check("noto'g'ri manfiy yo'q: qo'shilgan 40 000 kalitning hammasi topiladi", fn == 0, f"{fn} ta topilmadi")

    errs = []
    for p in (0.01, 0.05):
        b = bloom_mod.Bloom(40_000, p)
        for x in members:
            b.add(x)
        fp = sum(1 for i in range(100_000) if f"q{i}" in b) / 100_000
        if not 0.6 * p <= fp <= 1.4 * p:
            errs.append(f"p={p}: haqiqiy ulush {fp:.4f}")
        else:
            print(f"      p={p}: haqiqiy noto'g'ri ijobiy ulush {fp:.4f}")
    check("noto'g'ri ijobiy ulush va'da qilingan p ga yaqin (0.6p..1.4p)", not errs, "; ".join(errs))


# ============================================================ 3. kesh
def mk(store, **kw):
    cfg = dict(capacity=100, neg_capacity=50, ttl=10.0, neg_ttl=2.0, stale=0.0, db_latency=0.005)
    cfg.update(kw)
    return cache_mod.LinkCache(store, **cfg)


def part_cache():
    print("3. Kesh")
    errs = []
    st = Store()
    st.put("abc", "https://a.uz")
    c = mk(st)
    r1 = c.get("abc", 0.0)
    r2 = c.get("abc", 0.002)
    r3 = c.get("abc", 0.006)
    if not same(r1, ("https://a.uz", 0.005)):
        errs.append(f"birinchi so'rov {r1}, kutilgan ('https://a.uz', 0.005)")
    if not same(r2, ("https://a.uz", 0.003)):
        errs.append(f"yuklanish paytidagi so'rov {r2}: shu yuklanishni kutishi kerak (0.003 s)")
    if not same(r3, ("https://a.uz", 0.0)):
        errs.append(f"yuklangandan keyin {r3}, kutilgan keshdan (0.0)")
    if st.reads != 1:
        errs.append(f"bazaga {st.reads} o'qish, kutilgan 1")
    c.get("abc", 10.004)
    if st.reads != 1:
        errs.append("TTL tugashidan oldin bazaga borildi")
    c.get("abc", 10.006)
    if st.reads != 2:
        errs.append("TTL tugagandan keyin bazadan qayta o'qilmadi")
    if not same(c.get("yoq", 20.0), (None, 0.005)) or not same(c.get("yoq", 20.01), (None, 0.0)):
        errs.append("yo'q kalit: birinchi marta bazaga, keyin salbiy keshdan")
    st.put("yoq", "https://b.uz")
    if c.get("yoq", 21.0)[0] is not None:
        errs.append("salbiy yozuv neg_ttl ichida amal qilishi kerak")
    if not same(c.get("yoq", 22.1), ("https://b.uz", 0.005)):
        errs.append("neg_ttl tugagach yangi havola ko'rinishi kerak")
    c.get("abc", 30.0)
    st.delete("abc")
    c.invalidate("abc")
    if not same(c.get("abc", 30.01), (None, 0.005)):
        errs.append("invalidate dan keyin o'chirilgan havola qaytdi")
    check("birlik: kutish, TTL, salbiy kesh, invalidate", not errs, "; ".join(errs[:3]))

    # fuzz
    errs = []
    for seed in range(60):
        rng = random.Random(seed)
        cfg = dict(capacity=rng.randint(1, 6), neg_capacity=rng.randint(1, 4),
                   ttl=rng.choice([0.5, 1.0, 3.0]), neg_ttl=rng.choice([0.2, 1.0]),
                   stale=rng.choice([0.0, 0.0, 1.0, 5.0]), db_latency=rng.choice([0.05, 0.2, 0.5]))
        sa, sb = Store(), Store()
        a, b = cache_mod.LinkCache(sa, **cfg), NaiveCache(sb, **cfg)
        keys = [f"k{i}" for i in range(rng.randint(3, 15))]
        for k in keys:
            if rng.random() < 0.6:
                sa.put(k, "u" + k)
                sb.put(k, "u" + k)
        now = 0.0
        for step in range(400):
            now += rng.choice([0.0, 0.0, 0.01, 0.05, 0.1, 0.3, 1.0])
            k = rng.choice(keys)
            if rng.random() < 0.08:
                if k in sa.data:
                    sa.delete(k)
                    sb.delete(k)
                else:
                    v = f"u{k}{step}"
                    sa.put(k, v)
                    sb.put(k, v)
                if rng.random() < 0.7:
                    a.invalidate(k)
                    b.invalidate(k)
                continue
            got, e = attempt(a.get, k, now)
            want = b.get(k, now)
            if e or not same(got, want) or sa.reads != sb.reads:
                errs.append(f"seed {seed}, qadam {step}, t={now:.2f}, get({k}): {e or got}, "
                            f"kutilgan {want}; bazaga o'qish {sa.reads} vs {sb.reads}")
                break
        if errs:
            break
    check("fuzz: 60 ta tasodifiy ketma-ketlik — sodda model bilan aynan bir xil", not errs, errs[0] if errs else "")

    # stampede
    st = Store()
    st.put("hot", "https://viral.uz")
    c = mk(st, ttl=1.0, stale=0.0, db_latency=0.02)
    t, waits = 0.0, []
    while t < 5.0:
        waits.append(c.get("hot", t)[1])
        t += 0.0002                                  # 5000 so'rov/s
    n_req = len(waits)
    check(f"cache stampede: bitta kalit, 5000 so'rov/s, TTL 1 s, 5 s — bazaga {st.reads} o'qish (≤ 6)",
          st.reads <= 6, f"{n_req} so'rovdan {st.reads} tasi bazaga ketdi — single-flight yo'q")

    st = Store()
    st.put("hot", "https://viral.uz")
    c = mk(st, ttl=1.0, stale=30.0, db_latency=0.02)
    t, waits = 0.0, []
    while t < 5.0:
        waits.append(c.get("hot", t)[1])
        t += 0.0002
    late = sum(1 for w in waits[200:] if w > 0)
    check(f"stale-while-revalidate: birinchi yuklanishdan keyin hech kim kutmaydi ({late} kutdi), "
          f"bazaga {st.reads} o'qish", late == 0 and 3 <= st.reads <= 6,
          f"{late} so'rov kutdi, {st.reads} o'qish (fonda TTL har tugaganda bittadan bo'lishi kerak)")

    # skaner
    st = Store()
    hot = [f"h{i}" for i in range(200)]
    for k in hot:
        st.put(k, "u" + k)
    c = mk(st, capacity=200, neg_capacity=100, ttl=1000.0, neg_ttl=60.0, db_latency=0.001)
    t = 0.0
    for k in hot:
        c.get(k, t)
        t += 0.01
    rng = random.Random(5)
    t += 1.0
    before = st.reads
    hot_db = 0
    for i in range(20000):
        t += 0.0005
        if i % 4 == 0:
            r0 = st.reads
            c.get(rng.choice(hot), t)
            hot_db += st.reads - r0
        else:
            c.get(f"scan{i}", t)
    check(f"skaner: 15 000 yo'q kalit issiq havolalarni siqib chiqarmaydi (issiqlar bazaga {hot_db} marta)",
          hot_db == 0, f"issiq havolalar uchun bazaga {hot_db} o'qish — salbiy yozuvlar alohida bo'lishi kerak"
          f" (jami {st.reads - before})")


# ============================================================ 4. tizim
def part_system():
    print("4. Tizim: bir daqiqalik trafik")
    rng = random.Random(11)
    D = BASE ** 7
    counter = Counter()
    fe = keys_mod.Feistel(D, 31337)
    servers = [keys_mod.KeyAllocator(counter, fe, block=1000) for _ in range(4)]
    st = Store()
    links = []
    for i in range(60_000):
        k = servers[i % 4].next_key()
        st.put(k, f"https://site{i}.uz/sahifa")
        links.append(k)
    bl = bloom_mod.Bloom(100_000, 0.01)
    for k in links:
        bl.add(k)
    c = cache_mod.LinkCache(st, capacity=6000, neg_capacity=2000, ttl=300.0, neg_ttl=2.0,
                            stale=600.0, db_latency=0.005)
    z = Zipf(len(links), 1.1, seed=3)
    created, deleted = [], set()
    n = reads = wrong = scan = scan_db = 0
    waits = []
    t, dt = 0.0, 1 / 4000
    steps = 0
    t0 = time.time()
    while t < 60.0:
        t += dt
        warm = t >= 30.0                                # birinchi 30 s — kesh isinadi, hisobga olinmaydi
        u = rng.random()
        if u < 0.15:                                    # skaner
            key = keys_mod.encode(rng.randrange(D), 7)
        elif u < 0.17:                                  # yangi havolalar: yaratildi va darhol bosildi
            if not created or rng.random() < 0.1:
                k = servers[rng.randrange(4)].next_key()
                st.put(k, f"https://yangi{len(created)}.uz")
                bl.add(k)
                created.append(k)
            key = created[-1 - rng.randrange(min(len(created), 20))]
        elif 40 <= t < 50 and u < 0.40:                 # viral havola
            key = links[777]
        else:
            key = links[z.sample()]
        if t >= 45 and not deleted:                     # 200 ta eng mashhur havola o'chiriladi
            for k in links[:200]:
                st.delete(k)
                c.invalidate(k)
                deleted.add(k)
        truth = st.data.get(key)
        r0 = st.reads
        if key not in bl:
            got, w = None, 0.0
        else:
            got, w = c.get(key, t)
        if got != truth:
            wrong += 1
        if warm:
            n += 1
            reads += st.reads - r0
            waits.append(w)
            if u < 0.15:
                scan += 1
                scan_db += st.reads - r0
        steps += 1
        if steps % 2000 == 0 and time.time() - t0 > 30:
            break
    elapsed = time.time() - t0
    waits.sort()
    waits = waits or [0.0]
    p50, p99 = waits[len(waits) // 2], waits[int(len(waits) * 0.99)]
    print(f"      issiq 30 s: {n} so'rov ({n / 30:.0f}/s), bazaga {reads} ({reads / 30:.0f}/s, {reads / max(n, 1):.1%}), "
          f"kutish p50={p50 * 1000:.1f} ms p99={p99 * 1000:.1f} ms; skanerdan bazaga {scan_db}/{scan}; {elapsed:.1f} s")
    check("to'g'rilik: 240 000 javobning hammasi bazadagi haqiqatga teng (o'chirish va yaratishdan keyin ham)",
          wrong == 0 and t >= 60.0, f"{wrong} ta noto'g'ri javob" if wrong else "vaqt tugadi")
    check(f"bazaga yuk (issiq holatda): so'rovlarning ≤ 16% i ({reads / max(n, 1):.1%})", n and reads / n <= 0.16,
          "kesh yoki Bloom filtri yaxshi ishlamayapti")
    check(f"skaner bazaga deyarli yetmaydi: {scan_db}/{scan} (≤ 1.5%)", scan and scan_db <= 0.015 * scan,
          "Bloom filtri yo'q kalitlarni yetarlicha to'xtatmayapti")


# ============================================================ 5. tezlik
def part_speed():
    print("5. Tezlik")
    t0 = time.time()
    fe = keys_mod.Feistel(BASE ** 7, 1)
    a = keys_mod.KeyAllocator(Counter(), fe, block=10_000)
    for _ in range(50_000):
        a.next_key()
    t1 = time.time()
    st = Store()
    for i in range(50_000):
        st.put(f"k{i}", f"u{i}")
    c = cache_mod.LinkCache(st, capacity=20_000, neg_capacity=5_000, ttl=3.0, neg_ttl=1.0,
                            stale=10.0, db_latency=0.005)
    z = Zipf(60_000, 1.0, seed=9)
    ks = [f"k{z.sample()}" for _ in range(300_000)]
    t2 = time.time()
    t = 0.0
    for i, k in enumerate(ks):
        t += 0.0001
        c.get(k, t)
        if i % 1000 == 0 and time.time() - t2 > 6:
            break
    t3 = time.time()
    check(f"50 000 kalit ({t1 - t0:.2f} s) va 300 000 kesh so'rovi ({t3 - t2:.2f} s) — jami 4 soniyadan tez",
          i == len(ks) - 1 and (t1 - t0) + (t3 - t2) < 4.0, f"{i + 1} so'rovdan keyin to'xtatildi")


def run(part):
    try:
        part()
        return True
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
        results.append(False)
        return False
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        print("\n  Xato (istisno):\n    " + "\n    ".join(tb[-3:]))
        results.append(False)
        return False


def main():
    t0 = time.time()
    ok1 = run(part_keys)
    ok2 = run(part_bloom)
    ok3 = run(part_cache)
    if ok1 and ok2 and ok3 and all(results):
        run(part_system)
        run(part_speed)
    else:
        print("4-5. O'tkazib yuborildi: avval 1-3 qismlar to'liq o'tsin")
        results.append(False)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
