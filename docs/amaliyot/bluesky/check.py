"""repo.py va appview.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

To'rt qism:
  1. Repo (MST): tuzilma qoidalari, determinizm, aniq javob, inklyuziya va
     yo'qlik isbotlari (soxtalari rad etiladi), diff — to'g'ri va tejamkor.
  2. AppView: birlik testlari — like va follow hisoblari, tahrir va
     o'chirish, imzo, takrorlar, bo'shliq va resinxronizatsiya, hisob
     holati, kalit almashtirish, tasma (timeline).
  3. Xaos: "yomon" relay va tarmoq bilan 25 ta stsenariy — yakuniy indeks
     PDS'lardagi haqiqiy repolar bilan aynan bir xil.
  4. Tezlik: 500 ta muallifli "Following" tasmasi.
"""
import random
import sys
import time

from model import (EMPTY_ROOT, FOLLOW, LIKE, POST, Account, Commit, Identity, Node,
                   RepoSnapshot, at_uri, commit_bytes, key_level, keypair, sha, sign,
                   tree_hash)
from sim import Sim

import appview as app_mod
import repo as repo_mod

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


# ============================================================ 1. MST
def items_of(n, seed=0, prefix=POST):
    rng = random.Random(seed)
    keys = set()
    while len(keys) < n:
        keys.add(f"{prefix}/{rng.getrandbits(40):010x}")
    return {k: sha(k + "#v") for k in keys}


def walk(node, out):
    """In-order kalitlar va qiymatlar; har tugunda tuzilma qoidalarini tekshiradi."""
    if node is None:
        return None
    lv = {key_level(e.key) for e in node.entries}
    if len(lv) > 1:
        raise AssertionError("bitta tugunda turli darajadagi kalitlar")
    level = lv.pop() if lv else None
    for child in [node.left] + [e.right for e in node.entries]:
        if child is not None:
            if not child.entries:
                raise AssertionError("bo'sh ichki tugun")
            cl = key_level(child.entries[0].key)
            if level is not None and cl >= level:
                raise AssertionError("bola tugun darajasi ota tugundan past emas")
    walk(node.left, out)
    for e in node.entries:
        out.append((e.key, e.value))
        walk(e.right, out)
    return level


def depth(node):
    if node is None:
        return 0
    return 1 + max([depth(node.left)] + [depth(e.right) for e in node.entries])


KNOWN_200 = "7144e539768f61886c88b5d3e1deb657a4dee3207fea70b09e1ca11940d7d4e0"


