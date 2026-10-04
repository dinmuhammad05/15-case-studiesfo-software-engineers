"""Bloom filtri — 2-daraja topshirig'ining 2-qismi. To'rtta joy TODO.

Darsdan: 6-bo'lim 7-qadam. "Bu kalit ANIQ yo'q" yoki "bo'lishi mumkin":
yo'q kalitlarni bazaga yubormasdan rad etish.

Qoidalar:
  * Bloom(n, p): n — kutilayotgan elementlar soni, p — noto'g'ri ijobiy ulush.
      m = ceil(-n * ln(p) / ln(2)^2)      (bitlar soni)
      k = max(1, round(m / n * ln(2)))   (xesh funksiyalar soni)
    Bitlar — bytearray((m + 7) // 8), p-bit: bits[p >> 3] & (1 << (p & 7)).
  * Pozitsiyalar — "ikki xesh" usuli (Kirsch-Mitzenmacher):
      h1 = stable_hash("b1", kalit), h2 = stable_hash("b2", kalit) | 1
      i-pozitsiya = (h1 + i * h2) % m,  i = 0..k-1
    (| 1 — h2 hech qachon 0 bo'lmasin, aks holda k ta pozitsiya bitta bo'lib qoladi.)
  * add(kalit) — k ta bitni yoqadi; `kalit in filtr` — k ta bitning HAMMASI
    yoniqmi. Noto'g'ri manfiy javob bo'lmasligi shart.

Tekshiruv: python check.py
"""
import math  # noqa: F401

from model import stable_hash  # noqa: F401


class Bloom:
    def __init__(self, n: int, p: float):
        # TODO: self.m, self.k va self.bits
        raise NotImplementedError("Bloom.__init__")

    def _positions(self, key):
        # TODO: k ta pozitsiya ro'yxati
        raise NotImplementedError("Bloom._positions")

    def add(self, key):
        # TODO
        raise NotImplementedError("Bloom.add")

    def __contains__(self, key):
        # TODO
        raise NotImplementedError("Bloom.__contains__")
