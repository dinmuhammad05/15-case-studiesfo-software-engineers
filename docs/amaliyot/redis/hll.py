"""HyperLogLog — 2-daraja topshirig'ining 2-qismi. To'rtta joy TODO.

Darsdan: 5-bo'lim 8-stsenariy, 7-bo'lim. Redis'dagi kabi: 2^14 = 16384
registr, 64 bitli xesh, standart xato 1.04 / sqrt(16384) = 0.81%.

Qoidalar:
  * Xesh: h = stable_hash("hll", element) — 64 bit.
  * index_rank(h): registr raqami — h ning QUYI 14 biti. Qolgan 50 bit
    (w = h >> 14) dagi OXIRGI (quyi) nollar soni + 1 — "rank". w == 0
    bo'lsa rank = 51. Masalan: w = ...1000 (ikkilikda) -> rank 4.
  * add(element): reg[i] = max(reg[i], rank). Registr o'zgarsa True,
    aks holda False (Redis PFADD ham shunday javob beradi).
  * count(): alpha = 0.7213 / (1 + 1.079 / M);
      E = alpha * M^2 / sum(2^(-reg[j]))
    Kichik n uchun tuzatish: E <= 2.5 * M va bo'sh (0) registrlar V > 0
    bo'lsa — E = M * ln(M / V) ("linear counting"). Butun songa yaxlitlang.
  * merge(other): har registrda maksimum (PFMERGE). Natija — ikki
    to'plam birlashmasining HLL i bilan AYNAN bir xil.

Tekshiruv: python check.py
"""
import math  # noqa: F401

from model import stable_hash  # noqa: F401

P_BITS = 14
M = 1 << P_BITS


def index_rank(h):
    # TODO: (registr raqami, rank)
    raise NotImplementedError("index_rank")


class HLL:
    def __init__(self):
        self.reg = bytearray(M)      # Redis 6 bit ishlatadi (12 KB); bu yerda bayt — soddalik uchun

    def add(self, item):
        # TODO
        raise NotImplementedError("HLL.add")

    def count(self):
        # TODO
        raise NotImplementedError("HLL.count")

    def merge(self, other):
        # TODO
        raise NotImplementedError("HLL.merge")
