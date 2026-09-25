"""Tarmoq izlari: har soniya uchun o'tkazuvchanlik (Mbit/s). TAYYOR.

Izlar deterministik (belgilangan seed) — natijalar har safar bir xil,
shuning uchun algoritmlarni adolatli solishtirish mumkin.
"""
import math
import random

SECONDS = 1200


def _clip(x, lo=0.05):
    return max(lo, x)


def stable_4g(seed=1):
    """Barqaror 4G: ~8 Mbit/s, kichik shovqin."""
    rng = random.Random(seed)
    return [_clip(8.0 * (1 + rng.gauss(0, 0.15))) for _ in range(SECONDS)]


def volatile_3g(seed=2):
    """Tebranuvchi 3G: o'rtacha ~2 Mbit/s, katta va 'yopishqoq' o'zgarishlar."""
    rng = random.Random(seed)
    x, out = math.log(2.0), []
    for _ in range(SECONDS):
        x = 0.9 * x + 0.1 * math.log(2.0) + rng.gauss(0, 0.25)   # AR(1) log-fazoda
        out.append(_clip(math.exp(x)))
    return out


def metro(seed=3):
    """Metro: odatda ~6 Mbit/s, har ~2 daqiqada 20-40 s ga ~0.2 Mbit/s gacha tushadi."""
    rng = random.Random(seed)
    out, t = [], 0
    while t < SECONDS:
        good = rng.randint(80, 140)
        out += [_clip(6.0 * (1 + rng.gauss(0, 0.2))) for _ in range(good)]
        bad = rng.randint(20, 40)
        out += [_clip(0.2 * (1 + rng.gauss(0, 0.3))) for _ in range(bad)]
        t += good + bad
    return out[:SECONDS]


def slow_start(seed=4):
    """Sekin boshlanish: birinchi 30 s ~0.8 Mbit/s, keyin ~10 Mbit/s (Wi-Fi ulandi)."""
    rng = random.Random(seed)
    return [_clip((0.8 if t < 30 else 10.0) * (1 + rng.gauss(0, 0.1))) for t in range(SECONDS)]


TRACES = {
    "4g_barqaror": stable_4g,
    "3g_tebranuvchi": volatile_3g,
    "metro": metro,
    "sekin_boshlanish": slow_start,
}
