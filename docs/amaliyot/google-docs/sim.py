"""Jupiter uslubidagi OT simulyatori (tayyor, o'zgartirmang).

Bitta server va bir nechta mijoz. Har mijoz darsdagi 5-bo'lim, 4-qadam
holat mashinasini bajaradi: bitta operatsiya yo'lda, qolgani buferda.
Tarmoq — har yo'nalishda FIFO navbat (TCP kabi), lekin xabarlar
tasodifiy paytda yetkaziladi: ya'ni parallellik doimiy.

Ishlatish:
  python sim.py                       # 200 ta tasodifiy stsenariy
  python sim.py --seeds 1000 --clients 5
  python sim.py --seed 17 --verbose   # bitta stsenariy, har qadam jurnali

Stsenariy muvaffaqiyatli, agar oxirida barcha mijozlar va server bir xil
matnga ega bo'lsa ("yaqinlashish").
"""
import argparse
import random

import ot

ALPHABET = "abcdefgh"


class Server:
    def __init__(self, doc):
        self.doc = doc
        self.history = []          # [(mijoz, op)] — revision = indeks + 1
        self.transforms = 0

    def receive(self, cid, base_rev, op):
        # Mijoz ko'rmagan operatsiyalar (5-bo'lim, 4-qadam; 6.2)
        for _, past in self.history[base_rev:]:
            _, op = ot.transform(past, op)       # tarixdagi op birinchi: bog'lashda u oldinda
            self.transforms += 1
        self.doc = ot.apply(self.doc, op)        # uzunlik mos kelmasa -> ValueError
        self.history.append((cid, op))
        return len(self.history), op


class Client:
    def __init__(self, cid, doc):
        self.cid = cid
        self.doc = doc
        self.rev = 0               # oxirgi ko'rilgan server revision
        self.pending = None        # yo'ldagi (tasdiqlanmagan) operatsiya
        self.buffer = None         # hali yuborilmagan
        self.cursor = 0
        self.outbox = []           # serverga ketadigan xabarlar (sim o'qiydi)

    def local(self, op, cursor):
        self.doc = ot.apply(self.doc, op)
        self.cursor = cursor
        if self.pending is None:
            self.pending = op
            self.outbox.append((self.rev, op))
        elif self.buffer is None:
            self.buffer = op
        else:
            self.buffer = ot.compose(self.buffer, op)

    def on_ack(self):
        self.rev += 1
        self.pending, self.buffer = self.buffer, None
        if self.pending is not None:
            self.outbox.append((self.rev, self.pending))

    def on_remote(self, op):
        self.rev += 1
        if self.pending is not None:
            op, self.pending = ot.transform(op, self.pending)
        if self.buffer is not None:
            op, self.buffer = ot.transform(op, self.buffer)
        self.doc = ot.apply(self.doc, op)
        self.cursor = ot.transform_cursor(self.cursor, op)


def random_edit(rng, doc, tokens=None):
    """Tasodifiy lokal tahrir: (op, yangi_kursor)."""
    n = len(doc)
    if tokens is not None:
        # Faqat qo'shish: noyob token, mavjud tokenlar CHEGARASIGA
        bounds = [0] + [i + 1 for i, ch in enumerate(doc) if ch == "]"]
        p = rng.choice(bounds)
        return ot.normalize([p, tokens(), n - p]), p
    p = rng.randint(0, n)
    r = rng.random()
    if r < 0.5 or n == p:
        s = "".join(rng.choice(ALPHABET) for _ in range(rng.randint(1, 3)))
        return ot.normalize([p, s, n - p]), p + len(s)
    k = rng.randint(1, min(4, n - p))
    if r < 0.85:
        return ot.normalize([p, -k, n - p - k]), p
    s = rng.choice(ALPHABET).upper()          # almashtirish: o'chirish + qo'shish
    return ot.normalize([p, s, -k, n - p - k]), p + 1