def part_mst():
    print("1. Repo: Merkle Search Tree")
    t, err = attempt(repo_mod.build_tree, {})
    unit("bo'sh repo — bitta bo'sh tugun, xeshi EMPTY_ROOT", err is None and tree_hash(t) == EMPTY_ROOT,
         err or f"{tree_hash(t) if t else None}")

    bad = None
    for seed in range(20):
        items = items_of(random.Random(seed).randint(1, 600), seed)
        root, err = attempt(repo_mod.build_tree, items)
        if err:
            bad = err
            break
        out = []
        try:
            walk(root, out)
        except AssertionError as e:
            bad = f"seed={seed}: {e}"
            break
        if out != sorted(items.items()):
            bad = f"seed={seed}: daraxtdagi kalitlar/qiymatlar to'plam bilan mos emas"
            break
    unit("tuzilma: kalitlar tartibda, tugun ichida bir xil daraja, bolalar pastroq darajada, "
         "bo'sh ichki tugun yo'q", bad is None, bad or "")

    items = items_of(200, 7)
    keys = list(items)
    h1 = tree_hash(repo_mod.build_tree(items))
    random.Random(1).shuffle(keys)
    h2 = tree_hash(repo_mod.build_tree({k: items[k] for k in keys}))
    unit("determinizm: kiritish tartibi ahamiyatsiz; aniq javob (200 kalit) mos", h1 == h2 and h1 == KNOWN_200,
         f"{h1[:16]}... / {h2[:16]}... kerak {KNOWN_200[:16]}...")

    ch = dict(items)
    k0 = sorted(items)[100]
    ch[k0] = sha("boshqa")
    unit("bitta qiymat o'zgarsa — ildiz xeshi o'zgaradi; qaytarilsa — avvalgisi",
         tree_hash(repo_mod.build_tree(ch)) != h1 and tree_hash(repo_mod.build_tree(dict(items))) == h1)

    items = items_of(400, 11)
    root = repo_mod.build_tree(items)
    rh = tree_hash(root)
    ok, worst, err = True, 0, ""
    for k, v in items.items():
        pr, err = attempt(repo_mod.prove, root, k)
        if err or not repo_mod.verify_proof(rh, k, v, pr):
            ok = False
            err = err or f"{k} isboti o'tmadi"
            break
        worst = max(worst, len(pr))
    rng = random.Random(3)
    for _ in range(60):
        k = f"{POST}/{rng.getrandbits(40):010x}x"
        if not repo_mod.verify_proof(rh, k, None, repo_mod.prove(root, k)):
            ok, err = False, f"yo'qlik isboti o'tmadi: {k}"
            break
    unit(f"isbotlar: 400 ta kalitning har biri va 60 ta yo'q kalit tasdiqlanadi; isbot uzunligi "
         f"<= daraxt chuqurligi ({worst} <= {depth(root)})", ok and worst <= depth(root), err)

    k = sorted(items)[123]
    v = items[k]
    pr = repo_mod.prove(root, k)
    forged = list(pr)
    forged[-1] = forged[-1].replace(v.encode(), sha("soxta").encode())
    k_abs = f"{POST}/zzzz"
    pr_abs = repo_mod.prove(root, k_abs)
    other = sorted(items)[5]
    cases = {
        "noto'g'ri qiymat": repo_mod.verify_proof(rh, k, sha("soxta"), pr),
        "noto'g'ri ildiz": repo_mod.verify_proof(sha("x"), k, v, pr),
        "o'zgartirilgan tugun": repo_mod.verify_proof(rh, k, sha("soxta"), forged),
        "kesilgan isbot": len(pr) > 1 and repo_mod.verify_proof(rh, k, v, pr[:-1]),
        "ortiqcha tugun": repo_mod.verify_proof(rh, k, v, pr + [pr[-1]]),
        "bor kalitni 'yo'q' deyish": repo_mod.verify_proof(rh, k, None, pr),
        "yo'q kalitga qiymat": repo_mod.verify_proof(rh, k_abs, v, pr_abs),
        "boshqa kalitning isboti": repo_mod.prove(root, other) != pr
        and repo_mod.verify_proof(rh, other, items[other], pr),
    }
    passed = [n for n, r in cases.items() if r]
    unit("soxta isbotlar rad etiladi (8 holat)", not passed, f"o'tib ketdi: {passed}")

    bad = None
    for seed in range(60):
        rng = random.Random(100 + seed)
        a = items_of(rng.randint(0, 300), seed)
        b = dict(a)
        for kk in rng.sample(sorted(a), min(len(a), rng.randint(0, 20))):
            if rng.random() < 0.5:
                del b[kk]
            else:
                b[kk] = sha(kk + "new")
        b.update(items_of(rng.randint(0, 20), 9000 + seed, LIKE))
        want = {kk: (a.get(kk), b.get(kk)) for kk in set(a) | set(b) if a.get(kk) != b.get(kk)}
        got, err = attempt(repo_mod.diff, repo_mod.build_tree(a), repo_mod.build_tree(b))
        if err or got[0] != want:
            bad = err or f"seed={seed}: {len(want)} ta o'zgarish kerak, olindi {len(got[0])}"
            break
    unit("diff: 60 ta tasodifiy juftlikda qo'shilgan, o'zgargan va o'chirilgan kalitlar aniq", bad is None, bad or "")

    big = items_of(3000, 21)
    t1 = repo_mod.build_tree(big)
    b2 = dict(big)
    kk = sorted(big)[1500]
    b2[kk] = sha("yangi")
    ch1, v1 = repo_mod.diff(t1, repo_mod.build_tree(b2))
    ch0, v0 = repo_mod.diff(t1, repo_mod.build_tree(dict(big)))
    chall, _ = repo_mod.diff(Node(), t1)
    unit(f"diff tejamkor: 3 000 kalitda bitta o'zgarish — {v1} tugun ochildi (<= 60); bir xil daraxtlar — "
         f"{v0} (0); bo'sh va to'liq — 3 000 o'zgarish",
         ch1 == {kk: (big[kk], b2[kk])} and v1 <= 60 and v0 == 0 and ch0 == {} and len(chall) == 3000,
         f"o'zgarishlar={len(ch1)}, ochildi={v1}, bir xil={v0}, to'liq={len(chall)}")


