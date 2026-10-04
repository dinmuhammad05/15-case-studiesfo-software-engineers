"""Gibrid fan-out tasma xizmati — 2-daraja topshirig'ining 2-qismi. To'rtta joy TODO.

Darsdan: 5-bo'lim (push, pull, gibrid), 6-bo'lim 1-5-qadamlar, 7-bo'lim.
Vaqt — mantiqiy: post ID lari va obuna paytlari bitta o'suvchi hisoblagichdan.

Qoidalar (check.py har o'qishni "JOIN" bilan ishlaydigan sodda model bilan
AYNAN solishtiradi):

  post(a, pid) -> shu post uchun push yozuvlari soni
    * Muallifning o'z tasmasiga DOIM yoziladi (o'z postini darhol ko'rsin).
    * Obunachilari soni >= threshold bo'lsa — "mashhur": obunachilarga
      tarqatilmaydi, pid self.unpushed[a] ro'yxatiga qo'shiladi (pull).
    * Aks holda har obunachining tasmasiga yoziladi (push).
    * Har tasmaga yozish — self.stats["push_writes"] += 1. Tasma — self.cap
      dan uzun bo'lmasin (eng eskisi chiqadi). Tasmalarni o'sish tartibida
      saqlang (eskidan yangiga).

  read(u, limit=50, cursor=None) -> (pid lar ro'yxati, keyingi_kursor)
    * Nomzodlar: u ning tasmasi (push) + u obuna bo'lgan har bir akkauntning
      unpushed ro'yxati (pull; har bo'sh bo'lmagan ro'yxat uchun
      self.stats["pull_fetches"] += 1).
    * cursor berilsa — faqat pid < cursor.
    * Yangidan eskiga, takrorsiz, faqat KO'RINADIGANLAR (_visible), ko'pi
      bilan limit ta. Hammasini yig'ib saralamang: har ro'yxat allaqachon
      tartiblangan — uyum (heapq) bilan k ta ro'yxatni birlashtiring
      (k-way merge) va limit ga yetganda to'xtang.
    * keyingi_kursor — natija limit ga to'lsa oxirgi pid, aks holda None.

  _visible(u, pid):
    * o'chirilgan (self.deleted) — yo'q
    * muallif u ning o'zi — ha
    * u muallifga hozir obuna EMAS — yo'q; obuna paytidan oldingi post
      (pid <= since) — yo'q; muallif bloklangan — yo'q.

Tekshiruv: python check.py
"""
import bisect  # noqa: F401
import heapq  # noqa: F401
from collections import deque  # noqa: F401


class TimelineService:
    def __init__(self, threshold, cap=800):
        self.threshold = threshold
        self.cap = cap
        self.following = {}        # u -> {a: since}
        self.followers = {}        # a -> set(u)
        self.blocked = {}          # u -> set(a)
        self.timelines = {}        # u -> pid lar (eskidan yangiga), uzunligi <= cap
        self.unpushed = {}         # a -> [pid] — tarqatilmagan (mashhur) postlar, o'suvchi
        self.author = {}           # pid -> muallif
        self.deleted = set()       # tombstone'lar
        self.stats = {"push_writes": 0, "pull_fetches": 0}

    def follow(self, u, a, since):
        if u == a:
            return
        self.following.setdefault(u, {})[a] = since
        self.followers.setdefault(a, set()).add(u)

    def unfollow(self, u, a):
        self.following.get(u, {}).pop(a, None)
        self.followers.get(a, set()).discard(u)

    def block(self, u, a):
        self.blocked.setdefault(u, set()).add(a)

    def delete(self, pid):
        self.deleted.add(pid)      # tasmalarga tegilmaydi — o'qishda filtrlanadi

    def _push(self, u, pid):
        # TODO: u ning tasmasiga pid; cap; stats
        raise NotImplementedError("TimelineService._push")

    def post(self, a, pid):
        # TODO
        raise NotImplementedError("TimelineService.post")

    def _visible(self, u, pid):
        # TODO
        raise NotImplementedError("TimelineService._visible")

    def read(self, u, limit=50, cursor=None):
        # TODO
        raise NotImplementedError("TimelineService.read")
