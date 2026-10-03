"""AppView: firehose'dan indeks — 2-daraja topshirig'ining 2-qismi. Oltita joy TODO.

Darsdan: 5-bo'lim 6-9-qadamlar, 6-bo'lim. AppView butun tarmoq firehose'ini
o'qiydi va savollarga javob beradi: "bu postga nechta like?", "kim nechta
obunachiga ega?", "men uchun 'Following' tasmasi".

Qoidalar (check.py aynan shularni tekshiradi):
  * seq <= self.cursor — takror yoki eski hodisa: e'tiborsiz.
  * Commit imzosi foydalanuvchining joriy kaliti bilan tekshiriladi
    (self.resolve(did); kalit keshlanadi, Identity hodisasida kesh tozalanadi).
    Imzo noto'g'ri — commit jim tashlanadi.
  * Har repo uchun oxirgi qo'llangan rev. ev.prev == oxirgi rev (birinchi
    commitda ikkalasi None) — qo'llash. ev.rev <= oxirgi rev — eski, tashlash.
    Aks holda — bo'shliq: self.request_resync(did) (bir marta), shu did ning
    keyingi commitlari buferga, on_resync kelganda — surat + buferdagi
    yangilari.
  * Like va follow — "kim" bo'yicha: bitta odamning ikki like yozuvi bitta
    postga — bitta like. Delete amalida yozuv yuborilmaydi — eski yozuvni
    o'zingiz eslab qolishingiz kerak.
  * Hisob active=False — uning yozuvlari (like, follow, post) indeksdan
    chiqadi (lekin saqlanib turadi); active=True — qaytadi.
  * Tasma: tomosha qiluvchi va u follow qilganlarning (faol) postlari,
    (createdAt, uri) bo'yicha kamayish tartibida, limit ta. 100 000 postda
    ham tez bo'lsin: hammasini yig'ib saralamang.

Tekshiruv: python check.py
"""
import heapq  # noqa: F401
from bisect import bisect_left, insort  # noqa: F401
from collections import Counter  # noqa: F401
from itertools import islice  # noqa: F401

from model import (FOLLOW, LIKE, POST, Account, Commit, Identity, at_uri,  # noqa: F401
                   commit_bytes, verify)


class AppView:
    def __init__(self, resolve, request_resync):
        self.resolve = resolve                  # did -> joriy ochiq kalit
        self.request_resync = request_resync    # did -> None; keyin on_resync(RepoSnapshot) keladi
        self.keys = {}          # did -> keshlangan kalit
        self.cursor = 0         # oxirgi ko'rilgan seq
        self.rev = {}           # did -> oxirgi qo'llangan rev
        self.active = {}        # did -> bool (yo'q bo'lsa — faol)
        self.records = {}       # did -> {path: record}
        self.waiting = set()    # resinxronizatsiya kutilayotgan did lar
        self.buffer = {}        # did -> [Commit]
        self.likes = {}         # uri -> Counter(like qilgan did -> yozuvlar soni)
        self.followers = {}     # did -> Counter(obunachi -> yozuvlar soni)
        self.following = {}     # did -> Counter(kimga obuna -> yozuvlar soni)
        self.posts = {}         # did -> [(createdAt, uri)] o'sish tartibida

    # ------------------------------------------------------------ o'qish (tayyor)
    def like_count(self, uri):
        return len(self.likes.get(uri, ()))

    def follower_count(self, did):
        return len(self.followers.get(did, ()))

    def is_active(self, did):
        return self.active.get(did, True)

    # ------------------------------------------------------------ indeks
    def _index(self, did, path, rec, d):
        """Bitta yozuvni indeksga qo'shadi (d=+1) yoki olib tashlaydi (d=-1):
        LIKE -> likes[subject]; FOLLOW -> followers[subject] va following[did];
        POST -> posts[did] ((createdAt, uri), tartiblangan)."""
        raise NotImplementedError("TODO: _index")

    def _put(self, did, path, rec):
        """Yozuvni o'rnatadi (rec=None — o'chiradi): eskisini indeksdan chiqarib,
        yangisini qo'shadi (faqat hisob faol bo'lsa)."""
        raise NotImplementedError("TODO: _put")

    def _valid(self, ev):
        """Commit imzosi joriy (keshlangan) kalit bilan to'g'rimi."""
        raise NotImplementedError("TODO: _valid")

    # ------------------------------------------------------------ hodisalar
    def on_event(self, ev):
        """Firehose'dan bitta hodisa: Commit, Identity yoki Account."""
        raise NotImplementedError("TODO: on_event")

    def on_resync(self, snap):
        """So'ralgan RepoSnapshot keldi (kutilmagan bo'lsa — e'tiborsiz)."""
        raise NotImplementedError("TODO: on_resync")

    def timeline(self, viewer, limit=50):
        """'Following' tasmasi: uri lar ro'yxati, eng yangisidan."""
        raise NotImplementedError("TODO: timeline")
