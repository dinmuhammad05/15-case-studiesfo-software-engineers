"""Buyurtmalar kitobi (order book) — 2-daraja topshirig'ining 1-qismi. To'qqizta usul TODO.

Darsdan: 2-bo'lim (kitob va narx-vaqt ustuvorligi), 5-bo'lim 1-5-qadamlar.

Qoidalar (check.py aynan shularni tekshiradi):
  * Narx-vaqt ustuvorligi: kelgan buyurtma avval eng yaxshi narxdagi, bir
    narxda esa eng oldin kelgan buyurtmalar bilan bajariladi.
  * Bitim narxi — kitobda turgan (maker) buyurtmaning narxi.
  * Kesishish: xarid narxi >= eng yaxshi sotuv narxi (yoki sotuv narxi <=
    eng yaxshi xarid narxi). Market buyurtmasi (price=None) har doim kesishadi.
  * Qoldiq: GTC — kitobga (navbat oxiriga); IOC — Cancelled(..., "ioc");
    market — Cancelled(..., "market").
  * FOK: avval "yetadimi?" tekshiriladi; yetmasa — hech qanday bitim yo'q,
    [Accepted, Cancelled(oid, qty, "fok")].
  * STP: kelgan buyurtma navbatda O'Z EGASINING buyurtmasiga yetsa — o'sha
    joyda to'xtaydi, qoldig'i Cancelled(..., "stp"), kitobdagi buyurtma
    tegilmaydi. Shuning uchun FOK uchun "mavjud miqdor" ham faqat birinchi o'z
    buyurtmasigacha sanaladi.
  * Tezlik: eng yaxshi narxni topish va bekor qilish kitob hajmiga chiziqli
    bog'liq bo'lmasin (check.py 5-qism: 20 000 buyurtmali kitobda 200 000
    buyruq 6 soniyadan tez). Maslahat: har narx darajasi uchun
    collections.OrderedDict (oid -> [qty, owner]) va narxlarning saralangan
    ro'yxati (bisect).

Hodisalar ketma-ketligi (model.py): submit -> [Accepted, Trade..., (Cancelled)]
yoki [Rejected]; cancel -> [Cancelled(..., "user")] yoki [Rejected(oid, "unknown")];
modify -> [Modified, (Trade...), (Cancelled "stp")] yoki [Rejected].

Tekshiruv: python check.py
"""
from bisect import bisect_left, insort  # noqa: F401
from collections import OrderedDict  # noqa: F401

from model import (BUY, FOK, IOC, SELL, Accepted, Cancelled, Modified, Order,  # noqa: F401
                   Rejected, Trade)


def _is_int(x):
    """True — faqat haqiqiy butun son (bool va float emas)."""
    return isinstance(x, int) and not isinstance(x, bool)


class Book:
    def __init__(self, tick=1):
        self.tick = tick
        # TODO: ma'lumot tuzilmalari. Taklif:
        #   self.levels = {BUY: {}, SELL: {}}   narx -> OrderedDict(oid -> [qty, owner])
        #   self.prices = {BUY: [], SELL: []}   narxlar o'sish tartibida (bisect)
        #   self.total  = {BUY: {}, SELL: {}}   narx -> darajadagi jami miqdor
        #   self.where  = {}                    oid -> (side, price) — tez bekor qilish uchun
        #   self.seen   = set()                 ishlatilgan oid lar (qabul qilinganlar)
        raise NotImplementedError("TODO: Book.__init__")

    # ------------------------------------------------------------ o'qish
    def best_bid(self):
        """Eng yuqori xarid narxi yoki None."""
        raise NotImplementedError("TODO: best_bid")

    def best_ask(self):
        """Eng past sotuv narxi yoki None."""
        raise NotImplementedError("TODO: best_ask")

    def depth(self, side, n=5):
        """[(narx, jami miqdor), ...] — eng yaxshisidan boshlab, ko'pi bilan n ta."""
        raise NotImplementedError("TODO: depth")

    def order(self, oid):
        """Kitobda turgan buyurtmaning qolgan miqdori yoki None."""
        raise NotImplementedError("TODO: order")

    def state(self):
        """Solishtirish uchun to'liq holat:
        ((bid darajalari), (ask darajalari)), har daraja — (narx, ((oid, qty), ...)),
        darajalar eng yaxshisidan, daraja ichida — navbat tartibida."""
        raise NotImplementedError("TODO: state")

    # ------------------------------------------------------------ buyruqlar
    def submit(self, o: Order):
        """Yangi buyurtma.

        Tekshiruvlar (shu tartibda; rad etilgan oid "ishlatilgan" hisoblanmaydi):
          1. o.oid avval qabul qilingan bo'lsa -> Rejected(oid, "dup")
          2. qty butun va > 0 emas -> "qty"
          3. price None emas va (butun emas yoki <= 0 yoki tick ga karrali emas) -> "tick"
          4. post_only va (market yoki darhol kesishadi) -> "post_only"
        Keyin: Accepted, FOK tekshiruvi, bajarish (_match), qoldiq bilan ishlash."""
        raise NotImplementedError("TODO: submit")

    def cancel(self, oid):
        """Kitobdagi buyurtmani olib tashlaydi: [Cancelled(oid, qolgan, "user")]."""
        raise NotImplementedError("TODO: cancel")

    def modify(self, oid, qty, price=None):
        """Buyurtmani o'zgartiradi. qty — YANGI QOLGAN miqdor; price=None — narx o'zgarmaydi.

        * kitobda yo'q -> "unknown"; qty yaroqsiz -> "qty"; narx yaroqsiz -> "tick".
        * Narx o'sha va qty <= hozirgi qoldiq: joyida kamaytirish, NAVBAT SAQLANADI.
        * Aks holda (narx o'zgardi yoki miqdor oshdi): kitobdan olib, [Modified]
          dan keyin yangi buyurtmadek bajarish (kesishsa — bitim, STP ham amal
          qiladi), qoldig'i — yangi narxda navbat OXIRIGA (GTC kabi)."""
        raise NotImplementedError("TODO: modify")