# ============================================================ 2. AppView
class Net:
    """Birlik testlari uchun kichik PDS va relay."""

    def __init__(self):
        self.users = {}
        self.seq = 0
        self.asked = []
        self.app = app_mod.AppView(self.resolve, self.asked.append)

    def add(self, did):
        sk, pk = keypair(did + "#0")
        self.users[did] = {"sk": sk, "pk": pk, "rev": 0, "records": {}, "n": 0}

    def resolve(self, did):
        return self.users[did]["pk"]

    def mk(self, did, ops, key=None, bump=True):
        u = self.users[did]
        prev = u["rev"] or None
        rev = u["rev"] + 1
        for action, path, rec in ops:
            if action == "delete":
                u["records"].pop(path, None)
            else:
                u["records"][path] = rec
        if bump:
            u["rev"] = rev
        ops = tuple(ops)
        self.seq += 1
        return Commit(self.seq, did, rev, prev, ops, sign(key or u["sk"], commit_bytes(did, rev, prev, ops)))

    def send(self, did, ops, **kw):
        ev = self.mk(did, ops, **kw)
        self.app.on_event(ev)
        return ev

    def path(self, did, coll):
        self.users[did]["n"] += 1
        return f"{coll}/{self.users[did]['n']:04d}"

    def snap(self, did):
        u = self.users[did]
        return RepoSnapshot(did, u["rev"], dict(u["records"]))


