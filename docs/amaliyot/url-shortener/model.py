"""Tayyor qismlar (o'zgartirmang): alifbo, barqaror xesh, markaziy hisoblagich,
"ma'lumotlar bazasi" va Zipf taqsimotidagi trafik.

Vaqt — soniyalarda, float. Baza haqiqiy emas: u faqat o'qishlar sonini
sanaydi — kesh va Bloom filtri qanchalik yaxshi ishlayotganini shu son
ko'rsatadi.
"""
import bisect
import hashlib
import random

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)  # 62


def stable_hash(*parts) -> int:
    """Jarayondan jarayonga o'zgarmaydigan 64 bitli xesh (Python hash() dan farqli)."""
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(h[:8], "big")


class Counter:
    """Markaziy hisoblagich (masalan, bitta SQL jadval yoki ZooKeeper tuguni).
    lease(n) — ketma-ket n ta sonlik diapazonning boshini qaytaradi.
    calls — markazga necha marta murojaat qilingani: bu tor joy."""

    def __init__(self, start=0):
        self.value = start
        self.calls = 0

    def lease(self, n: int) -> int:
        self.calls += 1
        start = self.value
        self.value += n
        return start


class Store:
    """Manba haqiqat: kalit -> URL. reads — necha marta o'qilgani."""

    def __init__(self):
        self.data = {}
        self.reads = 0

    def get(self, key):
        self.reads += 1
        return self.data.get(key)

    def put(self, key, url):
        if key in self.data:
            raise KeyError(f"kalit band: {key}")   # UNIQUE cheklovi
        self.data[key] = url

    def delete(self, key):
        self.data.pop(key, None)


class Zipf:
    """i-element og'irligi 1 / (i+1)^s. Kichik qism elementlar trafikning
    katta qismini oladi — havolalar aynan shunday bosiladi."""

    def __init__(self, n: int, s: float = 1.0, seed: int = 0):
        self.rng = random.Random(seed)
        acc, self.cum = 0.0, []
        for i in range(n):
            acc += 1.0 / (i + 1) ** s
            self.cum.append(acc)
        self.total = acc

    def sample(self) -> int:
        return bisect.bisect_left(self.cum, self.rng.random() * self.total)
