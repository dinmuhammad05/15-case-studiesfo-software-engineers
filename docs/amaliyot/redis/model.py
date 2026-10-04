"""Tayyor qismlar (o'zgartirmang): skiplist tuguni, barqaror xesh, Zipf trafigi.

Bu — Redis'ning uchta ichki mexanizmining o'quv modeli. Tezlik emas,
TO'G'RI tuzilma tekshiriladi: check.py skiplistning ko'rsatkichlari va
span'larini, HLL registrlarini va ekspirasiya statistikasini o'zi ko'radi.
"""
import bisect
import hashlib
import random

MAX_LEVEL = 32      # Redis: ZSKIPLIST_MAXLEVEL
P = 0.25            # Redis: ZSKIPLIST_P — yuqori darajaga chiqish ehtimoli


class Node:
    """Skiplist tuguni. forward[i] — i-darajadagi keyingi tugun (yoki None),
    span[i] — o'sha ko'rsatkich 0-darajada nechta qadamni "sakrab o'tadi"
    (rank hisoblash uchun). backward — 0-darajadagi oldingi tugun."""
    __slots__ = ("member", "score", "forward", "span", "backward")

    def __init__(self, member, score, level):
        self.member = member
        self.score = score
        self.forward = [None] * level
        self.span = [0] * level
        self.backward = None


def stable_hash(*parts) -> int:
    """Jarayondan jarayonga o'zgarmaydigan 64 bitli xesh (Python hash() dan farqli)."""
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(h[:8], "big")


class Zipf:
    """i-element og'irligi 1 / (i+1)^s: kam sonli kalitlar ko'p so'raladi."""

    def __init__(self, n: int, s: float = 1.0, seed: int = 0):
        self.rng = random.Random(seed)
        acc, self.cum = 0.0, []
        for i in range(n):
            acc += 1.0 / (i + 1) ** s
            self.cum.append(acc)
        self.total = acc

    def sample(self) -> int:
        return bisect.bisect_left(self.cum, self.rng.random() * self.total)