def part_app_units():
    print("2. AppView: birlik testlari")
    n = Net()
    for d in ("did:a", "did:b", "did:c"):
        n.add(d)
    pa = n.path("did:a", POST)
    n.send("did:a", [("create", pa, {"text": "salom", "createdAt": 10})])
    p_uri = at_uri("did:a", pa)
    lb1, lb2, lc = n.path("did:b", LIKE), n.path("did:b", LIKE), n.path("did:c", LIKE)
    n.send("did:b", [("create", lb1, {"subject": p_uri}), ("create", lb2, {"subject": p_uri})])
    n.send("did:c", [("create", lc, {"subject": p_uri})])
    c1 = n.app.like_count(p_uri)
    n.send("did:b", [("delete", lb1, None)])
    c2 = n.app.like_count(p_uri)
    n.send("did:b", [("delete", lb2, None)])
    c3 = n.app.like_count(p_uri)
    unit("like: har kishi bir marta sanaladi; o'chirishda yozuv eslab qolinadi (delete da qiymat yo'q)",
         (c1, c2, c3) == (2, 2, 1), f"olindi {(c1, c2, c3)}, kerak (2, 2, 1)")

    fa1, fa2, fc = n.path("did:a", FOLLOW), n.path("did:a", FOLLOW), n.path("did:c", FOLLOW)
    n.send("did:a", [("create", fa1, {"subject": "did:b"}), ("create", fa2, {"subject": "did:b"})])
    n.send("did:c", [("create", fc, {"subject": "did:b"})])
    pb1, pb2, pb3 = n.path("did:b", POST), n.path("did:b", POST), n.path("did:b", POST)
    n.send("did:b", [("create", pb1, {"text": "1", "createdAt": 5}), ("create", pb2, {"text": "2", "createdAt": 20}),
                     ("create", pb3, {"text": "3", "createdAt": 20})])
    tl1 = n.app.timeline("did:a", 10)
    want1 = [at_uri("did:b", pb3), at_uri("did:b", pb2), p_uri, at_uri("did:b", pb1)]
    n.send("did:b", [("update", pb2, {"text": "2 (tahrir)", "createdAt": 20}), ("delete", pb1, None)])
    tl2 = n.app.timeline("did:a", 2)
    n.send("did:a", [("delete", fa1, None)])
    f1 = n.app.follower_count("did:b")
    tl3 = n.app.timeline("did:a", 10)
    unit("follow va tasma: bir xil follow ikki marta — bir obunachi; tasma eng yangisidan, teng vaqtda — uri "
         "bo'yicha; tahrir takror qilmaydi, o'chirilgan post yo'qoladi; limit ishlaydi",
         tl1 == want1 and tl2 == want1[:2] and f1 == 2 and tl3 == [want1[0], want1[1], p_uri],
         f"tl1={tl1}\n      tl2={tl2}, followers={f1}, tl3={tl3}")

    before = (n.app.like_count(p_uri), n.app.timeline("did:c", 10))
    fake_sk, _ = keypair("hujumchi")
    lx = n.path("did:c", LIKE)
    ev = n.mk("did:c", [("create", lx, {"subject": p_uri})], key=fake_sk, bump=False)
    n.users["did:c"]["records"].pop(lx)
    n.app.on_event(ev)
    after = (n.app.like_count(p_uri), n.app.timeline("did:c", 10))
    unit("soxta imzo: commit tashlanadi, holat o'zgarmaydi, resinxronizatsiya so'ralmaydi",
         before == after and not n.asked, f"oldin {before}, keyin {after}, so'rovlar {n.asked}")

    lc2 = n.path("did:c", LIKE)
    ev = n.mk("did:c", [("create", lc2, {"subject": at_uri("did:b", pb2)})])
    n.app.on_event(ev)
    n.app.on_event(ev)
    replay = Commit(n.seq + 1, ev.did, ev.rev, ev.prev, ev.ops, ev.sig)
    n.seq += 1
    n.app.on_event(replay)
    unit("takrorlar: bir xil hodisa ikki marta, eski commit yangi seq bilan — bir marta qo'llanadi, "
         "resinxronizatsiyasiz", n.app.like_count(at_uri("did:b", pb2)) == 1 and not n.asked,
         f"like={n.app.like_count(at_uri('did:b', pb2))}, so'rovlar={n.asked}")

    l1 = n.path("did:c", LIKE)
    e1 = n.mk("did:c", [("create", l1, {"subject": at_uri("did:b", pb3)})])          # yo'qoladi
    l2 = n.path("did:c", LIKE)
    e2 = n.mk("did:c", [("create", l2, {"subject": at_uri("did:b", pb3)})])
    n.app.on_event(e2)
    asked1 = list(n.asked)
    snap_mid = RepoSnapshot("did:c", e1.rev, {k: v for k, v in n.users["did:c"]["records"].items() if k != l2})
    l3 = n.path("did:c", LIKE)
    e3 = n.mk("did:c", [("delete", lc, None), ("create", l3, {"subject": at_uri("did:b", pb2)})])
    n.app.on_event(e3)
    n.seq += 1
    n.app.on_event(Commit(n.seq, e1.did, e1.rev, e1.prev, e1.ops, e1.sig))   # e1 kechikib keldi (eski)
    mid_like = n.app.like_count(p_uri)
    n.app.on_resync(snap_mid)
    unit("bo'shliq: resinxronizatsiya bir marta so'raladi; kutishda kelganlar buferda; suratdan keyin "
         "eskilari tashlanadi, yangilari qo'llanadi",
         asked1 == ["did:c"] and n.asked == ["did:c"] and mid_like == 1 and n.app.like_count(p_uri) == 0
         and n.app.like_count(at_uri("did:b", pb3)) == 1 and n.app.like_count(at_uri("did:b", pb2)) == 1,
         f"so'rovlar={n.asked}, oraliqda like={mid_like}, keyin {n.app.like_count(p_uri)}, "
         f"pb3={n.app.like_count(at_uri('did:b', pb3))}, pb2={n.app.like_count(at_uri('did:b', pb2))}")

    fb = n.path("did:b", FOLLOW)
    n.send("did:b", [("create", fb, {"subject": "did:a"})])
    seen = p_uri in n.app.timeline("did:b", 10)
    n.seq += 1
    deact = Account(n.seq, "did:a", False)
    n.app.on_event(deact)
    off = (n.app.follower_count("did:b"), n.app.timeline("did:a", 5), p_uri in n.app.timeline("did:b", 10),
           n.app.follower_count("did:a"))
    n.seq += 1
    n.app.on_event(Account(n.seq, "did:a", True))
    n.app.on_event(deact)      # eski hodisa qayta keldi — e'tiborsiz
    on = (n.app.follower_count("did:b"), p_uri in n.app.timeline("did:b", 10), n.app.follower_count("did:a"))
    unit("hisob o'chirilsa — uning follow'lari sanalmaydi, postlari tasmalarda yo'q; qaytarilsa — hammasi joyida; "
         "eski hisob hodisasi qayta kelsa — e'tiborsiz",
         seen and off == (1, [], False, 1) and on == (2, True, 1) and n.app.timeline("did:a", 1) != [],
         f"oldin={seen}, o'chiq: {off}, yoqiq: {on}")

    u = n.users["did:b"]
    old_sk = u["sk"]
    u["sk"], u["pk"] = keypair("did:b#1")
    n.seq += 1
    n.app.on_event(Identity(n.seq, "did:b"))
    pb4 = n.path("did:b", POST)
    n.send("did:b", [("create", pb4, {"text": "yangi kalit", "createdAt": 30})])
    ok_new = at_uri("did:b", pb4) in n.app.timeline("did:b", 1)
    pb5 = n.path("did:b", POST)
    ev = n.mk("did:b", [("create", pb5, {"text": "eski kalit", "createdAt": 31})], key=old_sk, bump=False)
    n.users["did:b"]["records"].pop(pb5)
    n.app.on_event(ev)
    ok_old = at_uri("did:b", pb5) not in n.app.timeline("did:b", 5)
    unit("kalit almashtirildi (Identity): yangi kalitli commit qabul qilinadi, eski kalitli — rad",
         ok_new and ok_old, f"yangi={ok_new}, eski rad={ok_old}")

    n2 = Net()
    n2.add("did:z")
    for i in range(3):
        n2.mk("did:z", [("create", n2.path("did:z", POST), {"text": str(i), "createdAt": i})])
    ev = n2.mk("did:z", [("create", n2.path("did:z", POST), {"text": "3", "createdAt": 3})])
    n2.app.on_event(ev)
    asked = list(n2.asked)
    n2.app.on_resync(n2.snap("did:z"))
    unit("kech qo'shilgan AppView: birinchi ko'rgan commiti prev != None — butun repo so'raladi",
         asked == ["did:z"] and len(n2.app.timeline("did:z", 10)) == 4, f"so'rovlar={asked}")

    n3 = Net()
    n3.add("did:y")
    ev = [n3.mk("did:y", [("create", n3.path("did:y", POST), {"text": str(i), "createdAt": i})]) for i in range(5)]
    n3.app.on_event(ev[0])
    n3.app.on_event(ev[2])                       # ev[1] yo'q -> surat so'raladi
    n3.app.on_event(ev[4])                       # buferga (ev[3] ham yo'q)
    n3.app.on_resync(RepoSnapshot("did:y", ev[1].rev,
                                  {op[1]: op[2] for e in ev[:2] for op in e.ops}))
    asked = list(n3.asked)
    n3.app.on_resync(n3.snap("did:y"))
    unit("suratdan keyin buferda yana bo'shliq qolsa — surat yana so'raladi",
         asked == ["did:y", "did:y"] and len(n3.app.timeline("did:y", 10)) == 5,
         f"so'rovlar={asked}, postlar={len(n3.app.timeline('did:y', 10))}")


