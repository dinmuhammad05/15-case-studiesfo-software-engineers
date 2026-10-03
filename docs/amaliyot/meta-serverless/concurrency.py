"""AIMD tirbandlik nazorati — 2-daraja topshirig'ining 2-qismi. Bitta usul TODO.

Darsdan: 5-bo'lim 11-qadam. Downstream xizmat (masalan, ma'lumotlar bazasi)
o'z sig'imini aytmaydi — faqat ortiqcha yuklanganda "sekinlash" (xato,
kechikish) signalini beradi. Funksiyalar platformasi TCP kabi ishlaydi:
signal yo'q bo'lsa — chegarani asta oshiradi, signal bo'lsa — keskin kamaytiradi.

on_tick(sent, overloaded) har tik oxirida chaqiriladi:
  * sent — shu tikda downstream'ga yuborilgan chaqiruvlar soni;
  * overloaded — ulardan nechtasi "ortiqcha yuklama" javobini oldi.
Qoidalar:
  * overloaded > 0  -> limit = max(lo, int(limit * factor))     (ko'paytiruvchi kamayish)
  * aks holda, faqat chegara TO'LIQ ishlatilgan bo'lsa (sent >= limit)
                    -> limit = min(hi, limit + step)             (qo'shuvchi o'sish)
  * chegara ishlatilmagan bo'lsa — o'zgarmaydi (aks holda u "bo'sh" o'sib,
    keyingi portlashda downstream'ni bosib ketadi).

Tekshiruv: python check.py
"""


class AIMD:
    def __init__(self, start=1, lo=1, hi=10_000, step=1, factor=0.5):
        self.lo, self.hi, self.step, self.factor = lo, hi, step, factor
        self.limit = max(lo, min(hi, start))

    def on_tick(self, sent, overloaded):
        raise NotImplementedError("TODO: on_tick")
