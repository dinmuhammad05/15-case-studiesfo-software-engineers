"""Rejalashtiruvchi — 2-daraja topshirig'ining 1-qismi. Uchta usul TODO.

Darsdan: 5-bo'lim 2, 7-9-qadamlar, 8-bo'lim. Navbatdagi chaqiruvlardan har
tikda qaysilarini bajarish kerakligini tanlaydi.

Qoidalar (check.py aynan shularni tekshiradi):
  * submit: cid avval ko'rilgan bo'lsa — False (takror), aks holda navbatga, True.
    Har chaqiruvning submit vaqti — uni yuborgan tik (kelajakdagi emas).
  * pick(now, capacity, limits) — shu tikda bajariladiganlar ro'yxati:
      1. Avval HAR funksiyaning kvotasi to'ldiriladi:
         tokens = min(burst, tokens + rate). Boshlang'ich tokens = burst.
      2. Tartib: kritiklik (yuqorisi oldin), keyin muddat (yaqini oldin),
         keyin submit, keyin cid — kalit (-crit, deadline, submit, cid).
      3. deadline < now bo'lgan chaqiruv hech qachon bajarilmaydi — navbatdan
         tashlanadi (self.dropped ga).
      4. Funksiyada token < 1 bo'lsa yoki uning downstream'i shu tikda
         limits[downstream] taga yetgan bo'lsa — o'tkazib yuboriladi (navbatda
         qoladi), lekin boshqalar tanlanishda davom etadi (bo'sh turmaslik).
      5. Har tanlangan chaqiruv 1 token va downstream'dan 1 o'rin oladi;
         jami capacity tadan ko'p emas.
  * Tezlik: navbatda yuz minglab chaqiruv bo'lishi mumkin — har tikda
    hammasini saralamang. Maslahat: har funksiyaga alohida heap, ularning
    "boshlari" uchun yana bitta heap.

Tekshiruv: python check.py
"""
import heapq  # noqa: F401

from model import Call, Fn  # noqa: F401


class Scheduler:
    def __init__(self, fns):
        self.fns = dict(fns)       # nom -> Fn
        self.dropped = []          # muddati o'tib tashlangan chaqiruvlar
        # TODO: tokenlar, navbatlar, ko'rilgan cid lar
        raise NotImplementedError("TODO: Scheduler.__init__")

    def submit(self, call):
        raise NotImplementedError("TODO: submit")

    def pending(self):
        """Navbatda turgan (tashlanmagan va bajarilmagan) chaqiruvlar soni."""
        raise NotImplementedError("TODO: pending")

    def pick(self, now, capacity, limits=None):
        """limits: {downstream: shu tikdagi eng ko'p chaqiruvlar} yoki None (cheklovsiz)."""
        raise NotImplementedError("TODO: pick")