def run(seed, clients=3, steps=300, tokens_mode=False, verbose=False):
    rng = random.Random(seed)
    start = "" if tokens_mode else "".join(rng.choice(ALPHABET) for _ in range(rng.randint(0, 12)))
    server = Server(start)
    cs = [Client(i, start) for i in range(clients)]
    to_server = []                       # [(cid, base_rev, op)] — FIFO
    to_client = [[] for _ in cs]         # har mijozga FIFO: ("ack",) yoki ("op", op)
    counter = [0]

    def new_token():
        counter[0] += 1
        return f"[{counter[0]}]"

    def flush_outboxes():
        for c in cs:
            for base, op in c.outbox:
                to_server.append((c.cid, base, op))
            c.outbox.clear()

    def deliver_server():
        cid, base, op = to_server.pop(0)
        rev, applied = server.receive(cid, base, op)
        for c in cs:
            to_client[c.cid].append(("ack",) if c.cid == cid else ("op", applied))
        if verbose:
            print(f"  server <- m{cid} (asos v{base}) -> v{rev}: {applied!r}  matn={server.doc!r}")

    def deliver_client(i):
        msg = to_client[i].pop(0)
        c = cs[i]
        if msg[0] == "ack":
            c.on_ack()
        else:
            c.on_remote(msg[1])
        if verbose:
            print(f"  m{i} <- {msg[0]}  matn={c.doc!r} kursor={c.cursor}")

    for _ in range(steps):
        r = rng.random()
        if r < 0.45:
            c = rng.choice(cs)
            op, cur = random_edit(rng, c.doc, new_token if tokens_mode else None)
            c.local(op, cur)
            if verbose:
                print(f"m{c.cid} tahrir {op!r} -> {c.doc!r}")
        elif r < 0.7 and to_server:
            deliver_server()
        else:
            ready = [i for i in range(len(cs)) if to_client[i]]
            if ready:
                deliver_client(rng.choice(ready))
        flush_outboxes()
        for c in cs:
            if not (0 <= c.cursor <= len(c.doc)):
                raise AssertionError(f"m{c.cid} kursori matndan tashqarida: {c.cursor} / {len(c.doc)}")

    # Tarmoqni bo'shatish
    while to_server or any(to_client):
        if to_server:
            deliver_server()
        for i in range(len(cs)):
            while to_client[i]:
                deliver_client(i)
        flush_outboxes()

    docs = [c.doc for c in cs]
    ok = all(d == server.doc for d in docs)
    return {
        "ok": ok, "server": server.doc, "clients": docs,
        "revisions": len(server.history), "transforms": server.transforms,
        "tokens": counter[0],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--clients", type=int, default=3)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--tokens", action="store_true", help="faqat noyob tokenlarni qo'shish")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    seeds = [a.seed] if a.seed is not None else range(a.seeds)
    bad = 0
    total_rev = total_tr = 0
    for s in seeds:
        try:
            res = run(s, a.clients, a.steps, a.tokens, a.verbose)
        except NotImplementedError:
            raise SystemExit("ot.py da TODO qolgan — funksiyalarni yozing.")
        except Exception as e:  # noqa: BLE001 — xatoni stsenariy raqami bilan ko'rsatish
            bad += 1
            print(f"seed {s}: XATO {type(e).__name__}: {e}")
            continue
        total_rev += res["revisions"]
        total_tr += res["transforms"]
        if not res["ok"]:
            bad += 1
            if bad <= 3:
                print(f"seed {s}: AJRALISH  server={res['server']!r}")
                for i, d in enumerate(res["clients"]):
                    print(f"          m{i}={d!r}")
    n = len(list(seeds))
    print(f"\n{n - bad}/{n} stsenariy yaqinlashdi; "
          f"jami {total_rev:,} revision, {total_tr:,} server transform "
          f"(o'rtacha k = {total_tr / max(1, total_rev):.2f})")
    if bad:
        print(f"Birinchi xatoni ko'rish: python sim.py --seed <raqam> --verbose")


if __name__ == "__main__":
    main()
