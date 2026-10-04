"""Kalit maydoni — 2-daraja topshirig'ining 3-qismi. Oltita joy TODO.

Darsdan: 3-bo'lim (ekspirasiya va siqib chiqarish). Xotira bu yerda
kalitlar soni bilan o'lchanadi: maxkeys — "maxmemory".

Qoidalar:
  * Tasodifiy tanlash O(1) bo'lishi kerak (Redis dictGetRandomKey kabi).
    Shuning uchun kalitlar lug'atdan tashqari MASSIVDA ham saqlanadi:
    self.keys + self.pos (kalit -> indeks); TTL lilar uchun alohida
    self.vkeys + self.vpos. O'chirish — "oxirgisi bilan almashtirib, pop".
  * get(k, now): yo'q — None. Muddati tugagan (expires <= now) — o'chiring
    (passiv ekspirasiya, self.expired += 1) va None. Aks holda access[k] = now.
  * set(k, v, now, ttl=None): yangi kalit va len >= maxkeys bo'lsa —
    _evict_one() (kerak bo'lsa bir necha marta). ttl berilsa expires = now + ttl,
    berilmasa eski TTL olib tashlanadi (Redis SET kabi). access[k] = now.
  * _evict_one(): siyosat bo'yicha bitta kalitni o'chiradi, self.evicted += 1.
      noeviction        -> OOMError
      allkeys-*         -> hamma kalitlar orasidan
      volatile-*        -> faqat TTL lilar orasidan (bo'sh bo'lsa OOMError)
      *-random          -> bitta tasodifiy kalit
      *-lru             -> `samples` ta tasodifiy kalit, eng ESKI access'li
  * active_expire_cycle(now): Redis'ning faol sikli. Takrorlang:
      TTL lilardan min(20, soni) tasini tasodifiy tekshiring, muddati
      tugaganlarini o'chiring; o'chirilganlar 20 talikning 25% idan KO'P
      bo'lsa — yana, aks holda to'xtang. Bitta siklda jami tekshiruvlar
      cycle_budget dan oshmasin (CPU budjeti). Tekshirilganlar sonini qaytaring.

Tasodifiylik uchun faqat self.rng dan foydalaning.

Tekshiruv: python check.py
"""
import random

SAMPLE = 20
ACCEPTABLE_STALE = 0.25


class OOMError(Exception):
    pass


class Keyspace:
    def __init__(self, maxkeys, policy="allkeys-lru", samples=5, seed=0, cycle_budget=400):
        self.maxkeys = maxkeys
        self.policy = policy
        self.samples = samples
        self.rng = random.Random(seed)
        self.cycle_budget = cycle_budget
        self.data = {}            # kalit -> qiymat
        self.access = {}          # kalit -> oxirgi murojaat vaqti (LRU uchun)
        self.keys = []            # hamma kalitlar massivi (tasodifiy tanlash uchun)
        self.pos = {}             # kalit -> self.keys dagi indeks
        self.expires = {}         # kalit -> muddat (faqat TTL lilar)
        self.vkeys = []           # TTL li kalitlar massivi
        self.vpos = {}
        self.evicted = 0
        self.expired = 0

    @staticmethod
    def _arr_add(arr, pos, k):
        # TODO: O(1)
        raise NotImplementedError("Keyspace._arr_add")

    @staticmethod
    def _arr_del(arr, pos, k):
        # TODO: O(1) — oxirgi element bilan almashtirib, pop
        raise NotImplementedError("Keyspace._arr_del")

    def __len__(self):
        return len(self.data)

    def _delete(self, k):
        del self.data[k]
        del self.access[k]
        self._arr_del(self.keys, self.pos, k)
        if k in self.expires:
            del self.expires[k]
            self._arr_del(self.vkeys, self.vpos, k)

    def ttl(self, k, now):
        """Redis TTL: -2 — kalit yo'q, -1 — TTL yo'q, aks holda qolgan soniya."""
        if self.get(k, now) is None:
            return -2
        e = self.expires.get(k)
        return -1 if e is None else e - now

    def get(self, k, now):
        # TODO
        raise NotImplementedError("Keyspace.get")

    def set(self, k, v, now, ttl=None):
        # TODO
        raise NotImplementedError("Keyspace.set")

    def _evict_one(self):
        # TODO
        raise NotImplementedError("Keyspace._evict_one")

    def active_expire_cycle(self, now):
        # TODO
        raise NotImplementedError("Keyspace.active_expire_cycle")
