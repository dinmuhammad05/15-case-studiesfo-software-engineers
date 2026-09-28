"""L2 bozor ma'lumotlari mijozi — 2-daraja topshirig'ining 2-qismi. Ikki usul TODO.

Darsdan: 5-bo'lim 8-qadam, 7-bo'lim. Birja har o'zgargan narx darajasini
tartib raqamli xabar bilan e'lon qiladi (model.Update). Mijoz (broker,
treyder) shu xabarlardan kitobning o'z nusxasini quradi. Tarmoq (UDP
multicast) xabarni yo'qotishi, takrorlashi va tartibini buzishi mumkin.

Mijoz qoidalari:
  * seq == self.seq + 1  -> qo'llash (qty == 0 bo'lsa — darajani o'chirish).
  * seq <= self.seq      -> takror yoki eski: e'tiborsiz (qiymat absolyut,
                            eskisini qo'llash yangi holatni buzadi).
  * seq > self.seq + 1   -> bo'shliq: nusxa endi ishonchsiz. self.waiting = True,
                            xabarni buferga saqlash, self.request_snapshot() ni
                            chaqirish. Kutish paytida kelgan hamma xabar — buferga.
  * Surat kelganda: nusxani surat bilan almashtirish (self.seq = surat.seq),
    keyin buferdagilarni seq bo'yicha tartiblab: suratdan eskilarini tashlash,
    ketma-ketlarini qo'llash; yana bo'shliq bo'lsa — yana surat so'rash.

check.py quyidagi atributlarni o'qiydi: bids, asks (narx -> miqdor), seq, waiting.

Tekshiruv: python check.py
"""
from model import BUY  # noqa: F401


class L2Client:
    def __init__(self, request_snapshot):
        self.request_snapshot = request_snapshot   # chaqirilsa, keyinroq on_snapshot keladi
        self.bids = {}
        self.asks = {}
        self.seq = 0            # oxirgi qo'llangan xabar raqami (0 — bo'sh kitobdan boshlanadi)
        self.waiting = False    # True — surat kutilyapti
        self.buffer = []

    def _apply(self, u):
        lv = self.bids if u.side == BUY else self.asks
        if u.qty == 0:
            lv.pop(u.price, None)
        else:
            lv[u.price] = u.qty
        self.seq = u.seq

    def on_update(self, u):
        """Tarmoqdan kelgan bitta model.Update."""
        raise NotImplementedError("TODO: on_update")

    def on_snapshot(self, s):
        """So'ralgan model.Snapshot keldi. Kutmayotgan bo'lsak yoki surat
        bizning holatimizdan eski bo'lsa (s.seq < self.seq) — e'tiborsiz."""
        raise NotImplementedError("TODO: on_snapshot")
