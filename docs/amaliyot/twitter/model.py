"""Tayyor qismlar (o'zgartirmang): soxta soat va darajali (power-law) obunalar grafi.

Vaqt bu yerda "mantiqiy": post ID lari ham, obuna paytlari ham bitta o'suvchi
hisoblagichdan olinadi. Shuning uchun "post obunadan keyin yozilganmi" degan
savol oddiy taqqoslash: post_id > since.
"""
import random


class FakeClock:
    """Millisekund qaytaruvchi soat. Testlar uni xohlagancha boshqaradi:
    to'xtatadi, oldinga suradi, hatto orqaga qaytaradi."""

    def __init__(self, start_ms=1_700_000_000_000):
        self.ms = start_ms
        self.calls = 0
        self.auto = 0          # har chaqiruvda shuncha ms qo'shiladi (0 — to'xtagan)

    def __call__(self):
        self.calls += 1
        v = self.ms
        self.ms += self.auto
        return v


def power_law_graph(n_users, avg_following, alpha=1.1, seed=0):
    """Obunalar grafi: kim kimga obuna. Mashhurlik darajali taqsimotga
    bo'ysunadi — bir nechta akkauntda juda ko'p obunachi, ko'pchilikda oz.
    Qaytaradi: {foydalanuvchi: [obuna bo'lganlari]}."""
    rng = random.Random(seed)
    weights = [1.0 / (i + 1) ** alpha for i in range(n_users)]
    total = sum(weights)
    cum, acc = [], 0.0
    for w in weights:
        acc += w / total
        cum.append(acc)
    import bisect
    graph = {}
    for u in range(n_users):
        k = max(1, int(rng.expovariate(1 / avg_following)))
        seen = set()
        for _ in range(k):
            a = min(bisect.bisect_left(cum, rng.random()), n_users - 1)
            if a != u:
                seen.add(a)
        graph[u] = sorted(seen)
    return graph
