"""Buyurtmalar va hodisalar (tayyor, o'zgartirmang).

Narx va miqdor — faqat butun sonlar. Narx "tick"larda (masalan, tiyinda):
10 050 = 100.50 so'm. Float ishlatilmaydi — 0.1 + 0.2 != 0.3 (darsning
5-bo'limi, 2-qadam).

Order     — kiruvchi buyurtma
Accepted  — buyurtma qabul qilindi (tekshiruvdan o'tdi)
Rejected  — rad etildi; reason: "qty", "tick", "dup", "post_only", "unknown"
Trade     — bitim: taker (kelgan buyurtma) va maker (kitobda turgan) o'rtasida
Cancelled — qoldiq bekor qilindi; reason: "user", "ioc", "market", "fok", "stp"
Modified  — buyurtma o'zgartirildi (yangi narx va QOLGAN miqdor)
"""
from dataclasses import dataclass
from typing import Optional

BUY, SELL = "B", "S"
GTC, IOC, FOK = "GTC", "IOC", "FOK"


@dataclass(frozen=True)
class Order:
    oid: int
    owner: str
    side: str                    # "B" yoki "S"
    qty: int
    price: Optional[int] = None  # None — bozor (market) buyurtmasi
    tif: str = GTC               # GTC — kitobda qoladi; IOC — darhol yoki bekor; FOK — to'liq yoki hech
    post_only: bool = False      # faqat kitobga qo'shilishi kerak; darhol bitim bo'lsa — rad


@dataclass(frozen=True)
class Accepted:
    oid: int


@dataclass(frozen=True)
class Rejected:
    oid: int
    reason: str


@dataclass(frozen=True)
class Trade:
    taker: int
    maker: int
    price: int
    qty: int


@dataclass(frozen=True)
class Cancelled:
    oid: int
    qty: int      # bekor qilingan (bajarilmagan) miqdor
    reason: str


@dataclass(frozen=True)
class Modified:
    oid: int
    price: int
    qty: int      # o'zgartirishdan keyingi qolgan miqdor


# ---------------------------------------------------------------- bozor ma'lumotlari (L2)

@dataclass(frozen=True)
class Update:
    """Bitta narx darajasining yangi holati. qty — darajadagi JAMI miqdor (0 — daraja yo'qoldi).

    seq — oqimdagi tartib raqami: 1, 2, 3, ... bo'shliqsiz. Qiymat "absolyut",
    ya'ni "+5" emas, "endi 120": bitta yangilanishni ikki marta qo'llash zarar
    qilmaydi, lekin ESKI yangilanishni yangi holat ustiga qo'llash — xato.
    """
    seq: int
    side: str
    price: int
    qty: int


@dataclass(frozen=True)
class Snapshot:
    """Butun kitobning L2 surati: seq — suratga kirgan oxirgi yangilanish raqami."""
    seq: int
    bids: dict   # narx -> jami miqdor
    asks: dict
