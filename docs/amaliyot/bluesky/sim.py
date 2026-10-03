"""Tarmoq simulyatori (tayyor, o'zgartirmang).

Bir nechta foydalanuvchi (har biri o'z PDS'ida) post yozadi, tahrirlaydi,
o'chiradi, like va follow qiladi. Har commit imzolanadi va relay orqali
firehose'ga chiqadi. Tarmoq va relay "yomon": hodisalar yo'qoladi,
takrorlanadi, qo'shnilar o'rni almashadi, soxta commitlar qo'shiladi,
kalitlar almashtiriladi, hisoblar o'chiriladi va qaytariladi. Yo'qolishi
mumkin va o'rni almashishi mumkin bo'lgani — faqat commitlar (Identity va
Account hodisalari tartib bilan yetib keladi, lekin takrorlanishi mumkin).
AppView so'ragan resinxronizatsiya (butun repo) kechikib yetkaziladi.

Oxirida AppView indeksi "haqiqat" — PDS'lardagi yakuniy repolar — bilan
solishtiriladi (check.py).
"""
import random

from model import (FOLLOW, LIKE, POST, Account, Commit, Identity, RepoSnapshot,
                   at_uri, commit_bytes, keypair, sign)


class User:
    def __init__(self, did):
        self.did = did
        self.gen = 0
        self.secret, self.public = keypair(f"{did}#0")
        self.rev = 0
        self.records = {}
        self.active = True
        self.n = 0

    def rkey(self):
        self.n += 1
        return f"{self.n:06d}"