# ============================================================ 3. xaos
def part_chaos():
    print("3. Xaos: yomon relay va tarmoq")
    fails, t0, resyncs = [], time.time(), 0
    for seed in range(25):
        s = Sim(app_mod.AppView, seed=seed, steps=1200)
        asked = []
        orig = s.request_resync

        def counting(did, _o=orig, _a=asked):
            _a.append(did)
            _o(did)
        s.app.request_resync = counting
        ok, err = attempt(s.run)
        if err or not ok:
            fails.append((seed, err or "yakunlanmadi"))
            continue
        resyncs += len(asked)
        t = s.truth()
        _, likes, followers, _, _ = t
        problem = None
        for uri in sorted(s.all_posts | set(likes) | {"at://soxta/post"}):
            if s.app.like_count(uri) != len(likes.get(uri, ())):
                problem = f"like_count({uri}) = {s.app.like_count(uri)}, kerak {len(likes.get(uri, ()))}"
                break
        if problem is None:
            for d in sorted(s.users):
                if s.app.follower_count(d) != len(followers.get(d, ())):
                    problem = f"follower_count({d}) = {s.app.follower_count(d)}, kerak {len(followers.get(d, ()))}"
                    break
                if s.app.timeline(d, 30) != s.truth_timeline(d, 30, t):
                    problem = f"timeline({d}) mos emas"
                    break
        if problem:
            fails.append((seed, problem))
    check(f"25 ta stsenariy (3% yo'qolish, 3% takror, o'rin almashish, soxta commitlar, kalit almashtirish, "
          f"hisob o'chirish; {resyncs} ta resinxronizatsiya): yakuniy indeks haqiqiy repolar bilan bir xil",
          not fails, f"seed={fails[0][0]}: {fails[0][1]}" if fails else f"{time.time() - t0:.1f} s")


