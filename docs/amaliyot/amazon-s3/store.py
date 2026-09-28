"""Ob'ekt ombori — 2-daraja topshirig'i. Oltita joy TODO.

Darsdan: erasure coding (5-bo'lim 7-8-qadamlar, 7-bo'lim), metadata va
ma'lumotni ajratish (2-qadam), nazorat summalari (5-qadam), joylashtirish
qoidalari (4-qadam, 6.1), doimiy tekshiruv va tiklash (6-qadam).

Yordamchilar:
  gf.py      — GF(256): mul, inv, scale(block, c), xor(a, b), mat_inv(M)
  cluster.py — Disk: write(data) -> chunk_id, read(chunk_id), delete, az, alive, used
  zlib.crc32 — nazorat summasi

Tekshiruv: python check.py
"""
import math  # noqa: F401
import zlib  # noqa: F401

import gf  # noqa: F401
from cluster import DiskDead  # noqa: F401


class LostError(Exception):
    """Ob'ektni tiklash uchun sog' bo'laklar yetarli emas (k tadan kam)."""


# ------------------------------------------------------------ Reed-Solomon

def generator(k, m):
    """Tizimli kodlash matritsasi: k + m qator, har qatorda k ta element.

    Birinchi k qator — birlik matritsa (bo'laklar = ma'lumotning o'zi).
    Qolgan m qator — Koshi matritsasi: C[i][j] = gf.inv(x_i ^ y_j),
    bu yerda x_i = k + i, y_j = j. Shunda istalgan k ta qatordan
    tuzilgan matritsa teskarilanadi."""
    raise NotImplementedError("TODO: generator")


def encode(data, k, m):
    """data (bytes) -> k + m ta bir xil uzunlikdagi bo'lak (bytes ro'yxati).

    Bo'lak uzunligi L = ceil(len(data) / k); oxirgi ma'lumot bo'lagi nol
    baytlar bilan to'ldiriladi. Birinchi k bo'lak — ma'lumot bo'laklari
    (tizimli kod). Paritet bo'lagi i: XOR_j scale(d_j, C[i][j]).
    Bo'sh data -> k + m ta bo'sh bo'lak."""
    raise NotImplementedError("TODO: encode")


def decode(shards, k, m, size):
    """shards — {bo'lak_raqami: bytes} (0..k+m-1), kamida k ta.

    Istalgan k tasini tanlang, generator'dan mos qatorlarni oling,
    gf.mat_inv bilan teskarilang va ma'lumot bo'laklarini tiklang.
    Natija — dastlabki size bayt. k tadan kam bo'lsa — LostError."""
    raise NotImplementedError("TODO: decode")


# -------------------------------------------------------------- Ob'ekt ombori

class Store:
    """Metadata (self.index) va ma'lumot (disklar) alohida.

    self.index[key] = {"size": int, "shards": [(disk_id, chunk_id, crc32), ...]}
    — ro'yxatdagi i-element — i-bo'lak (0..k+m-1). Tekshiruv skripti indeksni
    shu shaklda o'qiydi."""

    def __init__(self, disks, k=6, m=3):
        self.disks = {d.id: d for d in disks}
        self.k, self.m = k, m
        self.index = {}

    def _place(self, n, exclude=(), az_count=None):
        """n ta disk tanlang (disk ID lari ro'yxati):
          * faqat tirik disklar, exclude'dagilar emas, hammasi har xil;
          * har AZ dan ko'pi bilan ceil((k + m) / AZ_soni) ta, bu yerda AZ_soni —
            tirik diski bor AZ lar soni (butun AZ o'lsa, qolganlarga ko'proq);
            az_count (AZ -> shu ob'ektda allaqachon band bo'laklar) hisobga olinsin;
          * eng kam band (disk.used) disklar afzal, teng bo'lsa — disk ID bo'yicha.
        Yetarli disk bo'lmasa — RuntimeError."""
        raise NotImplementedError("TODO: _place")

    def put(self, key, data):
        """Kodlash, har bo'lakni o'z diskiga yozish (crc32 bilan), keyin
        indeks yozuvi. Kalit mavjud bo'lsa — eski bo'laklar o'chiriladi."""
        raise NotImplementedError("TODO: put")

    def get(self, key):
        """Bo'laklarni o'qing; o'lik disk, yo'q bo'lak yoki crc32 mos kelmasa —
        o'sha bo'lakni tashlab keting. Sog' bo'laklar k tadan kam bo'lsa —
        LostError (hech qachon noto'g'ri baytlar emas!). Kalit yo'q — KeyError."""
        raise NotImplementedError("TODO: get")

    def scrub(self):
        """Hamma ob'ektni tekshiring. Har buzilgan bo'lakni (o'lik disk,
        yo'q bo'lak, crc32 mos emas) qayta hisoblab, YANGI diskka yozing
        (joylashtirish qoidalari bilan: shu ob'ektning boshqa bo'laklari
        turgan disklarga emas, AZ chegarasi bilan) va indeksni yangilang.
        Tiklangan bo'laklar sonini qaytaring. Tiklab bo'lmaydigan ob'ektlarni
        o'tkazib yuboring."""
        raise NotImplementedError("TODO: scrub")