class Sim:
    def __init__(self, appview_cls, seed=0, users=12, steps=1500, drop=0.03, dup=0.03, swap=0.05,
                 forge=0.02, rotate=0.004, toggle=0.004):
        self.rng = random.Random(seed)
        self.users = {f"did:plc:u{i:02d}": User(f"did:plc:u{i:02d}") for i in range(users)}
        self.steps = steps
        self.p = dict(drop=drop, dup=dup, swap=swap, forge=forge, rotate=rotate, toggle=toggle)
        self.seq = 0
        self.clock = 0
        self.net = []                   # yo'ldagi hodisalar
        self.resyncs = []               # [kechikish, did]
        self.all_posts = set()
        self.app = appview_cls(self.resolve, self.request_resync)

    # ------------------------------------------------------------ AppView uchun
    def resolve(self, did):
        """DID hujjatidan joriy ochiq kalit."""
        return self.users[did].public

    def request_resync(self, did):
        self.resyncs.append([self.rng.randint(1, 25), did])

    # ------------------------------------------------------------ PDS
    def _emit(self, ev):
        self.net.append(ev)

    def _next_seq(self):
        self.seq += 1
        return self.seq

    def commit(self, u, ops):
        prev = u.rev if u.rev else None
        u.rev += 1
        for action, path, rec in ops:
            if action == "delete":
                u.records.pop(path, None)
            else:
                u.records[path] = rec
        ops = tuple(ops)
        sig = sign(u.secret, commit_bytes(u.did, u.rev, prev, ops))
        ev = Commit(self._next_seq(), u.did, u.rev, prev, ops, sig)
        self._emit(ev)

    def random_ops(self, u):
        rng = self.rng
        ops = []
        for _ in range(rng.choice([1, 1, 1, 2, 3])):
            r = rng.random()
            mine = list(u.records)
            if r < 0.35 or not mine:
                path = f"{POST}/{u.rkey()}"
                self.clock += 1
                rec = {"text": f"salom {self.clock}", "createdAt": self.clock if rng.random() > 0.1
                       else self.clock - rng.randint(0, 50)}
                self.all_posts.add(at_uri(u.did, path))
                ops.append(("create", path, rec))
            elif r < 0.6 and self.all_posts:
                ops.append(("create", f"{LIKE}/{u.rkey()}", {"subject": rng.choice(sorted(self.all_posts))}))
            elif r < 0.75:
                ops.append(("create", f"{FOLLOW}/{u.rkey()}", {"subject": rng.choice(sorted(self.users))}))
            elif r < 0.85:
                posts = [p for p in mine if p.startswith(POST)]
                if posts:
                    p = rng.choice(posts)
                    old = u.records[p]
                    ops.append(("update", p, {"text": old["text"] + " (tahrir)", "createdAt": old["createdAt"]}))
            else:
                ops.append(("delete", rng.choice(mine), None))
        # bitta commit ichida bir yo'lga ikki amal bo'lmasin
        seen, uniq = set(), []
        for op in ops:
            if op[1] not in seen and (op[0] == "create" or op[1] in u.records):
                seen.add(op[1])
                uniq.append(op)
        return uniq

    # ------------------------------------------------------------ yomon relay
    def forge(self):
        u = self.users[self.rng.choice(sorted(self.users))]
        fake_secret, _ = keypair("hujumchi" + str(self.rng.random()))
        prev = u.rev if u.rev else None
        ops = (("create", f"{LIKE}/zz{self.rng.randint(0, 10**6)}", {"subject": "at://soxta/post"}),)
        sig = sign(fake_secret, commit_bytes(u.did, u.rev + 1, prev, ops))
        self._emit(Commit(self._next_seq(), u.did, u.rev + 1, prev, ops, sig))

    def deliver(self, force=False):
        rng = self.rng
        if (not force and len(self.net) > 1 and isinstance(self.net[0], Commit)
                and isinstance(self.net[1], Commit) and rng.random() < self.p["swap"]):
            self.net[0], self.net[1] = self.net[1], self.net[0]
        if self.net and (force or rng.random() < 0.85):
            ev = self.net.pop(0)
            x = rng.random() if isinstance(ev, Commit) else 1.0   # hisob va identifikatsiya hodisalari yo'qolmaydi
            if x < self.p["drop"] and not force:
                pass
            elif x < self.p["drop"] + self.p["dup"] and not force:
                self.app.on_event(ev)
                self.app.on_event(ev)
            else:
                self.app.on_event(ev)
        for r in self.resyncs:
            r[0] -= 1
        due = [r for r in self.resyncs if r[0] <= 0]
        self.resyncs = [r for r in self.resyncs if r[0] > 0]
        for _, did in due:
            u = self.users[did]
            self.app.on_resync(RepoSnapshot(did, u.rev, dict(u.records)))

    def step(self):
        rng = self.rng
        u = self.users[rng.choice(sorted(self.users))]
        x = rng.random()
        if x < self.p["rotate"]:
            u.gen += 1
            u.secret, u.public = keypair(f"{u.did}#{u.gen}")
            self._emit(Identity(self._next_seq(), u.did))
        elif x < self.p["rotate"] + self.p["toggle"]:
            u.active = not u.active
            self._emit(Account(self._next_seq(), u.did, u.active))
        elif x < self.p["rotate"] + self.p["toggle"] + self.p["forge"]:
            self.forge()
        else:
            ops = self.random_ops(u)
            if ops:
                self.commit(u, ops)
        self.deliver()

    def run(self):
        for _ in range(self.steps):
            self.step()
        guard = 0
        while self.net or self.resyncs:
            self.deliver(force=True)
            guard += 1
            if guard > 20000:
                return False
        # oxirgi commitlar yo'qolgan bo'lishi mumkin: har PDS joriy kalit bilan bo'sh
        # commit yuboradi (ishonchli) — AppView orqada bo'lsa, bo'shliqni ko'radi
        for did in sorted(self.users):
            self.commit(self.users[did], [])
        while self.net:
            self.deliver(force=True)
        while self.resyncs:
            self.deliver(force=True)
            guard += 1
            if guard > 40000:
                return False
        return True

    # ------------------------------------------------------------ haqiqat
    def truth(self):
        active = {d for d, u in self.users.items() if u.active}
        likes, followers, posts, following = {}, {}, {}, {}
        for d in active:
            for path, rec in self.users[d].records.items():
                coll = path.split("/", 1)[0]
                if coll == LIKE:
                    likes.setdefault(rec["subject"], set()).add(d)
                elif coll == FOLLOW:
                    followers.setdefault(rec["subject"], set()).add(d)
                    following.setdefault(d, set()).add(rec["subject"])
                elif coll == POST:
                    posts.setdefault(d, []).append((rec["createdAt"], at_uri(d, path)))
        return active, likes, followers, posts, following

    def truth_timeline(self, viewer, limit, t):
        active, _, _, posts, following = t
        if viewer not in active:
            return []
        authors = (following.get(viewer, set()) | {viewer}) & active
        allp = sorted((p for a in authors for p in posts.get(a, [])), reverse=True)
        return [uri for _, uri in allp[:limit]]