# ============================================================ 4. tezlik
def part_speed():
    print("4. Tezlik: 'Following' tasmasi")
    n = Net()
    rng = random.Random(5)
    authors = [f"did:w{i:03d}" for i in range(500)]
    for d in authors + ["did:viewer"]:
        n.add(d)
    for d in authors:
        ops = [("create", f"{POST}/{j:04d}", {"text": "x", "createdAt": rng.randint(0, 10**6)}) for j in range(200)]
        n.send(d, ops)
    n.send("did:viewer", [("create", f"{FOLLOW}/{i:04d}", {"subject": d}) for i, d in enumerate(authors)])
    t0 = time.time()
    first = None
    done = 0
    for _ in range(300):
        tl = n.app.timeline("did:viewer", 50)
        first = first or tl
        done += 1
        if time.time() - t0 > 3.0:
            break
    dt = time.time() - t0
    want = sorted(((rec["createdAt"], at_uri(d, p)) for d in authors for p, rec in n.users[d]["records"].items()),
                  reverse=True)[:50]
    check(f"100 000 post, 500 muallif: 300 ta tasma so'rovi (50 tadan) 3 soniyadan tez "
          f"({done / max(dt, 1e-9):,.0f} so'rov/s), natija to'g'ri",
          done == 300 and dt < 3.0 and first == [u for _, u in want],
          f"{dt:.2f} s" if done == 300 else f"3 s da faqat {done} ta so'rov")


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
    run(part_mst)
    n = len(results)
    ok_units = run(part_app_units) and all(results[n:])
    if ok_units:
        run(part_chaos)
        run(part_speed)
    else:
        print("3-4. O'tkazib yuborildi: avval AppView birlik testlari to'liq o'tsin")
        results.append(False)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
