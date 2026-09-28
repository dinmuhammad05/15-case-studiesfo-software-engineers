"""Sekvenser, jurnal va bozor ma'lumotlari oqimi (tayyor, o'zgartirmang).

Birjaning "yuragi" — bitta ip (thread) va bitta tartib:

  1. har buyruq (yangi buyurtma, bekor qilish, o'zgartirish) tartib raqami oladi;
  2. jurnalga yoziladi (bu yerda — ro'yxat; haqiqatda — disk va zaxira serverlar);
  3. kitobga qo'llanadi (book.Book);
  4. o'zgargan narx darajalari L2 oqimiga chiqadi (model.Update).

Kitob deterministik bo'lsa, jurnalni boshidan qayta o'ynash AYNAN o'sha
holatni va aynan o'sha hodisalarni beradi — zaxira server shu tarzda
asosiy serverni kuzatib boradi (darsning 5-bo'limi, 6-qadam).
"""
from model import BUY, SELL, Snapshot, Update


class Exchange:
    def __init__(self, book_cls, tick=1):
        self.book = book_cls(tick)
        self.tick = tick
        self.seq = 0            # buyruqlar tartib raqami
        self.journal = []       # (seq, buyruq)
        self.events = []        # (seq, hodisalar ro'yxati)
        self.feed_seq = 0       # L2 oqimi tartib raqami
        self.updates = []       # e'lon qilingan model.Update lar

    def _levels(self):
        return {(s, p): q for s in (BUY, SELL) for p, q in self.book.depth(s, n=10**9)}

    def handle(self, cmd):
        """cmd: ("new", Order) | ("cancel", oid) | ("modify", oid, qty, price)."""
        self.seq += 1
        self.journal.append((self.seq, cmd))
        before = self._levels()
        kind = cmd[0]
        if kind == "new":
            ev = self.book.submit(cmd[1])
        elif kind == "cancel":
            ev = self.book.cancel(cmd[1])
        elif kind == "modify":
            ev = self.book.modify(cmd[1], cmd[2], cmd[3])
        else:
            raise ValueError(kind)
        after = self._levels()
        self.events.append((self.seq, ev))
        for key in sorted(set(before) | set(after)):
            if before.get(key) != after.get(key):
                self.feed_seq += 1
                self.updates.append(Update(self.feed_seq, key[0], key[1], after.get(key, 0)))
        return ev

    def snapshot(self):
        lv = self._levels()
        return Snapshot(self.feed_seq,
                        {p: q for (s, p), q in lv.items() if s == BUY},
                        {p: q for (s, p), q in lv.items() if s == SELL})

    @classmethod
    def replay(cls, book_cls, journal, tick=1):
        """Jurnalni yangi, bo'sh birjada qayta o'ynaydi (zaxira server yoki tiklash)."""
        ex = cls(book_cls, tick)
        for _, cmd in journal:
            ex.handle(cmd)
        return ex
